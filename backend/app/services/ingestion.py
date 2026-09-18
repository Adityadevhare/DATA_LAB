from pathlib import Path

import polars as pl


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".json"}


class IngestionError(Exception):
    """Raised when a dataset cannot be ingested."""


def ingest_dataset(file_path: Path) -> pl.DataFrame:
    """
    Read a supported tabular dataset into a Polars DataFrame.

    Supported formats:
        - CSV
        - XLSX
        - tabular JSON
    """
    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise IngestionError(
            f"Unsupported file format: {extension or 'unknown'}"
        )

    try:
        if extension == ".csv":
            return pl.read_csv(file_path)

        if extension == ".xlsx":
            return pl.read_excel(file_path)

        if extension == ".json":
            return pl.read_json(file_path)

    except Exception as exc:
        raise IngestionError(
            f"Failed to read dataset: {exc}"
        ) from exc

    raise IngestionError("Unable to ingest dataset.")