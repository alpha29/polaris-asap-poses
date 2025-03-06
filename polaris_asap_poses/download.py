import zipfile
from pathlib import Path

import fsspec
import polaris as po
import polars as pl
from polaris.competition import CompetitionSpecification
from typeguard import typechecked

from polaris_asap_poses.io import (DATA_DIR_RAW_PACKAGES,
                                   DATA_DIR_RAW_REF_STRUCTURES)
from polaris_asap_poses.logger import logger
from polaris_asap_poses.util import add_fake_id_col, print_info

CHALLENGE = "antiviral-ligand-poses-2025"

####################################
# Polaris competition downloads
####################################


@typechecked
def load_comp(challenge: str = CHALLENGE) -> CompetitionSpecification:
    """
    Cache the competition dataset.

    Run `polaris login` before running this.
    """
    logger.info(f"Loading competition for challenge {challenge}...")
    competition = po.load_competition(f"asap-discovery/{challenge}")
    logger.info("Done. Caching...")
    # when you set this to "skip", polaris throws an exception I don't care to debug
    # cache_dir = competition.cache(if_exists="skip")
    cache_dir = competition.cache()
    logger.info(f"Cached data to {cache_dir}.")
    return competition


def download_raw_data_packages(
    raw_data_package_dir: str | Path = DATA_DIR_RAW_PACKAGES,
):
    logger.info(f"Downloading raw-data package to {raw_data_package_dir}")
    with fsspec.open(
        "https://fs.polarishub.io/2025-01-asap-discovery/raw_data_package.zip"
    ) as fd:
        with zipfile.ZipFile(fd, "a") as zip_ref:
            zip_ref.extractall(raw_data_package_dir)


def download_reference_structures(
    reference_structures_dir: str | Path = DATA_DIR_RAW_REF_STRUCTURES,
):
    logger.info(f"Downloading reference structures to {reference_structures_dir}")
    reference_structures_dir = Path(reference_structures_dir)
    with fsspec.open(
        "https://fs.polarishub.io/2025-01-asap-discovery/ligand_poses_reference_structures.zip"
    ) as fd:
        with zipfile.ZipFile(fd, "a") as zip_ref:
            zip_ref.extractall(reference_structures_dir)
    logger.info("Done.")
    logger.info(f"Contents:  {list(reference_structures_dir.iterdir())}")
    # We provide more information than just the protein structure
    more_stuff = list((reference_structures_dir / "SARS-CoV-2-Mpro").iterdir())
    logger.info(f"More stuff: {more_stuff}")


@typechecked
def get_df_train_for_comp_BUSTED(
    comp: CompetitionSpecification, save: bool = False
) -> pl.DataFrame:
    """
    Load training data as polars DataFrame
    Polaris has some dumbass bug where converting a competition subset to a dataframe fails, because polaris keeps adding duplicate columns to the DF?
    It doesn't make sense, I didn't dig into it, but this is the magic incantation that keeps that bug from manifesting.

    ...BUT WAIT, it gets worse
    polars chokes on rdkit.mol objects and the schema_overrides option doesn't do jack
    so let's leave this here for posterity, what the heck
    """
    logger.info(f"Loading training dataframe for comp {comp.name}...")
    df_train = pl.from_pandas(
        comp.get_train_test_split()[0].as_dataframe(),
        schema_overrides={"Ligand Pose": pl.Object},
    )
    print_info(df_train)
    if save:
        logger.info("Saving...")
        logger.info(
            "NOOOPE we're not saving anything until we're smarter about persisting rdkit mol objects"
        )
        # asap_train_raw.save(df_train)
    return df_train


@typechecked
def get_df_train_for_comp(
    comp: CompetitionSpecification, save: bool = False
) -> pl.DataFrame:
    """
    Load training data as polars DataFrame
    """
    logger.info(f"Loading training dataframe for comp {comp.name}...")
    df_train_no_poses = pl.from_pandas(
        comp.get_train_test_split()[0].as_dataframe().drop(["Ligand Pose"], axis=1)
    )
    just_poses = comp.get_train_test_split()[0].as_dataframe()["Ligand Pose"].to_list()
    df_train = df_train_no_poses.with_columns(
        pl.Series(name="ligand_pose", values=just_poses, dtype=pl.Object)
    )
    df_train = df_train.rename(
        {
            "Chain B Sequence": "chain_b_sequence",
            "Protein Label": "protein_label",
            "Chain A Sequence": "chain_a_sequence",
        }
    ).select(
        [
            "protein_label",
            "CXSMILES",
            "ligand_pose",
            "chain_a_sequence",
            "chain_b_sequence",
        ]
    )
    df_train = add_fake_id_col(df_train, "train_fake_id")
    print_info(df_train)
    if save:
        logger.info("Saving...")
        logger.info(
            "NOOOPE we're not saving anything until we're smarter about persisting rdkit mol objects"
        )
        # asap_train_raw.save(df_train)
    return df_train


@typechecked
def get_df_test_for_comp(
    comp: CompetitionSpecification, save: bool = False
) -> pl.DataFrame:
    """
    Load test data as polars DataFrame
    """
    logger.info(f"Loading training dataframe for comp {comp.name}...")
    df_test = pl.from_pandas(comp.get_train_test_split()[1].as_dataframe())
    df_test = df_test.rename(
        {
            "Chain B Sequence": "chain_b_sequence",
            "Protein Label": "protein_label",
            "Chain A Sequence": "chain_a_sequence",
        }
    ).select(["protein_label", "CXSMILES", "chain_a_sequence", "chain_b_sequence"])
    df_test = add_fake_id_col(df_test, "test_fake_id")
    print_info(df_test)
    return df_test


def download_comp_data():
    comp = load_comp()
    download_raw_data_packages()
    download_reference_structures()
