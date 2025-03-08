import subprocess
from pathlib import Path

from python_on_whales import docker
from typeguard import typechecked

from polaris_asap_poses.io import (DATA_DIR_GNINA_OUT, DATA_DIR_LIGAND_SDF,
                                   POLARIS_ASAP_POSES_HOME)
from polaris_asap_poses.logger import logger


def test_run_gnina_docker():
    data_dir_mers_ref_struct = (
        Path(POLARIS_ASAP_POSES_HOME) / "data/raw/reference_structures/MERS-CoV-Mpro"
    )
    protein_pdb = data_dir_mers_ref_struct / "protein.pdb"
    ligand_sdf = DATA_DIR_LIGAND_SDF / "test_73_MERS-CoV-Mpro.sdf"
    output_sdf = DATA_DIR_GNINA_OUT / "docked_test_73_mers.sdf"
    run_gnina_docker(protein_pdb, ligand_sdf, output_sdf, seed=0)


def test_run_gnina_prebuilt():
    data_dir_mers_ref_struct = (
        Path(POLARIS_ASAP_POSES_HOME) / "data/raw/reference_structures/MERS-CoV-Mpro"
    )
    protein_pdb = data_dir_mers_ref_struct / "protein.pdb"
    ligand_sdf = DATA_DIR_LIGAND_SDF / "test_73_MERS-CoV-Mpro.sdf"
    output_sdf = DATA_DIR_GNINA_OUT / "docked_test_73_mers.sdf"
    run_gnina_prebuilt(protein_pdb, ligand_sdf, output_sdf, seed=0)


def run_gnina_docker(
    protein_pdb: Path | str,
    ligand_sdf: Path | str,
    output_sdf: Path | str,
    seed: int = -1,
):
    logger.info("Running gnina via docker...")

    cmd = (
        f"gnina -r /scr/{protein_pdb.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"-l /scr/{ligand_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"--autobox_ligand /scr/{ligand_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"-o /scr/{output_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        "--exhaustiveness 16"
    )

    if seed >= 0:
        cmd = cmd + f" --seed {seed}"

    logger.info(f"Command: {cmd}")

    result = docker.run(
        image="gnina/gnina",
        command=cmd.split(" "),
        volumes=[(POLARIS_ASAP_POSES_HOME, "/scr")],
        remove=True,
    )
    logger.info(result)
    logger.info("Done.")


def run_gnina_prebuilt(
    protein_pdb: Path | str,
    ligand_sdf: Path | str,
    output_sdf: Path | str,
    seed: int = -1,
):
    logger.info("Running gnina (prebuilt)...")

    cmd = (
        f"gnina -r {protein_pdb.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"-l {ligand_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"--autobox_ligand {ligand_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"-o {output_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        "--exhaustiveness 16"
    )

    if seed >= 0:
        cmd = cmd + f" --seed {seed}"

    logger.info(f"Command: {cmd}")

    result = subprocess.run(cmd.split(" "), check=True)

    logger.info(result)
    logger.info("Done.")


if __name__ == "__main__":
    test_run_gnina_prebuilt()
