"""
Similarity algorithms for data in ComptoxAI's graph database.

These algorithms may use database routines (e.g., Neo4j's Graph Data Science
library) or may use other, third-party libraries.
"""

import re

import scipy.spatial.distance as spdist


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from comptox_ai.db import GraphDB


def _make_distance_matrix(feature_matrix, metric):
    distance = spdist.pdist(feature_matrix, metric=metric)
    return distance


def chemical_similarity(db: GraphDB, chemicals: list=None, chemical_list: str=None, metric: str='cosine', property: str='maccs'):
    """Compute pairwise similarity scores between all pairs of chemicals in a
    specified group based on tabular chemical properties (i.e., graph structure
    is not used).
    
    Parameters
    ----------
    db : comptox_ai.db.GraphDB
        An instance of a ComptoxAI graph database.
    chemicals : list
        A list of DSSTOX IDs or CASRNs corresponding to the chemicals you would
        like to analyze.
    chemical_list : str or list of str
        Acronym corresponding to a chmical list (or a list of acronyms, in
        which case the union of those chemical lists will be retrieved).
    metric : str, default 'cosine'
        The distance metric to use. All distance metrics provided by
        `scipy.spatial.distance` are supported - for a complete list see 
        https://docs.scipy.org/doc/scipy/reference/spatial.distance.html
    property : str, default 'maccs'
        Node property to use for distance computation. `maccs` (or another
        chemical fingerprint) is recommended.

    Returns
    -------
    list of str
        A list of chemical DSSTOX IDs corresponding to the rows (and columns)
        of the distance matrix.
    numpy.ndarray
        A 2-dimensional ndarray of pairwise distances between chemicals.
    """
    if (chemicals==None and chemical_list==None):
        return ValueError("Either `chemicals` or `chemical_list` must be given")

    dtxsids = []
    casrns = []

    # Get chemicals and/or chemical_list and merge IDs
    if chemicals:
        # Do we have DSSTOX IDs or CASRNs?
        for chem in chemicals:
            if re.match(r'DTXSID\d{7,9}', chem):  # Regex DSSTOX Substance ID
                dtxsids.appen(chem)
            elif re.match(r'[1-9]\d{1,6}-\d{2}-\d', chem):  # Regex CASRN
                casrnrs.append(chem)
        
        if (len(dtxsids) == 0) and (len(casrns) == 0):
            raise ValueError("`chemicals` did not contain any valid DTXSIDs or CASRNs")

    if len(dtxsids) > 0:
        dtxsid_data = db.fetch_nodes("Chemical", "xrefDTXSID", dtxsids)
    if len(casrns) > 0:
        casrn_data = db.fetch_nodes("Chemical", "xrefCasRN", casrns)

    if chemical_list:
        _, list_data = db.fetch_chemical_list(chemical_list)