import base64
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List
import polars as pl
from rdkit import Chem
from typeguard import typechecked

from polaris_asap_poses.logger import logger
from polaris_asap_poses.util import print_info

pl.Config(tbl_rows=500)
pl.Config(fmt_str_lengths=500)

POLARIS_ASAP_POSES_HOME = os.environ["POLARIS_ASAP_POSES_HOME"]
DATA_DIR = Path(POLARIS_ASAP_POSES_HOME) / "data"
DATA_DIR_RAW = DATA_DIR / "raw"
DATA_DIR_RAW_REF_STRUCTURES = DATA_DIR_RAW / "reference_structures"
DATA_DIR_RAW_PACKAGES = DATA_DIR_RAW / "raw_data_package"

DATA_DIR_LIGAND_SDF = DATA_DIR / "ligand_sdf"
DATA_DIR_GNINA_OUT = DATA_DIR / "gnina-out"
DATA_DIR_CLEAN = DATA_DIR / "clean"
DATA_DIR_DIRTY = DATA_DIR / "dirty"
DATA_DIR_COMBINED = DATA_DIR / "combined"

# yeah don't do this, but we'll live with it
DATA_DIR_RAW.mkdir(parents=True, exist_ok=True)
DATA_DIR_CLEAN.mkdir(parents=True, exist_ok=True)
DATA_DIR_DIRTY.mkdir(parents=True, exist_ok=True)
DATA_DIR_COMBINED.mkdir(parents=True, exist_ok=True)
DATA_DIR_LIGAND_SDF.mkdir(parents=True, exist_ok=True)
DATA_DIR_GNINA_OUT.mkdir(parents=True, exist_ok=True)

@dataclass
class NamedDataset:
    """
    put a tags dict in here someday or something
    """

    name: str
    filepath: Path | str

    def save(self, df: pl.DataFrame) -> None:
        logger.info(f"Saving {self.name} to {self.filepath}...")
        if str(self.filepath).endswith(".csv"):
            df.write_csv(self.filepath)
        elif str(self.filepath).endswith(".parquet"):
            df.write_parquet(self.filepath)
        else:
            raise ValueError(f"Unsupported file format: {self.filepath}")
        logger.info("Done.")

    def read(
        self,
        show_columns: bool = False,
        show_unique: bool = False,
        n: int | None = None,
    ) -> pl.DataFrame:
        logger.info(f"Reading {self.name} from {self.filepath}...")
        if str(self.filepath).endswith(".csv"):
            df = pl.read_csv(self.filepath, n_rows=n)
        elif str(self.filepath).endswith(".parquet"):
            df = pl.read_parquet(self.filepath, n_rows=n)
        else:
            raise ValueError(f"Unsupported file format: {self.filepath}")
        print_info(df, show_columns=show_columns, show_unique=show_unique)
        logger.info("Done.")
        return df


@typechecked
def write_sdf(mol: Chem.Mol, path: Path):
    """
    Write a single RDKit molecule to an SDF file at the specified path.
    """
    with Chem.SDWriter(path) as w:
        w.write(mol=mol)


@typechecked
def read_sdf(path: Path) -> List[Chem.Mol]:
    """
    Read a single RDKit molecule from an SDF file at the specified path.
    """
    supplier = Chem.SDMolSupplier(path)
    mols = [x for x in supplier]
    if len(mols) > 1:
        logger.warning(f"{path} contains {len(mols)} mols, which is too many mols")
    if len(mols) == 0:
        logger.warning(f"{path} contains {len(mols)} mols, where are your mols bro")
    return mols


@typechecked
def serialize_rdkit_mol(mol: Chem.Mol):
    """
    Serialize an RDKit molecule, to prepare for submission.
    """
    props = Chem.PropertyPickleOptions.AllProps
    mol_bytes = mol.ToBinary(props)
    return base64.b64encode(mol_bytes).decode("ascii")
