import zipfile
from pathlib import Path

import fsspec
import pandas as pd
import polaris as po
import polars as pl
from polaris.competition import CompetitionSpecification
from polaris.dataset import Dataset
from typeguard import typechecked

from polaris_asap_poses.io import (DATA_DIR_RAW_PACKAGES,
                                   DATA_DIR_RAW_REF_STRUCTURES)
from polaris_asap_poses.logger import logger
from polaris_asap_poses.util import print_info

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


def download_comp_data():
    comp = load_comp()
    download_raw_data_packages()
    download_reference_structures()
