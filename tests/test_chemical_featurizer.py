from comptox_ai.chemical_featurizer.generate_vectors import *
from rdkit.Chem import Descriptors
import pytest
import os


class TestSanitizeSmiles:
    def test_sanitize_correct_smiles(self):
        assert sanitize_smiles(
            [
                "CCN(CCO)CCCC(C)NC1=CC=NC2=CC(Cl)=CC=C12",
                "CC(=O)CC(C1=CC=CC=C1)C1=C(O)C2=CC=CC=C2OC1=O",
            ]
        ) == [
            "CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12",
            "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
        ]

    def test_sanitize_incorrect_smiles(self):
        with pytest.raises(ValueError) as exec_info:
            sanitize_smiles(["abc"])
        assert f"Invalid SMILES string: abc" in str(exec_info.value)


class TestRetrieveSmiles:
    def test_retrieve_single_common_name(self):
        assert retrieve_smiles("Hydroxychloroquine") == (
            ["CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12"],
            ["Hydroxychloroquine"],
        )

    def test_retrieve_single_common_name_no_sanitize(self):
        assert retrieve_smiles("Hydroxychloroquine", sanitize_smiles_flag=False) == (
            ["CCN(CCO)CCCC(C)NC1=CC=NC2=CC(Cl)=CC=C12"],
            ["Hydroxychloroquine"],
        )

    def test_retrieve_multiple_common_name(self):
        assert retrieve_smiles(["Hydroxychloroquine", "Warfarin"]) == (
            [
                "CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12",
                "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
            ],
            ["Hydroxychloroquine", "Warfarin"],
        )

    def test_retrieve_drugbank_id(self):
        assert retrieve_smiles(
            ["DB01611", "DB00682"], chemical_descriptor_type="xrefDrugbank"
        ) == (
            [
                "CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12",
                "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
            ],
            ["DB01611", "DB00682"],
        )

    def test_retrieve_mesh_id(self):
        assert retrieve_smiles(
            ["MESH:D006886", "MESH:D014859"], chemical_descriptor_type="xrefMeSH"
        ) == (
            [
                "CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12",
                "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
            ],
            ["MESH:D006886", "MESH:D014859"],
        )

    def test_retrieve_pubchem_sid(self):
        assert retrieve_smiles(
            ["315673741.0", "315674265.0"], chemical_descriptor_type="xrefPubchemSID"
        ) == (
            [
                "CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12",
                "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
            ],
            ["315673741.0", "315674265.0"],
        )

    def test_retrieve_pubchem_cid(self):
        assert retrieve_smiles(
            ["3652", "54678486"], chemical_descriptor_type="xrefPubchemCID"
        ) == (
            [
                "CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12",
                "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
            ],
            ["3652", "54678486"],
        )

    def test_retrieve_casrn(self):
        assert retrieve_smiles(
            ["118-42-3", "81-81-2"], chemical_descriptor_type="xrefCasRN"
        ) == (
            [
                "CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12",
                "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
            ],
            ["118-42-3", "81-81-2"],
        )

    def test_retrieve_smiles(self):
        assert retrieve_smiles(
            [
                "CCN(CCO)CCCC(C)NC1=CC=NC2=CC(Cl)=CC=C12",
                "CC(=O)CC(C1=CC=CC=C1)C1=C(O)C2=CC=CC=C2OC1=O",
            ],
            chemical_descriptor_type="sMILES",
        ) == (
            [
                "CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12",
                "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
            ],
            [
                "CCN(CCO)CCCC(C)NC1=CC=NC2=CC(Cl)=CC=C12",
                "CC(=O)CC(C1=CC=CC=C1)C1=C(O)C2=CC=CC=C2OC1=O",
            ],
        )

    def test_retrieve_dtxsid(self):
        assert retrieve_smiles(
            ["DTXSID8023135", "DTXSID5023742"], chemical_descriptor_type="xrefDTXSID"
        ) == (
            [
                "CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12",
                "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
            ],
            ["DTXSID8023135", "DTXSID5023742"],
        )

class TestGenerate3DConformers:
    def test_generate_3d_conformers(self):
        mol_list = generate_3d_conformers(["CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12", "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O"])

        assert Descriptors.MolWt(mol_list[0]) == pytest.approx(335.8789999999995, 0.001)
        assert Descriptors.MolWt(mol_list[1]) == pytest.approx(308.3329999999997, 0.001)

class TestCreateVectorTable:

    def test_create_vector_table_original_chemical_ids_as_index(self):
        df_file_path = (
            "tests/example_vector_table_original_chemical_ids_as_index.pkl"
            if os.path.exists(
                "tests/example_vector_table_original_chemical_ids_as_index.pkl"
            )
            else "example_vector_table_original_chemical_ids_as_index.pkl"
        )
        expected_output_df_original_chemical_ids_as_index = pd.read_pickle(df_file_path)
        assert create_vector_table(
            ["Hydroxychloroquine", "Warfarin"], molfeat_descriptors=['maccs', "usr", "Roberta-Zinc480M-102M", "gin_supervised_masking"]
        ).equals(expected_output_df_original_chemical_ids_as_index)

    def test_create_vector_table_smiles_as_index(self):
        df_file_path = (
            "tests/example_vector_table_smiles_as_index.pkl"
            if os.path.exists("tests/example_vector_table_smiles_as_index.pkl")
            else "example_vector_table_smiles_as_index.pkl"
        )
        expected_output_df_smiles_as_index = pd.read_pickle(df_file_path)
        assert create_vector_table(
            ["Hydroxychloroquine", "Warfarin"],
            molfeat_descriptors=['maccs', "usr", "Roberta-Zinc480M-102M", "gin_supervised_masking"],
            use_original_chemical_ids_for_df_index=False,
        ).equals(expected_output_df_smiles_as_index)
