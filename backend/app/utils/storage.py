from pathlib import Path
from uuid import uuid4


BASE_STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage" / "sessions"


def create_dataset_storage() -> tuple[str, Path, Path]:
    """
    Create a unique storage directory for a dataset session.

    Returns:
        dataset_id: Unique identifier for the dataset.
        original_dir: Directory containing the untouched uploaded file.
        working_dir: Directory containing the editable working copy.
    """
    dataset_id = str(uuid4())

    dataset_dir = BASE_STORAGE_DIR / dataset_id
    original_dir = dataset_dir / "original"
    working_dir = dataset_dir / "working"

    original_dir.mkdir(parents=True, exist_ok=False)
    working_dir.mkdir(parents=True, exist_ok=False)

    return dataset_id, original_dir, working_dir