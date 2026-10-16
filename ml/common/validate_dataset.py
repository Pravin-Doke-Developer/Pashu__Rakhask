"""
Dataset Validation Script
=========================
Inspects an image classification dataset organized in class-labeled folders.

What this script does:
1. Scans all images in each class folder.
2. Checks for corrupt / unreadable images (tries to open with Pillow).
3. Reports image dimensions, formats, and color modes.
4. Detects potential near-duplicate images using perceptual hashing (pHash).
5. Calculates class imbalance metrics.
6. Generates a visual class distribution chart.
7. Saves a JSON validation report.

Usage:
    python validate_dataset.py --dataset_dir ../../datasets/disease

Expected folder structure:
    dataset_dir/
    ├── ClassA/
    │   ├── img1.jpg
    │   └── img2.png
    ├── ClassB/
    │   └── img3.jpg
    └── ClassC/
        └── img4.jpg

Output:
    - Console summary
    - validation_report.json (in the dataset directory)
    - class_distribution.png (in the dataset directory)
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Third-party imports — installed via requirements.txt
try:
    from PIL import Image
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend (no GUI needed)
    import matplotlib.pyplot as plt
    import imagehash
    from tqdm import tqdm
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Common image extensions to look for
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

# Perceptual hash distance threshold for near-duplicate detection.
# Lower = stricter (exact duplicates). Higher = catches more variations.
# 10 is a reasonable default — it catches rotated/slightly edited copies
# but won't flag genuinely different images of the same animal.
HASH_DISTANCE_THRESHOLD = 10


def discover_classes(dataset_dir: Path) -> list[str]:
    """
    Find all class folders inside the dataset directory.
    A 'class folder' is any subdirectory that contains at least one image file.

    Returns a sorted list of class names (folder names).
    """
    dataset_dir = Path(dataset_dir)
    classes = []
    seen = set()

    def has_images(folder: Path) -> bool:
        return any(
            f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
            for f in folder.iterdir()
        )

    for entry in sorted(dataset_dir.iterdir()):
        if not entry.is_dir():
            continue

        if has_images(entry):
            classes.append(entry.name)
            seen.add(entry.resolve())
            continue

        # Some datasets nest a single extra directory layer before the class folders.
        for child in sorted(entry.iterdir()):
            if child.is_dir() and child.resolve() not in seen and has_images(child):
                classes.append(child.name)
                seen.add(child.resolve())

    return sorted(set(classes))


def validate_images(class_dir: Path) -> dict:
    """
    Validate every image in a single class folder.

    Returns a dict with:
        - valid_images: list of valid image paths
        - corrupt_images: list of corrupt/unreadable file paths
        - dimensions: list of (width, height) tuples
        - formats: Counter of image formats (JPEG, PNG, etc.)
        - modes: Counter of color modes (RGB, L, RGBA, etc.)
        - extensions: Counter of file extensions
        - file_sizes: list of file sizes in bytes
    """
    valid_images = []
    corrupt_images = []
    dimensions = []
    formats = Counter()
    modes = Counter()
    extensions = Counter()
    file_sizes = []

    image_files = [
        f for f in class_dir.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    for img_path in image_files:
        ext = img_path.suffix.lower()
        extensions[ext] += 1

        try:
            # Open the image and force a full decode.
            # Some corrupt files open successfully but fail when you
            # try to read the pixel data — .verify() catches this.
            with Image.open(img_path) as img:
                img.verify()  # Check for corruption

            # Re-open after verify (verify closes the file)
            with Image.open(img_path) as img:
                img.load()  # Force full pixel decode
                w, h = img.size
                dimensions.append((w, h))
                formats[img.format or "UNKNOWN"] += 1
                modes[img.mode] += 1
                file_sizes.append(img_path.stat().st_size)
                valid_images.append(str(img_path))

        except Exception as e:
            corrupt_images.append({
                "path": str(img_path),
                "error": str(e)
            })

    return {
        "valid_images": valid_images,
        "corrupt_images": corrupt_images,
        "dimensions": dimensions,
        "formats": dict(formats),
        "modes": dict(modes),
        "extensions": dict(extensions),
        "file_sizes": file_sizes,
    }


def compute_dimension_stats(dimensions: list[tuple[int, int]]) -> dict:
    """
    Compute statistics about image dimensions.

    Why this matters:
    - Neural networks need fixed-size inputs (e.g., 224×224).
    - If images vary wildly in size, some will be heavily distorted
      when resized, which can hurt model performance.
    - Very small images may lack detail for disease detection.
    """
    if not dimensions:
        return {}

    widths = [d[0] for d in dimensions]
    heights = [d[1] for d in dimensions]

    return {
        "width": {
            "min": int(min(widths)),
            "max": int(max(widths)),
            "mean": round(float(np.mean(widths)), 1),
            "median": int(np.median(widths)),
        },
        "height": {
            "min": int(min(heights)),
            "max": int(max(heights)),
            "mean": round(float(np.mean(heights)), 1),
            "median": int(np.median(heights)),
        },
        "total_unique_sizes": len(set(dimensions)),
    }


def find_near_duplicates(
    all_images: dict[str, list[str]],
    threshold: int = HASH_DISTANCE_THRESHOLD,
) -> dict:
    """
    Detect near-duplicate images using perceptual hashing (pHash).

    How perceptual hashing works (in simple terms):
    1. Shrink the image to a tiny size (e.g., 8×8).
    2. Convert to grayscale.
    3. Compute the Discrete Cosine Transform (DCT) — this captures
       the image's dominant visual structure, ignoring fine details.
    4. Generate a binary hash from the DCT coefficients.

    Two images with similar visual content will have similar hashes,
    even if they differ in resolution, brightness, or minor edits.

    The 'distance' between two hashes tells us how different they are:
    - Distance 0: Exact visual duplicate
    - Distance 1-5: Very similar (likely the same image with minor edits)
    - Distance 6-10: Similar (possibly the same scene/animal)
    - Distance 11+: Probably different images

    Why this matters for ML:
    - If the same image appears in both training and test sets, the model
      will appear to perform better than it actually does (data leakage).
    - Near-duplicates can inflate training set diversity artificially.

    Returns:
        - within_class: duplicates found within the same class
        - cross_class: duplicates found across different classes
          (these are especially suspicious — the same image with different labels!)
    """
    if not all_images or not any(paths for paths in all_images.values()):
        return {
            "exact_duplicate_groups": 0,
            "exact_duplicates": {},
            "near_duplicates_within_class": 0,
            "near_duplicates_cross_class": 0,
            "cross_class_examples": [],
            "within_class_examples": [],
        }

    print("\n🔍 Computing perceptual hashes for near-duplicate detection...")
    print("   (This may take a minute for large datasets)\n")

    # Compute hashes for all images
    image_hashes = {}  # path -> hash
    hash_to_paths = defaultdict(list)  # hash_str -> [(path, class_name)]

    for class_name, paths in all_images.items():
        for img_path in tqdm(paths, desc=f"  Hashing {class_name}", unit="img"):
            try:
                with Image.open(img_path) as img:
                    h = imagehash.phash(img)
                    image_hashes[img_path] = h
                    hash_to_paths[str(h)].append((img_path, class_name))
            except Exception:
                pass  # Already caught in validation

    # Find exact hash matches (distance = 0)
    exact_duplicates = {
        h: entries for h, entries in hash_to_paths.items()
        if len(entries) > 1
    }

    # Find near-duplicates (distance > 0 but below threshold)
    # We use a simple O(n²) approach — fine for datasets under ~10,000 images.
    near_duplicates_within = []
    near_duplicates_cross = []

    hash_list = list(image_hashes.items())
    total_comparisons = len(hash_list) * (len(hash_list) - 1) // 2

    if total_comparisons > 5_000_000:
        print(f"  ⚠️ Skipping pairwise comparison ({total_comparisons:,} pairs would be too slow).")
        print("     Only reporting exact hash matches.\n")
    else:
        print(f"  Comparing {total_comparisons:,} image pairs...")
        checked = 0
        for i in range(len(hash_list)):
            path_a, hash_a = hash_list[i]
            class_a = None
            for cn, paths in all_images.items():
                if path_a in paths:
                    class_a = cn
                    break

            for j in range(i + 1, len(hash_list)):
                path_b, hash_b = hash_list[j]
                distance = hash_a - hash_b

                if 0 < distance <= threshold:
                    class_b = None
                    for cn, paths in all_images.items():
                        if path_b in paths:
                            class_b = cn
                            break

                    entry = {
                        "image_a": os.path.basename(path_a),
                        "image_b": os.path.basename(path_b),
                        "class_a": class_a,
                        "class_b": class_b,
                        "hash_distance": int(distance),
                    }

                    if class_a == class_b:
                        near_duplicates_within.append(entry)
                    else:
                        near_duplicates_cross.append(entry)

                checked += 1

    return {
        "exact_duplicate_groups": len(exact_duplicates),
        "exact_duplicates": {
            h: [{"path": os.path.basename(p), "class": c} for p, c in entries]
            for h, entries in list(exact_duplicates.items())[:20]  # Limit output
        },
        "near_duplicates_within_class": len(near_duplicates_within),
        "near_duplicates_cross_class": len(near_duplicates_cross),
        "cross_class_examples": near_duplicates_cross[:20],  # Most suspicious ones
        "within_class_examples": near_duplicates_within[:20],
    }


def compute_class_imbalance(class_counts: dict[str, int]) -> dict:
    """
    Compute class imbalance metrics.

    Why class imbalance matters:
    - If one class has 10x more images than another, the model might
      just always predict the majority class and still get high accuracy.
    - Example: 90% Healthy + 10% Diseased → always predicting "Healthy"
      gives 90% accuracy but is useless for disease detection.

    Metrics:
    - Imbalance ratio: largest_class / smallest_class
      (1.0 = perfectly balanced, higher = more imbalanced)
    - Each class's percentage of the total
    """
    if not class_counts:
        return {}

    total = sum(class_counts.values())
    max_count = max(class_counts.values())
    min_count = min(class_counts.values())

    per_class = {
        name: {
            "count": count,
            "percentage": round(100 * count / total, 1) if total > 0 else 0.0,
        }
        for name, count in sorted(class_counts.items())
    }

    return {
        "total_images": total,
        "num_classes": len(class_counts),
        "imbalance_ratio": round(max_count / min_count, 2) if min_count > 0 else 0.0,
        "per_class": per_class,
    }


def plot_class_distribution(class_counts: dict[str, int], output_path: Path):
    """
    Create a bar chart showing how many images are in each class.
    Saves the chart as a PNG file.
    """
    names = list(class_counts.keys())
    counts = list(class_counts.values())

    if not names:
        print(f"📊 No class data available to plot at: {output_path}")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(names, counts, color=["#2ecc71", "#e74c3c", "#3498db", "#f39c12", "#9b59b6"])

    # Add count labels on top of each bar
    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(counts) * 0.01,
            str(count),
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=12,
        )

    ax.set_title("Dataset Class Distribution", fontsize=16, fontweight="bold")
    ax.set_xlabel("Class", fontsize=13)
    ax.set_ylabel("Number of Images", fontsize=13)
    ax.tick_params(axis="x", rotation=15)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"📊 Class distribution chart saved to: {output_path}")


def main():
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(
        description="Validate an image classification dataset.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
    python validate_dataset.py --dataset_dir ../../datasets/disease

The dataset should be organized with one subfolder per class,
each containing the images for that class.
        """,
    )
    parser.add_argument(
        "--dataset_dir",
        type=str,
        required=True,
        help="Path to the dataset root directory (containing class folders).",
    )
    parser.add_argument(
        "--skip_duplicates",
        action="store_true",
        help="Skip near-duplicate detection (faster, but less thorough).",
    )

    args = parser.parse_args()
    dataset_dir = Path(args.dataset_dir).resolve()

    # --- Check the directory exists ---
    if not dataset_dir.exists():
        print(f"❌ Error: Directory not found: {dataset_dir}")
        print("\nMake sure you've downloaded and extracted the dataset.")
        print("See datasets/README.md for instructions.")
        sys.exit(1)

    if not dataset_dir.is_dir():
        print(f"❌ Error: Not a directory: {dataset_dir}")
        sys.exit(1)

    # --- Discover classes ---
    print(f"\n{'='*60}")
    print(f"  Dataset Validation Report")
    print(f"  Directory: {dataset_dir}")
    print(f"{'='*60}\n")

    classes = discover_classes(dataset_dir)

    if not classes:
        print("❌ No class folders found!")
        print(f"   Looked in: {dataset_dir}")
        print(f"   Expected: subdirectories containing image files")
        print(f"   Supported extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

        # Help debug: show what IS in the directory
        contents = list(dataset_dir.iterdir())
        if contents:
            print(f"\n   Directory contains:")
            for item in contents[:20]:
                item_type = "📁" if item.is_dir() else "📄"
                print(f"     {item_type} {item.name}")
            # Maybe there's an extra nesting level
            for item in contents:
                if item.is_dir():
                    sub_classes = discover_classes(item)
                    if sub_classes:
                        print(f"\n   💡 Tip: Classes found inside '{item.name}/'")
                        print(f"      Try: --dataset_dir {item}")
                        break
        sys.exit(1)

    print(f"📂 Found {len(classes)} classes: {', '.join(classes)}\n")

    # --- Validate each class ---
    all_results = {}
    class_counts = {}
    all_valid_images = {}  # class_name -> [paths]
    all_dimensions = []
    all_formats = Counter()
    all_modes = Counter()
    total_corrupt = 0

    for class_name in classes:
        class_dir = dataset_dir / class_name
        print(f"  Validating: {class_name}/")

        result = validate_images(class_dir)
        all_results[class_name] = result

        n_valid = len(result["valid_images"])
        n_corrupt = len(result["corrupt_images"])
        total_corrupt += n_corrupt
        class_counts[class_name] = n_valid
        all_valid_images[class_name] = result["valid_images"]
        all_dimensions.extend(result["dimensions"])
        all_formats.update(result["formats"])
        all_modes.update(result["modes"])

        status = "✅" if n_corrupt == 0 else "⚠️"
        print(f"    {status} {n_valid} valid, {n_corrupt} corrupt")

    # --- Compute statistics ---
    imbalance = compute_class_imbalance(class_counts)
    dim_stats = compute_dimension_stats(all_dimensions)

    # --- Near-duplicate detection ---
    duplicate_report = {}
    if not args.skip_duplicates:
        duplicate_report = find_near_duplicates(all_valid_images)

    # --- Print summary ---
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}\n")

    print(f"  Total images:  {imbalance.get('total_images', 0)}")
    print(f"  Total classes: {imbalance.get('num_classes', 0)}")
    print(f"  Corrupt files: {total_corrupt}")
    print(f"  Imbalance ratio: {imbalance.get('imbalance_ratio', 'N/A')}")
    print()

    print("  Class breakdown:")
    for name, info in imbalance.get("per_class", {}).items():
        bar_len = int(info["percentage"] / 2)  # Scale bar to ~50 chars max
        bar = "█" * bar_len
        print(f"    {name:30s} {info['count']:5d}  ({info['percentage']:5.1f}%)  {bar}")
    print()

    if dim_stats:
        print(f"  Image dimensions:")
        print(f"    Width:  {dim_stats['width']['min']}–{dim_stats['width']['max']} "
              f"(median: {dim_stats['width']['median']}, mean: {dim_stats['width']['mean']})")
        print(f"    Height: {dim_stats['height']['min']}–{dim_stats['height']['max']} "
              f"(median: {dim_stats['height']['median']}, mean: {dim_stats['height']['mean']})")
        print(f"    Unique sizes: {dim_stats['total_unique_sizes']}")
        print()

    print(f"  Image formats: {dict(all_formats)}")
    print(f"  Color modes:   {dict(all_modes)}")

    if duplicate_report:
        print(f"\n  Near-duplicate detection:")
        print(f"    Exact duplicate groups: {duplicate_report.get('exact_duplicate_groups', 0)}")
        print(f"    Near-duplicates (same class):  {duplicate_report.get('near_duplicates_within_class', 0)}")
        print(f"    Near-duplicates (cross class): {duplicate_report.get('near_duplicates_cross_class', 0)}")

        if duplicate_report.get("near_duplicates_cross_class", 0) > 0:
            print("\n    ⚠️ WARNING: Cross-class near-duplicates found!")
            print("    These are images that look similar but have different labels.")
            print("    This could indicate labeling errors or data quality issues.")
            for ex in duplicate_report.get("cross_class_examples", [])[:5]:
                print(f"      • {ex['image_a']} ({ex['class_a']}) ↔ "
                      f"{ex['image_b']} ({ex['class_b']}) [distance={ex['hash_distance']}]")

    # --- Save outputs ---
    # Build the full report
    report = {
        "dataset_dir": str(dataset_dir),
        "classes": classes,
        "class_counts": class_counts,
        "imbalance": imbalance,
        "dimension_stats": dim_stats,
        "formats": dict(all_formats),
        "color_modes": dict(all_modes),
        "corrupt_files": {
            "total": total_corrupt,
            "details": {
                name: result["corrupt_images"]
                for name, result in all_results.items()
                if result["corrupt_images"]
            },
        },
        "duplicates": duplicate_report,
    }

    report_path = dataset_dir / "validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n📋 Full report saved to: {report_path}")

    # Class distribution chart
    chart_path = dataset_dir / "class_distribution.png"
    plot_class_distribution(class_counts, chart_path)

    # --- Final assessment ---
    print(f"\n{'='*60}")
    issues = []
    if total_corrupt > 0:
        issues.append(f"  ⚠️ {total_corrupt} corrupt images found — remove before training.")
    if imbalance.get("imbalance_ratio", 1) > 3:
        issues.append(f"  ⚠️ Significant class imbalance (ratio {imbalance['imbalance_ratio']}) — "
                      f"consider class weights or oversampling.")
    if duplicate_report.get("near_duplicates_cross_class", 0) > 0:
        issues.append(f"  ⚠️ Cross-class duplicates found — review for labeling errors.")
    if duplicate_report.get("exact_duplicate_groups", 0) > 10:
        issues.append(f"  ⚠️ Many exact duplicates — consider deduplication.")

    if issues:
        print("  ISSUES TO ADDRESS:")
        for issue in issues:
            print(issue)
    else:
        print("  ✅ No critical issues found. Dataset looks ready for splitting.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
