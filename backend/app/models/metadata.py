import polars as pl


def get_dataset_metadata(df: pl.DataFrame) -> dict:
    """
    Extract basic metadata from a Polars DataFrame.
    """

    columns = []

    for column_name, data_type in df.schema.items():
        columns.append(
            {
                "name": column_name,
                "data_type": str(data_type),
                "missing_count": df[column_name].null_count(),
                "unique_count": df[column_name].n_unique(),
            }
        )

    return {
        "row_count": df.height,
        "column_count": df.width,
        "columns": columns,
    }