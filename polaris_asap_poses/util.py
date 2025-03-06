import numpy as np
import polars as pl
import polars.selectors as cs

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


def add_fake_id_col(
    df: pl.DataFrame, fake_id_col_name: str = "fake_id"
) -> pl.DataFrame:
    """
    Add a fake ID column as the first column in the DF
    TODO:  Let this be either zero- or one-indexed
    """
    fake_ids = np.arange(0, len(df), dtype=np.int64)
    df = df.with_columns(pl.lit(fake_ids).alias(fake_id_col_name)).select(
        cs.by_name(fake_id_col_name), ~cs.by_name(fake_id_col_name)
    )
    return df
