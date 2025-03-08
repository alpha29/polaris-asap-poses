import subprocess
from pathlib import Path

from python_on_whales import docker
from typeguard import typechecked

from polaris_asap_poses.download import get_df_test_for_comp, load_comp
from polaris_asap_poses.io import (DATA_DIR_GNINA_OUT, DATA_DIR_LIGAND_SDF,
                                   DATA_DIR_RAW_REF_STRUCTURES,
                                   POLARIS_ASAP_POSES_HOME)
from polaris_asap_poses.logger import logger
from polaris_asap_poses.model import MERS, SARS


def test_run_gnina_docker():
    protein_pdb = DATA_DIR_RAW_REF_STRUCTURES / "MERS-CoV-Mpro" / "protein.pdb"
    ligand_sdf = DATA_DIR_LIGAND_SDF / "test_73_MERS-CoV-Mpro.sdf"
    autobox_ligand_sdf = DATA_DIR_RAW_REF_STRUCTURES  / "MERS-CoV-Mpro" / "ligand.sdf"
    output_sdf = DATA_DIR_GNINA_OUT / "docked_test_73_mers.sdf"
    run_gnina_docker(protein_pdb=protein_pdb, ligand_sdf=ligand_sdf, autobox_ligand_sdf=autobox_ligand_sdf, output_sdf=output_sdf, seed=0)


def test_run_gnina_prebuilt():
    protein_pdb = DATA_DIR_RAW_REF_STRUCTURES / "MERS-CoV-Mpro" / "protein.pdb"
    ligand_sdf = DATA_DIR_LIGAND_SDF / "test_73_MERS-CoV-Mpro.sdf"
    autobox_ligand_sdf = DATA_DIR_RAW_REF_STRUCTURES  / "MERS-CoV-Mpro" / "ligand.sdf"
    output_sdf = DATA_DIR_GNINA_OUT / "docked_test_73_mers.sdf"
    run_gnina_prebuilt(protein_pdb=protein_pdb, ligand_sdf=ligand_sdf, autobox_ligand_sdf=autobox_ligand_sdf, output_sdf=output_sdf, seed=0)


def run_gnina_docker(
    protein_pdb: Path | str,
    ligand_sdf: Path | str,
    autobox_ligand_sdf: Path | str,
    output_sdf: Path | str,
    seed: int = -1,
):
    logger.info("Running gnina via docker...")

    cmd = (
        f"gnina -r /scr/{protein_pdb.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"-l /scr/{ligand_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"--autobox_ligand /scr/{autobox_ligand_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"-o /scr/{output_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        "--log /scr/log/gnina.log "
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
    autobox_ligand_sdf: Path | str,
    output_sdf: Path | str,
    seed: int = -1,
):
    logger.info("Running gnina (prebuilt)...")

    cmd = (
        f"./bin/gnina -r {protein_pdb.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"-l {ligand_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"--autobox_ligand {autobox_ligand_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        f"-o {output_sdf.relative_to(POLARIS_ASAP_POSES_HOME)} "
        "--log log/gnina.log "
        "--exhaustiveness 16"
    )

    if seed >= 0:
        cmd = cmd + f" --seed {seed}"

    logger.info(f"Command: {cmd}")

    result = subprocess.run(cmd.split(" "), check=True)

    logger.info(result)
    logger.info("Done.")


def run():
    logger.info("Start.")
    comp = load_comp()
    df_test = get_df_test_for_comp(comp)
    for row in df_test.iter_rows(named=True):
        logger.info(
            f"Processing id {row['test_fake_id']}, protein {row['protein_label']}, CXSMILES {row['CXSMILES']}..."
        )

        match row["protein_label"]:
            case SARS.data_label:
                this_protein = SARS
            case MERS.data_label:
                this_protein = MERS
            case _:
                raise ValueError(
                    f"Invalid protein_label {row['protein_label']} for test_fake_id {row['test_fake_id']}"
                )

        protein_pdb_path = (
            DATA_DIR_RAW_REF_STRUCTURES / this_protein.path_segment / "protein.pdb"
        )
        ligand_sdf_path = (
            DATA_DIR_LIGAND_SDF
            / f"test_{row['test_fake_id']}_{this_protein.path_segment}.sdf"
        )
        autobox_ligand_sdf_path = (
            DATA_DIR_RAW_REF_STRUCTURES / this_protein.path_segment / "ligand.sdf"
        )
        docking_result_path = (
            DATA_DIR_GNINA_OUT
            / f"docked_test_{row['test_fake_id']}_{this_protein.path_segment}.sdf"
        )
        run_gnina_prebuilt(
            protein_pdb=protein_pdb_path,
            ligand_sdf=ligand_sdf_path,
            autobox_ligand_sdf=autobox_ligand_sdf_path,
            output_sdf=docking_result_path,
        )
    logger.info("Done.")


if __name__ == "__main__":
    #run()
    test_run_gnina_docker()
