from comptox_ai.db.graph_db import GraphDB

from molfeat.trans.fp import FPVecTransformer
from rdkit import Chem
from rdkit.Chem import Descriptors
import numpy as np
import pandas as pd
from tqdm import tqdm


def retrieve_smiles(chemicals_to_find, chemical_descriptor_type="commonName"):
    if isinstance(chemicals_to_find, str):
        properties = {chemical_descriptor_type: chemicals_to_find}
    elif isinstance(chemicals_to_find, list):
        properties = {
            chemical_descriptor_type: chemical for chemical in chemicals_to_find
        }
    elif isinstance(chemicals_to_find, dict):
        properties = chemicals_to_find
    else:
        raise Exception(
            "chemicals_to_find should either be a list of chemicals that are the have the same type of descriptor or a dictionary of {descriptor type : chemical} descriptor key-value pairs"
        )

    db = GraphDB()
    nodes = list(db.find_nodes(properties=properties, node_types=["Chemical"]))

    smiles_list = [node["sMILES"] for node in nodes]

    return smiles_list


def create_vector_table(smiles_list, rdkit_descriptors=True, molfeat_descriptors=[]):

    if not isinstance(rdkit_descriptors, bool) or not isinstance(
        molfeat_descriptors, list
    ):
        raise Exception(
            "rdkit_descriptors should be True or False and molfeat_descriptors should be list of desired vector features"
        )

    vectors = []
    df_column_names = []

    if molfeat_descriptors:
        molfeat_features = dict()

        for feature in molfeat_descriptors:
            print(f"Calculating {feature} descriptors")
            featurizer = FPVecTransformer(kind=feature, dtype=np.float32)
            molfeat_features[feature] = featurizer(smiles_list)

        for k, v in molfeat_features.items():
            df_column_names += [f"{k}_{i}" for i in range(v.shape[1])]

        vectors.append(np.hstack(list(molfeat_features.values())))

    if rdkit_descriptors:
        print(f"Calculating rdkit descriptors")
        mols = [Chem.MolFromSmiles(smiles) for smiles in smiles_list]
        rdkit_features = [
            np.array(list(Descriptors.CalcMolDescriptors(mol).values())) for mol in mols
        ]

        df_column_names += list(Descriptors.CalcMolDescriptors(mols[0]).keys())

        vectors.append(np.vstack(rdkit_features))


    df = pd.DataFrame(np.hstack(vectors), columns=df_column_names)

    df.index = smiles_list

    return df


def chemicals_to_vectors(
    chemicals_to_find,
    chemical_descriptor_type="commonName",
    rdkit_descriptors=True,
    molfeat_descriptors=[],
):

    smiles_list = retrieve_smiles(chemicals_to_find, chemical_descriptor_type)

    return create_vector_table(smiles_list, rdkit_descriptors, molfeat_descriptors)
