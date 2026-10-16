"""Train the disease or cattle-breed image classifier in Google Colab.

In a Colab cell, mount Drive and run:

    !python /content/drive/MyDrive/animal-health-ai/notebooks/train_models_colab.py \
        --task disease \
        --project-root /content/drive/MyDrive/animal-health-ai

Change --task to "breed" to train the breed model. The script reads the
existing disease split, prefers datasets/breed_split when available, and
otherwise creates a reproducible split from datasets/breed/Cattle Breeds.
"""

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
IMAGE_SIZE = (224, 224)
SEED = 42


def image_files(folder: Path) -> list[Path]:
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def classes_in(folder: Path) -> list[str]:
    if not folder.is_dir():
        raise FileNotFoundError(f"Dataset folder does not exist: {folder}")
    return sorted(
        child.name
        for child in folder.iterdir()
        if child.is_dir() and image_files(child)
    )


def records_from_split(root: Path, split: str, class_names: list[str]) -> list[tuple[Path, int]]:
    split_root = root / split
    found_classes = classes_in(split_root)
    if found_classes != class_names:
        raise ValueError(
            f"{split_root} classes {found_classes} do not match expected classes {class_names}"
        )

    records = [
        (path, label)
        for label, class_name in enumerate(class_names)
        for path in image_files(split_root / class_name)
    ]
    if not records:
        raise ValueError(f"No supported images found in {split_root}")
    return records


def create_grouped_breed_split(
    root: Path, class_names: list[str]
) -> tuple[list[tuple[Path, int]], list[tuple[Path, int]], list[tuple[Path, int]]]:
    """Split raw breed images per class, keeping matching *_c files together."""
    partitions: dict[str, list[tuple[Path, int]]] = {
        "train": [],
        "val": [],
        "test": [],
    }

    for label, class_name in enumerate(class_names):
        groups: dict[str, list[Path]] = defaultdict(list)
        for path in image_files(root / class_name):
            group_name = path.stem.lower()
            if group_name.endswith("_c"):
                group_name = group_name[:-2]
            groups[group_name].append(path)

        group_names = sorted(groups)
        if len(group_names) < 4:
            raise ValueError(
                f"Class '{class_name}' needs at least 4 distinct image groups "
                "to make train/validation/test splits."
            )

        train_groups, remaining_groups = train_test_split(
            group_names, test_size=0.30, random_state=SEED
        )
        val_groups, test_groups = train_test_split(
            remaining_groups, test_size=0.50, random_state=SEED
        )
        for split, selected_groups in (
            ("train", train_groups),
            ("val", val_groups),
            ("test", test_groups),
        ):
            partitions[split].extend(
                (path, label)
                for group_name in selected_groups
                for path in groups[group_name]
            )

    return partitions["train"], partitions["val"], partitions["test"]


def make_dataset(
    records: list[tuple[Path, int]], batch_size: int, shuffle: bool
) -> tf.data.Dataset:
    paths = [str(path) for path, _ in records]
    labels = [label for _, label in records]
    dataset = tf.data.Dataset.from_tensor_slices((paths, labels))
    if shuffle:
        dataset = dataset.shuffle(
            buffer_size=len(records), seed=SEED, reshuffle_each_iteration=True
        )

    def decode_image(path: tf.Tensor, label: tf.Tensor) -> tuple[tf.Tensor, tf.Tensor]:
        contents = tf.io.read_file(path)
        image = tf.io.decode_image(contents, channels=3, expand_animations=False)
        image.set_shape([None, None, 3])
        image = tf.image.resize(image, IMAGE_SIZE)
        image = tf.cast(image, tf.float32) / 255.0
        return image, label

    return (
        dataset.map(decode_image, num_parallel_calls=tf.data.AUTOTUNE)
        .batch(batch_size)
        .prefetch(tf.data.AUTOTUNE)
    )


def class_weights(records: list[tuple[Path, int]], number_of_classes: int) -> dict[int, float]:
    counts = Counter(label for _, label in records)
    missing = [label for label in range(number_of_classes) if counts[label] == 0]
    if missing:
        raise ValueError(f"Training split is missing class indices: {missing}")
    total = sum(counts.values())
    return {
        label: total / (number_of_classes * counts[label])
        for label in range(number_of_classes)
    }


def make_model(number_of_classes: int) -> tuple[keras.Model, keras.Model]:
    augmentation = keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.04),
            layers.RandomZoom(0.08),
        ],
        name="augmentation",
    )
    backbone = keras.applications.MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    backbone.trainable = False

    inputs = keras.Input(shape=(*IMAGE_SIZE, 3), name="image")
    x = augmentation(inputs)
    # The backend sends RGB images scaled to [0, 1]; MobileNetV2 expects [-1, 1].
    x = layers.Rescaling(2.0, offset=-1.0, name="mobilenet_normalization")(x)
    x = backbone(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.25)(x)
    outputs = layers.Dense(number_of_classes, activation="softmax", name="predictions")(x)
    return keras.Model(inputs, outputs), backbone


def fit_model(
    model: keras.Model,
    backbone: keras.Model,
    train_ds: tf.data.Dataset,
    val_ds: tf.data.Dataset,
    weights: dict[int, float],
    work_dir: Path,
    head_epochs: int,
    fine_tune_epochs: int,
) -> keras.Model:
    work_dir.mkdir(parents=True, exist_ok=True)
    checkpoints: list[tuple[float, Path]] = []

    def train_stage(stage: str, epochs: int) -> None:
        if epochs < 1:
            return
        checkpoint = work_dir / f"{stage}.keras"
        callbacks = [
            keras.callbacks.ModelCheckpoint(
                checkpoint,
                monitor="val_loss",
                save_best_only=True,
                verbose=1,
            ),
            keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=4,
                restore_best_weights=True,
                verbose=1,
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.2,
                patience=2,
                min_lr=1e-7,
                verbose=1,
            ),
        ]
        history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=epochs,
            class_weight=weights,
            callbacks=callbacks,
        )
        checkpoints.append((min(history.history["val_loss"]), checkpoint))

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    train_stage("head", head_epochs)

    if fine_tune_epochs > 0:
        backbone.trainable = True
        for layer in backbone.layers[:-30]:
            layer.trainable = False
        for layer in backbone.layers:
            if isinstance(layer, layers.BatchNormalization):
                layer.trainable = False

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=1e-5),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        train_stage("fine_tune", fine_tune_epochs)

    if not checkpoints:
        raise ValueError("Set at least one of --head-epochs or --fine-tune-epochs above zero.")
    best_checkpoint = min(checkpoints, key=lambda item: item[0])[1]
    print(f"Using best validation checkpoint: {best_checkpoint}")
    return keras.models.load_model(best_checkpoint, compile=False)


def evaluate_model(
    model: keras.Model,
    test_ds: tf.data.Dataset,
    test_records: list[tuple[Path, int]],
    class_names: list[str],
) -> dict:
    test_loss, test_accuracy = model.evaluate(test_ds, verbose=1)
    probabilities = model.predict(test_ds, verbose=1)
    predicted = np.argmax(probabilities, axis=1)
    actual = np.array([label for _, label in test_records])
    report = classification_report(
        actual,
        predicted,
        labels=list(range(len(class_names))),
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )
    return {
        "test_loss": float(test_loss),
        "test_accuracy": float(test_accuracy),
        "classification_report": report,
        "confusion_matrix": confusion_matrix(
            actual, predicted, labels=list(range(len(class_names)))
        ).tolist(),
    }


def train(args: argparse.Namespace) -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    tf.random.set_seed(SEED)

    project_root = args.project_root.resolve()
    if args.task == "disease":
        data_root = project_root / "datasets" / "disease_split"
        class_names = classes_in(data_root / "train")
        expected = ["foot-and-mouth", "healthy", "lumpy"]
        if class_names != expected:
            raise ValueError(f"Expected disease classes {expected}; found {class_names}")
        train_records = records_from_split(data_root, "train", class_names)
        val_records = records_from_split(data_root, "val", class_names)
        test_records = records_from_split(data_root, "test", class_names)
    else:
        split_root = project_root / "datasets" / "breed_split"
        if split_root.exists():
            if not all((split_root / split).is_dir() for split in ("train", "val", "test")):
                raise ValueError(
                    f"{split_root} exists but must contain train/, val/, and test/ folders."
                )
            class_names = classes_in(split_root / "train")
            train_records = records_from_split(split_root, "train", class_names)
            val_records = records_from_split(split_root, "val", class_names)
            test_records = records_from_split(split_root, "test", class_names)
            data_root = split_root
            print(f"Using existing breed split at {split_root}")
        else:
            data_root = project_root / "datasets" / "breed" / "Cattle Breeds"
            class_names = classes_in(data_root)
            if len(class_names) < 2:
                raise ValueError(f"Expected breed class folders under {data_root}")
            train_records, val_records, test_records = create_grouped_breed_split(
                data_root, class_names
            )
            print(
                "No datasets/breed_split folder found; created a deterministic "
                "70/15/15 split from the raw breed folders."
            )

    print(f"TensorFlow: {tf.__version__}")
    print(f"GPU devices: {tf.config.list_physical_devices('GPU')}")
    print(f"Data source: {data_root}")
    print(f"Classes (model output order): {class_names}")
    print(
        "Image counts:",
        {
            "train": len(train_records),
            "val": len(val_records),
            "test": len(test_records),
        },
    )
    for split_name, records in (
        ("train", train_records),
        ("val", val_records),
        ("test", test_records),
    ):
        split_counts = Counter(class_names[label] for _, label in records)
        print(
            f"{split_name} by class:",
            {class_name: split_counts[class_name] for class_name in class_names},
        )

    train_ds = make_dataset(train_records, args.batch_size, shuffle=True)
    val_ds = make_dataset(val_records, args.batch_size, shuffle=False)
    test_ds = make_dataset(test_records, args.batch_size, shuffle=False)
    weights = class_weights(train_records, len(class_names))
    print(f"Class weights: {weights}")

    model, backbone = make_model(len(class_names))
    work_dir = Path("/content") / f"animal_health_{args.task}_training"
    best_model = fit_model(
        model,
        backbone,
        train_ds,
        val_ds,
        weights,
        work_dir,
        args.head_epochs,
        args.fine_tune_epochs,
    )
    metrics = evaluate_model(best_model, test_ds, test_records, class_names)

    artifact_dir = project_root / "artifacts" / f"{args.task}_model"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    model_name = f"{args.task}_model.keras"
    best_model.save(artifact_dir / model_name)
    (artifact_dir / "class_mapping.json").write_text(
        json.dumps({"classes": class_names}, indent=2), encoding="utf-8"
    )
    backend_mapping = project_root / "ml" / args.task / "class_mapping.json"
    backend_mapping.parent.mkdir(parents=True, exist_ok=True)
    backend_mapping.write_text(
        json.dumps({"classes": class_names}, indent=2), encoding="utf-8"
    )
    (artifact_dir / "training_config.json").write_text(
        json.dumps(
            {
                "task": args.task,
                "architecture": "MobileNetV2",
                "image_size": list(IMAGE_SIZE),
                "input_range": [0.0, 1.0],
                "seed": SEED,
                "batch_size": args.batch_size,
                "head_epochs": args.head_epochs,
                "fine_tune_epochs": args.fine_tune_epochs,
                "data_root": str(data_root),
                "class_order": class_names,
                "split_counts": {
                    "train": len(train_records),
                    "val": len(val_records),
                    "test": len(test_records),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (artifact_dir / "evaluation_report.json").write_text(
        json.dumps(metrics, indent=2, allow_nan=False), encoding="utf-8"
    )

    print(f"\nSaved model and reports to: {artifact_dir}")
    print(f"Model: {artifact_dir / model_name}")
    print(f"Class mapping: {artifact_dir / 'class_mapping.json'}")
    print(f"Test accuracy: {metrics['test_accuracy']:.4f}")
    print(f"Macro F1: {metrics['classification_report']['macro avg']['f1-score']:.4f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=("disease", "breed"), required=True)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("/content/drive/MyDrive/animal-health-ai"),
        help="Project folder in Google Drive containing datasets/ and artifacts/.",
    )
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--head-epochs", type=int, default=12)
    parser.add_argument("--fine-tune-epochs", type=int, default=8)
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")
    if args.head_epochs < 0 or args.fine_tune_epochs < 0:
        parser.error("Epoch counts must not be negative")
    return args


if __name__ == "__main__":
    train(parse_args())
