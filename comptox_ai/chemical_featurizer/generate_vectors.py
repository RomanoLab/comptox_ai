from comptox_ai.db.graph_db import GraphDB
from molfeat.trans import MoleculeTransformer
from molfeat.trans.pretrained.hf_transformers import PretrainedHFTransformer
from molfeat.trans.pretrained import PretrainedDGLTransformer
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, AllChem
import numpy as np
import pandas as pd
from collections import defaultdict
from itertools import chain


RDLogger.DisableLog("rdApp.*")  # Disable rdkit warnings


def sanitize_smiles(smiles_list):
    """
    Check and correct issues related to kekulization, valencies, aromaticity, conjugation, and hybridization for each SMILES string in a list of SMILES strings.

    Parameters
    ----------
    smiles_list : List[str]
        A list of SMILES strings.

    Returns
    -------
    List[str]
        List of sanitized SMILES strings.

    Examples
    --------
    >>> from comptox_ai.chemical_featurizer.generate_vectors import sanitize_smiles
    >>> smiles_list = ["CCN(CCO)CCCC(C)NC1=CC=NC2=CC(Cl)=CC=C12", "CC(=O)CC(C1=CC=CC=C1)C1=C(O)C2=CC=CC=C2OC1=O"]
    >>> sanitize_smiles(smiles_list)
    ['CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12', 'CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O']
    """

    print("Sanitizing sMILES")

    cleaned_smiles = []
    for smiles in smiles_list:
        try:
            cleaned_smiles.append(
                Chem.MolToSmiles(Chem.MolFromSmiles(smiles, sanitize=True))
            )
        except Exception as e:
            raise ValueError(f"Invalid SMILES string: {smiles}. Error: {str(e)}")

    return cleaned_smiles


def retrieve_smiles(
    chemicals_to_find, chemical_descriptor_type="commonName", sanitize_smiles_flag=True
):
    """
    Convert chemicals IDs (potentially with various representations) to a list of SMILES strings by querying the ComptoxAI database.

    Parameters
    ----------
    chemicals_to_find : Union(str, List[str], Dict[str, List[str]]
        A single chemical ID, list of chemicals IDs, or dictionary of {chemical_descriptor : list of chemical IDs} key-value pairs.
    chemical_descriptor_type : str
        Indicates the chemical descriptor type for chemcials_to_find if chemicals_to_find is str or List[str].
        Valid chemical_descriptor types include commonName, Drugbank ID (xrefDrugbank), MeSH ID (xrefMeSH), PubChem SID (xrefPubchemSID), PubChem CID(xrefPubchemCID), CasRN (xrefCasRN), sMILES, DTXSID (xrefDTXSID).
    sanitize_smiles_flag : bool
        Whether sanitize_smiles() should be run on the retrieved SMILES strings.

    Returns
    -------
    List[str]
        List of sanitized SMILES strings.

    Raises
    -------
    ValueError
        If type of chemicals_to_find is not str, List[str] or Dict[str, List[str]]

    Examples
    --------
    >>> from comptox_ai.chemical_featurizer.generate_vectors import retrieve_smiles
    >>> retrieve_smiles(["Hydroxychloroquine", "Warfarin"])
    ['CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12', 'CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O']
    """

    if type(chemicals_to_find) == str:
        chemicals_to_find = [chemicals_to_find]

    if chemical_descriptor_type == "sMILES" and type(chemicals_to_find) in (
        str,
        list,
    ):  # Return list of smiles directly no need to query database
        if sanitize_smiles_flag:
            return sanitize_smiles(chemicals_to_find), chemicals_to_find
        else:
            return chemicals_to_find, chemicals_to_find

    if type(chemicals_to_find) in (str, list, dict):

        if not isinstance(chemicals_to_find, dict):
            chemicals_to_find = {chemical_descriptor_type: chemicals_to_find}

        # Build Cypher query
        query = " OR ".join(
            [
                f"n.{descriptor} = '{chemical}'"
                for descriptor, chemical_list in chemicals_to_find.items()
                for chemical in chemical_list
            ]
        )

    else:
        raise ValueError(
            "Chemicals_to_find should either be a single chemical as a string, a list of chemicals that are the have the same type of descriptor or a dictionary of {descriptor type : List[chemical]} key-value pairs."
        )

    db = GraphDB()
    nodes = db.run_cypher(f"MATCH (n:Chemical) WHERE {query} RETURN n")

    nodes = [
        item["n"] for item in nodes
    ]  # Remove a layer of the cypher query result where all keys are 'n'
    smiles_list = [node["sMILES"] for node in nodes]

    # Determine which chemicals were not found
    # Track chemicals in user input grouped by their chemical descriptor type
    chemicals_to_find_tracking_dict = defaultdict(lambda: set())

    for descriptor, chemical_list in chemicals_to_find.items():
        chemicals_to_find_tracking_dict[descriptor] |= set(chemical_list)

    # Track chemicals returned by querying database grouped by chemical descriptor type

    found_chemicals_dict = defaultdict(lambda: set())

    for node in nodes:
        for descriptor in list(chemicals_to_find_tracking_dict.keys()):
            found_chemicals_dict[descriptor].add(node[descriptor])

    # Take the difference of sets between user requested chemicals and found chemicals per descriptor

    for k in chemicals_to_find_tracking_dict.keys():
        chemicals_to_find_tracking_dict[k] -= found_chemicals_dict[k]

    # Chemicals not found are left after taking set difference; combine these across descriptor types
    chemicals_not_found = set().union(*list(chemicals_to_find_tracking_dict.values()))

    print()
    if chemicals_not_found:
        print(chemicals_not_found, "were not found", "\n")

    # Original chemical identifiers of found chemicals
    found_chemical_id_list = []
    chemicals_to_find_set = set(chain(*chemicals_to_find.values()))
    for node in nodes:
        for id_type in found_chemicals_dict.keys():
            chemical_id = node[id_type]
            if chemical_id in chemicals_to_find_set:
                found_chemical_id_list.append(chemical_id)
                continue

    if sanitize_smiles_flag:
        smiles_list = sanitize_smiles(smiles_list)

    return smiles_list, found_chemical_id_list


def generate_3d_conformers(smiles_list):
    """
    Generates a list of mol objects with 3D conformer data from input list of SMILES strings.

    Parameters
    ----------
    smiles_list : List[str]
        List of SMILES strings.

    Returns
    -------
    List[rdkit.Chem.rdchem.Mol]
        List of mol objects with 3D conformer information.

    Examples
    --------
    >>> from comptox_ai.chemical_featurizer.generate_vectors import generate_3d_conformers
    >>> from rdkit.Chem import Descriptors
    >>> mol = generate_3d_conformers(["CCN(CCO)CCCC(C)Nc1ccnc2cc(Cl)ccc12"])
    >>> Descriptors.MolWt(mol[0])
    335.8789999999995
    """
    mols_with_3d = []
    for smiles in smiles_list:
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=0)
            AllChem.UFFOptimizeMolecule(mol)
            mols_with_3d.append(mol)
    return mols_with_3d


def create_vector_table(
    chemicals_to_find,
    chemical_descriptor_type="commonName",
    sanitize_smiles_flag=True,
    rdkit_descriptors=True,
    molfeat_descriptors=[],
    dtype=np.float32,
    use_original_chemical_ids_for_df_index=True,
):
    """
    Constructs Pandas DataFrame of vector (i.e. embedding) features for query chemicals.

    Parameters
    ----------
    chemicals_to_find : Union(str, List[str], Dict[str, List[str]]
        A single chemical ID, list of chemicals IDs, or dictionary of {chemical_descriptor : list of chemical IDs} key-value pairs.
    chemical_descriptor_type : str
        Indicates the chemical descriptor type for chemcials_to_find if chemicals_to_find is str or List[str].
        Valid chemical_descriptor types include commonName, Drugbank ID, MeSH ID, PubChem SID, PubChem CID, CasRN, sMILES, DTXSID.
    sanitize_smiles_flag : bool
        Whether sanitize_smiles() should be run on the retrieved SMILES strings.
    rdkit_descriptors : bool
        Whether full set of rdkit_descriptors should be calculated and incorporated as vectors.
    dtype : type
        Data type of output df (e.g. float, np.float32, etc.).
    molfeat_descriptors : List[str]
        List of features to generate. For possible features, see https://molfeat.datamol.io/featurizers.
     use_original_chemical_ids_for_df_index : bool
        Whether to use input chemical IDs or generated SMILES strings as the DataFrame index.

    Returns
    -------
    Pandas DataFrame
        List of sanitized SMILES strings.

    Raises
    -------
    ValueError
        If type of rdkit_descriptors is not bool or type of molfeat_descriptors is not list.

    Examples
    --------
    >>> from comptox_ai.chemical_featurizer.generate_vectors import create_vector_table
    >>> create_vector_table(["Hydroxychloroquine", "Warfarin"])
                                   maccs                  erg           ...  fr_thiophene  fr_unbrch_alkane  fr_urea
    Hydroxychloroquine     [0.0, 0.0, 0.0, ...]   [0.0, 0.0, 0.0, ...]  ...      0.0              0.0          0.0
    Warfarin               [0.0, 0.0, 0.0, ...]   [0.0, 0.0, 0.0, ...]  ...      0.0              0.0          0.0
    """

    if not isinstance(rdkit_descriptors, bool) or not isinstance(
        molfeat_descriptors, list
    ):
        raise ValueError(
            "Rdkit_descriptors should be True or False and molfeat_descriptors should be list of desired vector features."
        )

    smiles_list, found_chemical_id_list = retrieve_smiles(
        chemicals_to_find, chemical_descriptor_type, sanitize_smiles_flag
    )

    vectors = []
    df_column_names = []
    conformer_3D_flag = False

    if molfeat_descriptors:

        for feature in molfeat_descriptors:
            print(f"Calculating {feature} descriptors")

            if feature in {
                "Roberta-Zinc480M-102M",
                "GPT2-Zinc480M-87M",
                "ChemGPT-1.2B",
                "ChemGPT-19M",
                "ChemGPT-4.7M",
                "MolT5",
                "ChemBERTa-77M-MTR",
                "ChemBERTa-77M-MLM",
            }:
                featurizer = PretrainedHFTransformer(
                    kind=feature, notation="smiles", dtype=dtype
                )

            elif feature in {
                "gin_supervised_masking",
                "gin_supervised_infomax",
                "gin_supervised_edgepred",
                "jtvae_zinc_no_kl",
                "gin_supervised_contextpred",
            }:
                featurizer = PretrainedDGLTransformer(kind=feature, dtype=dtype)

            else:
                featurizer = MoleculeTransformer(
                    featurizer=feature, dtype=dtype, verbose=True
                )
                if feature in {
                    "desc3D",
                    "desc2D",
                    "electroshape",
                    "usrcat",
                    "usr",
                    "cats3d",
                    "pharm3D-cats",
                    "pharm3D-gobbi",
                    "pharm3D-pmapper",
                }:
                    mol_list = generate_3d_conformers(smiles_list)
                    conformer_3D_flag = True

            chemical_list = mol_list if conformer_3D_flag else smiles_list
            vectors.append(featurizer(chemical_list).tolist())

            df_column_names.append(feature)

    if rdkit_descriptors:
        print(f"Calculating rdkit descriptors")
        mols = [Chem.MolFromSmiles(smiles) for smiles in smiles_list]
        rdkit_features = np.array(
            [
                np.array(
                    list(Descriptors.CalcMolDescriptors(mol).values()), dtype=dtype
                )
                for mol in mols
            ]
        )

        df_column_names += list(Descriptors.CalcMolDescriptors(mols[0]).keys())

        for column in rdkit_features.T:
            vectors.append(column.tolist())

    df_dict = {
        column_name: vector for column_name, vector in zip(df_column_names, vectors)
    }

    df = pd.DataFrame(df_dict)

    df.index = (
        found_chemical_id_list
        if use_original_chemical_ids_for_df_index
        else smiles_list
    )

    return df
