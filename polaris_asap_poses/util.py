import polars as pl

from polaris_asap_poses.logger import logger


def print_info(df: pl.DataFrame, show_columns: bool = True, show_unique: bool = False):
    """
    Print diagnostic info about this dataframe.
    """
    if show_columns:
        # columns = df.columns
        columns = []
        for i, j in zip(df.columns, df.dtypes):
            columns.append(f"{i}: {j}")
    else:
        columns = "<you asked not to see these>"
    logger.info(
        f"Shape: {df.shape}, size: {df.estimated_size(unit='gb')} GB ({df.estimated_size(unit='mb')} MB), columns: {columns}."
    )
    if show_unique:
        print(f"Unique:  {df.approx_n_unique()}")
