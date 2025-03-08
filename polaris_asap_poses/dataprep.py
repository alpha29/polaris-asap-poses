from polaris_asap_poses.download import load_comp, get_df_train_for_comp, get_df_test_for_comp
from polaris_asap_poses.io import DATA_DIR_LIGAND_SDF, write_sdf
from polaris_asap_poses.model import SARS, MERS
from polaris_asap_poses.logger import logger
from rdkit import Chem

def write_test_ligand_sdfs():
    logger.info("Start.")
    comp = load_comp()
    df_test = get_df_test_for_comp(comp)
    for row in df_test.iter_rows(named=True):
        logger.info(f"Processing id {row['test_fake_id']}, protein {row['protein_label']}, CXSMILES {row['CXSMILES']}...")

        match row["protein_label"]:
            case SARS.data_label:
                this_protein = SARS
            case MERS.data_label:
                this_protein = MERS
            case _:
                raise ValueError(f"Invalid protein_label {row['protein_label']} for test_fake_id {row['test_fake_id']}")
        mol = Chem.MolFromSmiles(row["CXSMILES"])
        ligand_sdf_path = DATA_DIR_LIGAND_SDF / f"test_{row['test_fake_id']}_{this_protein.path_segment}.sdf"
        write_sdf(mol=mol, path=ligand_sdf_path)
    logger.info("Done.")

if __name__ == "__main__":
    write_test_ligand_sdfs()
