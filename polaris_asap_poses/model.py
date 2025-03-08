


from dataclasses import dataclass
from pathlib import Path

from polaris_asap_poses.io import DATA_DIR_RAW_REF_STRUCTURES



@dataclass
class Protein():
    name: str
    data_label: str     # This is what you see in df_train and df_test
    path_segment: str   # This is what's actually in the filepath - fully hyphenated, no spaces
    ref_dir: Path = Path()
    ref_fasta_path: Path = Path()
    ref_pdb_path: Path = Path()
    ref_ligand_smi_path: Path = Path()
    ref_ligand_sdf_path: Path = Path()
    ref_complex_path: Path = Path()

    def __post_init__(self):
        self.ref_dir = DATA_DIR_RAW_REF_STRUCTURES / self.path_segment
        self.ref_fasta_path = self.ref_dir / "protein.fasta"
        self.ref_pdb_path = self.ref_dir / "protein.pdb"
        self.ref_ligand_smi_path = self.ref_dir / "ligand.smi"
        self.ref_ligand_sdf_path = self.ref_dir / "ligand.sdf"
        self.ref_complex_path = self.ref_dir / "complex.pdb"

    def validate(self):
        assert self.ref_dir.exists() and self.ref_dir.is_dir
        assert self.ref_fasta_path.exists() and self.ref_fasta_path.is_file()
        assert self.ref_pdb_path.exists() and self.ref_fasta_path.is_file()
        assert self.ref_ligand_smi_path.exists() and self.ref_ligand_smi_path.is_file()
        assert self.ref_ligand_sdf_path.exists() and self.ref_ligand_sdf_path.is_file()
        assert self.ref_complex_path.exists() and self.ref_complex_path.is_file()

SARS = Protein(name="SARS", data_label="SARS-CoV-2 Mpro", path_segment="SARS-CoV-2-Mpro")
MERS = Protein(name="MERS", data_label="MERS-CoV Mpro", path_segment="MERS-CoV-Mpro")
