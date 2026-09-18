import shutil
from pathlib import Path

from app.models.metadata import get_dataset_metadata
from app.services.ingestion import ingest_dataset
from app.utils.storage import create_dataset_storage


class DatasetServiceError(Exception):
    """Raised when dataset session creation fails."""


def create_dataset_session(
    source_file: Path,
    original_filename: str,
) -> dict:
    """
    Create a dataset session from an uploaded file.

    The original file is preserved and a separate working copy
    is created for future data-cleaning operations.
    """

    if not source_file.exists():
        raise DatasetServiceError("Source file does not exist.")

    try:
        dataset_id, original_dir, working_dir = create_dataset_storage()

        # Preserve the uploaded file exactly as received.
        original_path = original_dir / original_filename
        shutil.copy2(source_file, original_path)

        # Read the original dataset.
        df = ingest_dataset(original_path)

        # Create the editable working copy.
        working_path = working_dir / original_filename
        shutil.copy2(original_path, working_path)

        metadata = get_dataset_metadata(df)

        return {
            "dataset_id": dataset_id,
            "filename": original_filename,
            "original_path": str(original_path),
            "working_path": str(working_path),
            "metadata": metadata,
        }

    except Exception as exc:
        raise DatasetServiceError(
            f"Failed to create dataset session: {exc}"
        ) from exc