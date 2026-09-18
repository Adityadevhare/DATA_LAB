from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.dataset_service import (
    DatasetServiceError,
    create_dataset_session,
)


router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".json"}


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a CSV, XLSX, or tabular JSON dataset.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file format: {extension or 'unknown'}. "
                "Supported formats: CSV, XLSX, JSON."
            ),
        )

    temporary_path = None

    try:
        # Save the incoming upload temporarily.
        with NamedTemporaryFile(
            suffix=extension,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

            while chunk := await file.read(1024 * 1024):
                temporary_file.write(chunk)

        # Create the dataset session and process the file.
        result = create_dataset_session(
            source_file=temporary_path,
            original_filename=file.filename,
        )

        return {
            "status": "ready",
            **result,
        }

    except DatasetServiceError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()

        await file.close()