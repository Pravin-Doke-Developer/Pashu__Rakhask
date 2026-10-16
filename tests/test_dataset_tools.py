"""
Test Suite for Dataset Validation & Splitting Tools
===================================================
Generates small synthetic test images (including valid, corrupt, and duplicates),
runs validate_dataset and split_dataset, and asserts expected behavior.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from PIL import Image

# Import functions from validate_dataset and split_dataset
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ml" / "common"))

from validate_dataset import discover_classes, validate_images, compute_class_imbalance, find_near_duplicates
from split_dataset import stratified_split, copy_splits, collect_images


class TestDatasetTools(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for mock dataset
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_dataset_"))
        
        # Create class directories
        self.class_a = self.test_dir / "healthy"
        self.class_b = self.test_dir / "lumpy_skin"
        self.class_a.mkdir()
        self.class_b.mkdir()

        # Generate sample valid images in Class A (healthy)
        for i in range(10):
            img = Image.new("RGB", (100 + i * 10, 100 + i * 10), color=(10 * i, 20 * i, 30 * i))
            img.save(self.class_a / f"healthy_{i}.jpg")

        # Generate sample valid images in Class B (lumpy_skin)
        for i in range(10):
            img = Image.new("RGB", (150, 150), color=(200, 50, 50 + i * 10))
            img.save(self.class_b / f"lumpy_{i}.png")

        # Create a corrupt file in Class B
        with open(self.class_b / "corrupt_image.jpg", "wb") as f:
            f.write(b"NOT_A_VALID_IMAGE_DATA_123456789")

        # Create an exact duplicate in Class A
        shutil.copy2(self.class_a / "healthy_0.jpg", self.class_a / "healthy_duplicate.jpg")

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_discover_classes(self):
        classes = discover_classes(self.test_dir)
        self.assertEqual(sorted(classes), ["healthy", "lumpy_skin"])

    def test_validate_images(self):
        res_a = validate_images(self.class_a)
        # 10 original + 1 duplicate = 11 valid images
        self.assertEqual(len(res_a["valid_images"]), 11)
        self.assertEqual(len(res_a["corrupt_images"]), 0)

        res_b = validate_images(self.class_b)
        # 10 valid images, 1 corrupt
        self.assertEqual(len(res_b["valid_images"]), 10)
        self.assertEqual(len(res_b["corrupt_images"]), 1)
        self.assertTrue("corrupt_image.jpg" in res_b["corrupt_images"][0]["path"])

    def test_near_duplicates_detection(self):
        res_a = validate_images(self.class_a)
        images = {"healthy": res_a["valid_images"]}
        dups = find_near_duplicates(images, threshold=5)
        self.assertGreaterEqual(dups["exact_duplicate_groups"], 1)

    def test_stratified_split(self):
        images = collect_images(self.test_dir)
        # Notice collect_images collects existing files
        splits = stratified_split(images, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, seed=42)
        
        self.assertIn("train", splits)
        self.assertIn("val", splits)
        self.assertIn("test", splits)

        # Total counts should be conserved
        for cls in ["healthy", "lumpy_skin"]:
            original_count = len(images[cls])
            split_count = len(splits["train"][cls]) + len(splits["val"][cls]) + len(splits["test"][cls])
            self.assertEqual(original_count, split_count)

        # Output copy test
        out_split_dir = self.test_dir / "split_output"
        manifest = copy_splits(splits, out_split_dir)
        self.assertTrue((out_split_dir / "train" / "healthy").exists())
        self.assertTrue((out_split_dir / "val" / "lumpy_skin").exists())
        self.assertTrue((out_split_dir / "test" / "healthy").exists())


if __name__ == "__main__":
    unittest.main()
