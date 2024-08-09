"""ComptoxAI's main interface with Neo4j.

This class and its methods maintain a connection to either a local or remote
instance of the ComptoxAI graph database, and provide convenient access to the
database's contents.

"""

# Authors: Joseph D. Romano <joseph.romano@pennmedicine.upenn.edu>
#
# Copyright: (c) 2021 by Joseph D. Romano
#
# License: MIT License

from logging import warn
import os
import warnings
from pathlib import Path
from neo4j.api import Version
from yaml import load, Loader
from dataclasses import dataclass
from typing import List, Dict
from textwrap import dedent

import ipdb

from neo4j import GraphDatabase
from neo4j.exceptions import (
    ClientError,
    AuthError,
    CypherSyntaxError,
    ServiceUnavailable,
)

import comptox_ai.db


def _get_default_config_file():
    root_dir = Path(__file__).resolve().parents[2]
    if os.path.exists(os.path.join(root_dir, "CONFIG.yaml")):
        default_config_file = os.path.join(root_dir, "CONFIG.yaml")
    else:
        default_config_file = os.path.join(root_dir, "CONFIG-default.yaml")
    return default_config_file


@dataclass
class Metagraph:
    """
    A metagraph containing the node types and relationship types (and their
    connectivity) in the overall graph database.

    Parameters
    ----------
    node_labels : list of str
        A list of node labels in the graph database.
    node_label_counts : dict of int
        A mapping from all node labels in `node_labels` to the corresponding number
        of nodes of that type in the graph database.
    relationship_types : list of str
        A list of relationship types in the graph database.
    relationship_path_schema : dict of list
        A mapping from each relationship type present in the graph database to a
        list describing valid (subject, object) pairs (in other words, all existing
        'from' node types and 'to' node types linked by the given relationship).
    """

    node_labels: List[str]
    node_label_counts: Dict[str, int]
    relationship_types: List[str]
    relationship_path_schema: Dict[str, Dict[str, int]]


class Node(dict):
    """
    A node in ComptoxAI's graph database.

    This class is essentially an immutable dict that is populated at
    initialization time via a connection to ComptoxAI's graph database.

    Parameters
    ----------
    db : comptox_ai.db.GraphDB
        ComptoxAI graph database in which to perform the node search.
    node_type : str
        Node label for the entity type being searched.
    search_params : dict
        Dict of parameters for querying nodes in the database. Exact string
        matching will be used to query these node properties (i.e., all must be
        an exact match for the node to be identified). Dict keys are node
        property names, and dict values are node property values.
    return_first_match : bool
        If `False`, searches that match multiple nodes will raise an exception.
        Otherwise, the first matching node in query results will be returned
        (all subsequent matches will be discarded).

    Example
    -------
    >>> db = GraphDB(hostname="neo4j.comptox.ai")
    >>> n = Node(db, "Chemical", {"xrefCasRN": "69313-80-0"})
    {'commonName': '1-[(2xi)-2,3-O-(1-Methylethylidene)-alpha-D-threo-pentofuranosyl]-1H-1,2,4-triazole-3-carboxamide',
     'maccs': '0000000000000000000000000000000000000100000000000001000010000100100000010110101101110000100101111000100010001101000010011111000000111000101101000101101111111111110110',
     'synonyms': '',
     ...}
    """

    def __init__(self, db, node_type, search_params, return_first_match=False):
        # build search query
        where_clause = ", ".join([f"n.{k} = '{v}'" for k, v in search_params.items()])

        node_search_query = f"""
        MATCH (n:{node_type})
        WHERE {where_clause}
        RETURN n;
        """
        print(node_search_query)

        node_search_res = db.run_cypher(node_search_query)

        if len(node_search_res) == 0:
            raise Exception("Error: Node not found in graph database")
        elif len(node_search_res) > 1:
            if return_first_match == False:
                raise Exception(
                    "Error: Multiple nodes match query. Use `return_first_match=True` to bypass error and use first matching node."
                )

        self.update(node_search_res[0]["n"].items())


class Graph(object):
    """
    A Neo4j graph, as defined by the Neo4j Graph Data Science Library. In
    general, users shouldn't instantiate this class directly - let a GraphDB
    instance handle that for you instead.

    See https://neo4j.com/docs/graph-data-science/current/management-ops/.

    Parameters
    ----------
    source_db : comptox_ai.db.GraphDb
        A Neo4j graph database object, as defined in ComptoxAI.
    name : str
        A name that can be used to identify the graph.
    """

    def __init__(self, source_db, name):
        self._db = source_db
        self.name = name


class GraphDB(object):
    """
    A Neo4j graph database containing ComptoxAI graph data.

    Parameters
    ----------
    hostname : string, default `"neo4j.comptox.ai"`
        Hostname specifying the location of a Neo4j instance to which to connect. The
        most likely values are `"neo4j.comptox.ai"` or `"localhost"`. If a non-standard
        port is used for broadcasting the Neo4j server, it can be appended to the end of
        the hostname (e.g., `"localhost:7688"`).
    username : string, default None
        Username for authentication to Neo4j. If no username or password are provided,
        a connection will be attempted without authentication.
    password : string, defualt None
        Password for authentication to Neo4j. If no username or password are provided,
        a connection will be attempted without authentication.
    verbose : bool, default True
        Sets verbosity to on or off. If True, status information will be returned
        to the user occasionally.
    """

    def __init__(
        self,
        hostname="neo4j.comptox.ai",
        username=None,
        password=None,
        verbose=False,
        silent=False,
    ):
        if not silent:
            print(f"Attempting to connect to public Neo4j database at `{hostname}`...")
            if (not username) and (not password):
                print(
                    f"No username/password provided - attempting to connect without authentication."
                )

        self.is_connected = False
        self.verbose = verbose

        if hostname:
            self.username = username
            self.password = password
            self.hostname = hostname

        self._connect()

        if not silent:
            print("...connection established successfully.")

        self.exporter = comptox_ai.db.GraphExporter(self)

    def __repr__(self):
        return dedent(
            f"""\
                ------------------------
                ComptoxAI graph database
                ------------------------
                Hostname: {self.hostname}
                Username: {self.username}"""
        )

    def _connect(self):
        username = self.username
        password = self.password
        hostname = self.hostname

        if hostname == "localhost":
            uri = "bolt://localhost:7687"
        else:
            uri = f"neo4j://{hostname}"

        # Create the graph database driver
        try:
            if (username is None) and (password is None):
                self._driver = GraphDatabase.driver(uri)
            else:
                self._driver = GraphDatabase.driver(uri, auth=(username, password))
        except AuthError as e:
            raise RuntimeError(
                "Could not find a database using the configuration provided."
            )

        # Test the connection to make sure we are connected to a database
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", "The configuration may change in the future."
                )
                conn_result = self._driver.verify_connectivity()
        except ServiceUnavailable:
            raise RuntimeError(
                "Neo4j driver created but we couldn't connect to any routing servers. You might be using an invalid hostname."
            )
        except ValueError:
            raise RuntimeError(
                "Neo4j driver created but the host address couldn't be resolved. Check your hostname, port, and/or protocol."
            )

        if conn_result is None:
            raise RuntimeError(
                "Neo4j driver created but a valid connection hasn't been established. You might be using an invalid hostname."
            )

    def _disconnect(self):
        self._driver.close()

    @staticmethod
    def _run_transaction(tx, query):
        result = tx.run(query)
        return result.data()

    def run_cypher(self, qry_str, verbose=True):
        """
        Execute a Cypher query on the Neo4j graph database.

        Parameters
        ----------
        qry_str : str
        A string containing the Cypher query to run on the graph database server.

        Returns
        -------
        list
        The data returned in response to the Cypher query.

        Examples
        --------
        >>> from comptox_ai.db import GraphDB
        >>> g = GraphDB()
        >>> g.run_cypher("MATCH (c:Chemical) RETURN COUNT(c) AS num_chems;")
        [{'num_chems': 719599}]
        """
        with self._driver.session() as session:
            if self.verbose:
                if (
                    verbose
                ):  # users can still override verbosity at the run_cypher level
                    print(f"Writing Cypher transaction: \n  {qry_str}")
            try:
                res = session.write_transaction(self._run_transaction, qry_str)
            except CypherSyntaxError as e:
                warnings.warn(
                    "Neo4j returned a Cypher syntax error. Please check your query and try again."
                )
                print(f"\nThe original error returned by Neo4j is:\n\n {e}")
                return None
            return res

    def get_graph_statistics(self):
        """Fetch statistics for the connected graph database.

        This method essentially calls APOC.meta.stats(); and formats the output.

        Returns
        -------
        dict
        Dict of statistics describing the graph database.

        Raises
        ------
        RuntimeError
        If not currently connected to a graph database or the APOC.meta
        procedures are not installed/available.
        """
        qry = "CALL apoc.meta.stats();"
        response = self.run_cypher(qry, verbose=self.verbose)
        assert len(response) == 1

        response = response[0]

        stats = {
            k: response[k]
            for k in ("nodeCount", "relCount", "labelCount", "relTypeCount")
            if k in response
        }

        return stats

    def fetch(
        self,
        field,
        operator,
        value,
        what="both",
        register_graph=True,
        negate=False,
        query_type="cypher",
        **kwargs,
    ):
        """
        Create and execute a query to retrieve nodes, edges, or both.

        Warnings
        --------
        This function is incomplete and should not be used until we can fix its
        behavior. Specifically, Neo4j's GDS library does not support non-numeric
        node or edge properties in any of its graph catalog-related subroutines.

        Parameters
        ----------
        field : str
            A property label.
        what : {'both', 'nodes', edges'}
            The type of objects to fetch from the graph database. Note that this
            functions independently from any subgraph registered in Neo4j during
            query execution - if `register_graph` is `True`, an induced subgraph
            will be registered in the database, but the components returned by this
            method call may be only the nodes or edges contained in that subgraph.
        filter : str
            'Cypher-like' filter statement, equivalent to a `WHERE` clause used in
            a Neo4j Cypher query (analogous to SQL `WHERE` clauses).
        query_type : {'cypher', 'native'}
            Whether to create a graph using a Cypher projection or a native
            projection. The 'standard' approach is to use a Cypher projection, but
            native projections can be (a.) more highly performant and (b.) easier
            for creating very large subgraphs (e.g., all nodes of several or more
            types that exist in all of ComptoxAI). See "Notes", below, for more
            information, as well as https://neo4j.com/docs/graph-data-science/current/management-ops/graph-catalog-ops/#catalog-graph-create.
        """

        raise NotImplementedError(
            "Error: GraphDB.fetch() not yet implemented - see documentation notes."
        )

        if query_type == "cypher":
            new_graph = self.build_graph_cypher_projection()
        elif query_type == "native":
            new_graph = self.build_graph_native_projection()
        else:
            raise ValueError("'query_type' must be either 'cypher' or 'native'")

        # consume results

        # (optionally) build Graph object

        # Return results to user

    def find_node(self, name=None, properties=None):
        """
        Find a single node either by name or by property filter(s).
        """
        if name:
            # search by name
            query = 'MATCH (n {{ commonName: "{0}" }}) RETURN n LIMIT 1;'.format(name)
        else:
            if not properties:
                raise ValueError(
                    "Error: Must provide a value for `name` or `properties`."
                )

        # search by properties
        # first, separate out properties with special meaning (e.g., `id`)

        # then, construct a MATCH clause suing the remaining properties
        # strings should be enclosed in
        prop_string = ", ".join(
            [
                f"{k}: '{v}'" if type(v) == str else f"{k}: {v}"
                for k, v in properties.items()
            ]
        )
        match_clause = f"MATCH (n {{ {prop_string} }})"
        # assemble the complete query

        query = f"{match_clause} RETURN n;"

        node_response = self.run_cypher(query)

        if len(node_response) < 1:
            warnings.warn("Warning: No node found matching the query you provided.")
            return False
        elif len(node_response) > 1:
            warnings.warn(
                "Warning: Multiple nodes found for query - only returning one (see `find_nodes` if you want all results)."
            )

        return node_response[0]["n"]

    def find_nodes(self, search_dict):
        """
        Find multiple nodes by node properties and/or labels.

        Parameters
        ----------
        search_dict : Dict[str, Dict[str, Union[str, int, list]]]
            Case sensitive dictionary of nodes to search for in the format of {node_type : {property : property_value(s)}}

        Returns
        -------
        Dict[str : List[Dict[str, str]]]
            Nodes found from the query in the format {node_type : [{node_property : property_value}]}

        Raises
        -------
        TypeError
            If type of search_dict is not Dict or if property is not str or if property values are not str, int, or List[Union[str, int]]

        Examples
        --------
        >>> db.find_nodes({"Chemical" : {'commonName': ["Hydroxychloroquine", "Warfarin"]}, "Gene" : {"xrefNcbiGene" : 1031, "geneSymbol" : "CDKN1A"}})
        {'Chemical': [{'commonName': 'Hydroxychloroquine',
        'synonyms': "+-|Ethanol, 2-[[4-[(7-chloro-4-quinolinyl)amino]pentyl]ethylamino]-|(.+-.)-Hydroxychloroquine|7-Chloro-4-[4-(N-ethyl-N-β-hydroxyethylamino)-1-methylbutylamino]quinoline|7-Chloro-4-[4'-[ethyl (2''-hydroxyethyl) amino]-1'-methylbutylamino]quinoline|7-Chloro-4-[4-[ethyl(2-hydroxyethyl)amino]-1-methylbutylamino]quinoline|7-Chloro-4-[5-(N-ethyl-N-2-hydroxyethylamino)-2-pentyl]aminoquinoline|Ethanol, 2-[[4-[(7-chloro-4-quinolyl)amino]pentyl]ethylamino]-|hidroxicloroquina|Hydroxychlorochin|Oxichloroquine|Oxychlorochin|Oxychloroquine|Racemic Hydroxychloroquine|5-22-10-00280|BRN 0253894|7-Chloro-4-(4-(N-ethyl-N-beta-hydroxyethylamino)-1-methylbutylamino)quinoline|7-Chloro-4-(5-(N-ethyl-N-2-hydroxyethylamino)-2-pentyl)aminoquinoline|EINECS 204-249-8|Oxichlorochinum|Hydroxychloroquinum|Idrossiclorochina|UNII-4QWG6N8QKH|(+-)-hydroxychloroquine|2-((4-((7-chloro-4-quinolyl)amino)pentyl)ethylamino)ethanol|2-(N-(4-(7-chlor-4-chinolylamino)-4-methylbutyl)ethylamino)ethanol|7-chloro-4-(4-(N-ethyl-N-beta-hydroxyethylamino)-1-methylbutylamino)quinoline|7-chloro-4-(4-(ethyl(2-hydroxyethyl)amino)-1-methylbutylamino)quinoline|7-chloro-4-[4-(N-ethyl-N-beta-hydroxyethylamino)-1-methylbutylamino]quinoline|7-chloro-4-[5-(N-ethyl-N-2-hydroxyethylamino)-2-pentyl]aminoquinoline|NSC4375|oxichlorochine",
        'xrefDrugbank': 'DB01611',
        'xrefMeSH': 'MESH:D006886',
        'xrefDTXSID': 'DTXSID8023135',
        'xrefPubchemSID': '315673741.0',
        'xrefCasRN': '118-42-3',
        'uri': 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid8023135',
        'monoisotopicMass': '335.1764402000',
        'maccs': '00000000000000000000000000000000000000000000000000000000000000000100000000000000101001110011000100101101110111010011101001100100110111110111001001011101010111101111110',
        'molFormula': 'C18H26ClN3O',
        'sMILES': 'CCN(CCO)CCCC(C)NC1=CC=NC2=CC(Cl)=CC=C12',
        'xrefPubchemCID': '3652',
        'molWeight': '335.8800000000'},
        {'commonName': 'Warfarin',
        'synonyms': "Coumadin|2H-1-Benzopyran-2-one, 4-hydroxy-3-(3-oxo-1-phenylbutyl)-|(.+-.)-Warfarin|(.+-.)-Warfarin-alcohol|(RS)-Warfarin|1-(4'-Hydroxy-3'-coumarinyl)-1-phenyl-3-butanone|3-(1'-Phenyl-2'-acetylethyl)-4-hydroxycoumarin|3-(α-Acetonylbenzyl)-4-hydroxycoumarin|3-(α-Phenyl-β-acetylethyl)-4-hydroxycoumarin|3-(α-Phenyl-β-acetylethyl)-4-hydroxy-coumarin|4-Hydroxy-3-(3-oxo-1-phenylbutyl)-2H-1-benzopyran-2-one|4-Hydroxy-3-(3-oxo-1-phenylbutyl)-2H-chromen-2-one|Athrombine-K|BENZOPYRAN(2H-1)-2-ONE, 4-HYDROXY-3-(3-OXO-1- PHENYLBUTYL)-|Brumolin|Coumafen|Coumafene|Coumaphen|Coumarin, 3-(α-acetonylbenzyl)-4-hydroxy-|Coumefene|Dethmor|DL-3-(α-Acetonylbenzyl)-4-hydroxycoumarin|Kumader|Kumatox|NSC 59813|rac-Warfarin|Ratron G|Rodafarin|Rodafarin C|Temus W|Vampirinip II|Vampirinip III|W.A.R.F. 42|WARF compound 42|warfarina|Warfarine|Zoocoumarin|5-18-04-00162|200 coumarin|Arab Rat Death|BRN 1293536|Caswell No. 903|Compound 42|Coumaphene|Coumarins|Cov-R-Tox|Dethnel|Eastern states duocide|EINECS 201-377-6|EPA Pesticide Chemical Code 086002|Frass-ratron|4-Hydroxy-3-(3-oxo-1-phenylbutyl)coumarin|Kypfarin|Liqua-tox|Maag rattentod cum|Mar-frin|Martin's mar-frin|Maveran|Mouse pak|3-(alpha-Phenyl-beta-acetylethyl)-4-hydroxycoumarin|Rat & mice bait|Rat-o-cide #2|Rat-Gard|Rat-B-gon|Rat-Kill|Rat-Mix|Rat-ola|Ratorex|Ratoxin|Rats-No-More|Ratten-koederrohr|Rattenstreupulver Neu Schacht|Rattenstreupulver new schacht|Rattentraenke|Rat-Trol|Rattunal|Rat-A-way|RCRA waste number P001|Ro-Deth|Rodex blox|Rough & ready mouse mix|Solfarin|Spray-trol brand roden-trol|Tox-Hid|Twin light rat away|Warfarat|Warfarin Q|Warfarin plus|DL-3-(alpha-Acetonylbenzyl)-4-hydroxycoumarin|Dicusat E|(Phenyl-1 acetyl-2 ethyl) 3-hydroxy-4 coumarine|3-(alpha-Phenyl-beta-acetylaethyl)-4-hydroxycumarin|4-Hydroxy-3-(3-oxo-1-fenyl-butyl) cumarine|4-Hydroxy-3-(3-oxo-1-phenyl-butyl)-cumarin|4-Idrossi-3-(3-oxo-1-fenil-butil)-cumarine|Warfarinum|UNII-5Q7ZVV76EI",
        'xrefDrugbank': 'DB00682',
        'xrefMeSH': 'MESH:D014859',
        'xrefDTXSID': 'DTXSID5023742',
        'xrefPubchemSID': '315674265.0',
        'uri': 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid5023742',
        'xrefCasRN': '81-81-2',
        'monoisotopicMass': '308.1048589950',
        'maccs': '00000000000000000000000000000000000000000000000000000000010000000000000000000000000000000101000000100100010000000101000000010101000010001101100111100010101101011011110',
        'molFormula': 'C19H16O4',
        'sMILES': 'CC(=O)CC(C1=CC=CC=C1)C1=C(O)C2=CC=CC=C2OC1=O',
        'xrefAOPWikiStressorID': 195,
        'xrefPubchemCID': '54678486',
        'molWeight': '308.3330000000'}],
        'Gene': [{'typeOfGene': 'protein-coding',
        'commonName': 'cyclin dependent kinase inhibitor 2C',
        'xrefOMIM': '603369',
        'xrefHGNC': '1789',
        'xrefEnsembl': 'ENSG00000123080',
        'geneSymbol': 'CDKN2C',
        'uri': 'http://jdr.bio/ontologies/comptox.owl#gene_cdkn2c',
        'xrefNcbiGene': 1031},
        {'typeOfGene': 'protein-coding',
        'commonName': 'cyclin dependent kinase inhibitor 1A',
        'xrefOMIM': '116899',
        'xrefHGNC': '1784',
        'xrefEnsembl': 'ENSG00000124762',
        'geneSymbol': 'CDKN1A',
        'uri': 'http://jdr.bio/ontologies/comptox.owl#gene_cdkn1a',
        'xrefNcbiGene': 1026}]}
        """

        result = dict()

        if not isinstance(search_dict, Dict):
            raise TypeError("search_dict should be a dictionary.")

        for node_type, property_dict in search_dict.items():

            if not isinstance(node_type, str):
                raise TypeError("node_type should be str.")
            property_match_substrings = []

            for property, property_value in property_dict.items():
                if isinstance(property_value, int):
                    property_match_substrings.append(
                        f"((n.{property}) = {property_value})"
                    )
                elif isinstance(property_value, str):
                    property_match_substrings.append(
                        f"((n.{property}) = '{property_value}')"
                    )
                elif isinstance(property_value, list):
                    property_match_substrings.append(
                        f"((n.{property}) IN {property_value})"
                    )
                else:
                    raise TypeError(
                        "Property values should be str, int, or list of str or int."
                    )

            match_substring = " OR ".join(property_match_substrings)

            query = f"MATCH (n:{node_type}) WHERE {match_substring} RETURN n"

            print(query)
            response = self.run_cypher(query)

            response = [node["n"] for node in response]

            result[node_type] = response

        return result

    def find_relationships(self):
        """
        Find relationships by subject/object nodes and/or relationship type.
        """
        pass

    def build_graph_native_projection(
        self, graph_name, node_types, relationship_types="all", config_dict=None
    ):
        """
        Create a new graph in the Neo4j Graph Catalog via a native projection.

        Parameters
        ----------
        graph_name : str
        A (string) name for identifying the new graph. If a graph already exists
        with this name, a ValueError will be raised.
        node_proj : str, list of str, or dict of
        Node projection for the new graph. This can be either a single node
        label, a list of node labels, or a node projection

        Notes
        -----

        ComptoxAI is meant to hide the implementation and usage details of graph
        databases from the user, but some advanced features do expose the syntax
        used in the Neo4j and MongoDB internals. This is especially true when
        building graph projections in the graph catalog. The following components

        NODE PROJECTIONS:

        *(corresponding argument: `node_proj`)*

        Node projections take the following format:

        .. code-block::

            {
                <node-label-1>: {
                    label: <neo4j-label>,
                    properties: <node-property-mappings>
                },
                <node-label-2>: {
                    label: <neo4j-label>,
                    properties: <node-property-mappings>
                },
                // ...
                <node-label-n>: {
                    label: <neo4j-label>,
                    properties: <node-property-mappings>
                }
            }

        where ``node-label-i`` is a name for a node label in the projected graph
        (it can be the same as or different from the label already in neo4j),
        ``neo4j-label`` is a node label to match against in the graph database, and
        ``node-property-mappings`` are filters against Neo4j node properties, as
        defined below.

        NODE PROPERTY MAPPINGS:

        RELATIONSHIP PROJECTIONS:

        Examples
        --------
        >>> g = GraphDB()
        >>> g.build_graph_native_projection(
        graph_name = "g1",
        node_proj = ['Gene', 'StructuralEntity'],
        relationship_proj = "*"
        )
        >>>
        """

        create_graph_query_template = """
        CALL gds.graph.create({0},{1},{2}{3})
        YIELD graphName, nodeCount, relationshipCount, createMillis;
        """[
            1:-1
        ]

        graph_name_str = "'{0}'".format(graph_name)

        node_proj_str = self._make_node_projection_str(node_types)

        # relationship_proj_str = "'{0}'".format(relationship_proj)
        relationship_proj_str = self._make_node_projection_str(relationship_types)

        # config_dict_str = str(config_dict)
        if config_dict is None:
            config_dict_str = ""
        else:
            config_dict_str = ", {0}".format(str(config_dict))

        create_graph_query = create_graph_query_template.format(
            graph_name_str, node_proj_str, relationship_proj_str, config_dict_str
        )

        if self.verbose:
            print(create_graph_query)

        res = self.run_cypher(create_graph_query)

        return res

    def build_graph_cypher_projection(
        self, graph_name, node_query, relationship_query, config_dict=None
    ):
        """
        Create a new graph in the Neo4j Graph Catalog via a Cypher projection.

        Examples
        --------
        >>> g = GraphDB()
        >>> g.build_graph_cypher_projection(...)
        >>>
        """

        create_graph_query_template = """
        CALL gds.graph.create.cypher({0},{1},{2}{3})
        YIELD graphName, nodeCount, relationshipCount, createMillis;
        """[
            1:-1
        ]

        graph_name_str = "'{0}'".format(graph_name)
        node_query_str = "'{0}'".format(node_query)
        relationship_query_str = "'{0}'".format(relationship_query)

        if config_dict is None:
            config_dict_str = ""
        else:
            config_dict_str = ", configuration: {0}".format(str(config_dict))

        create_graph_query = create_graph_query_template.format(
            graph_name_str, node_query_str, relationship_query_str, config_dict_str
        )

        if self.verbose:
            print(create_graph_query)

        res = self.run_cypher(create_graph_query)

        return res

    def _make_node_projection_str(self, node_proj_arg):
        if isinstance(node_proj_arg, str):
            # We need to wrap any string in double quotes
            if node_proj_arg == "all":
                return '"*"'
            # e.g., 'Chemical'
            return f'"{node_proj_arg}"'
        elif isinstance(node_proj_arg, list):
            # e.g., ['Chemical', 'Disease']
            return "{0}".format(str(node_proj_arg))
        elif isinstance(node_proj_arg, dict):
            return

    def _make_rel_projection_str(self, rel_proj_arg):
        raise NotImplementedError

    def fetch_nodes(self, node_type, property, values):
        """
        Fetch nodes by node property value.

        Allows users to filter by a single node type (i.e., ontology class).

        Parameters
        ----------
        node_type : str
        Node type on which to filter all results. Can speed up queries
        significantly.
        property : str
        Node property to match against.
        values : str or list
        Value or list of values on which to match `property`.

        Returns
        -------
        list of dict
        Each element in the list corresponds to a single node. If no matches are
        found in the database, an empty list will be returned.
        """
        raise NotImplementedError

    def fetch_chemical_list(self, list_name):
        """
        Fetch all chemicals that are members of a chemical list.

        Parameters
        ----------
        list_name : str
        Name (or acronym) corresponding to a Chemical List in ComptoxAI's graph
        database.

        Returns
        -------
        list_data : dict
        Metadata corresponding to the matched list
        chemicals : list of dict
        Chemical nodes that are members of the chemical list
        """
        res = self.run_cypher(
            f'MATCH (l:ChemicalList {{ listAcronym: "{list_name}" }})-[:LISTINCLUDESCHEMICAL]->(c:Chemical) RETURN l, c'
        )

        return (res[0]["l"], [r["c"] for r in res])

    def fetch_node_type(self, node_label):
        """
        Fetch an entire class of nodes from the Neo4j graph database.

        Parameters
        ----------
        node_label : str
        Node label corresponding to a class of entities in the database.

        Returns
        -------
        generator of dict

        Warnings
        --------
        Since many entities may be members of a single class, users are cautioned
        that this method may take a very long time to run and/or be very demanding
        on computing resources.
        """

        res = self.run_cypher(f"MATCH (n:{node_label}) RETURN n;")

        return (r["n"] for r in res)

    def fetch_relationships(self, relationship_type, from_label, to_label):
        """
        Fetch edges (relationships) from the Neo4j graph database.
        """

        res = self.run_cypher(
            f"MATCH (s:{from_label})-[r:{relationship_type}]->(o:{to_label}) RETURN s, r, o;"
        )

        return ((r["r"][0]["uri"], r["r"][1], r["r"][2]["uri"]) for r in res)

    def get_metagraph(self):
        """
        Examine the graph and construct a metagraph, which describes all of the
        node types and relationship types in the overall graph database.

        Notes
        -----
        We currently don't run this upon GraphDB instantiation, but it may be
        prudent to start doing that at some point in the future. It's not an
        extremely quick operation, but it's also not prohibitively slow.
        """

        meta = self.run_cypher("CALL apoc.meta.graph();")[0]
        node_labels = []
        for n in meta["nodes"]:
            node_labels.append(n["name"])

        node_labels = [n["name"] for n in meta["nodes"]]
        node_label_counts = dict([(n["name"], n["count"]) for n in meta["nodes"]])

        rel_types = []
        rel_path_schema = dict()
        for r in meta["relationships"]:
            if r[1] not in rel_types:
                rel_types.append(r[1])
                rel_path_schema[r[1]] = []

        rel_path_schema[r[1]].append({"from": r[0]["name"], "to": r[2]["name"]})

        metagraph = Metagraph(
            node_labels=node_labels,
            node_label_counts=node_label_counts,
            relationship_types=rel_types,
            relationship_path_schema=rel_path_schema,
        )

        return metagraph

    def list_existing_graphs(self):
        """
        Fetch a list of projected subgraphs stored in the GDS graph catalog.

        Returns
        -------
        list
        A list of graphs in the GDS graph catalog. If no graphs exist, this will
        be the empty list ``[]``.
        """
        graphs = self.run_cypher("CALL gds.graph.list();")
        if self.verbose:
            if len(graphs) == 0:
                print("Graph catalog is currently empty.")
            else:
                print(
                    "Number of graphs currently in GDS graph catalog: {0}".format(
                        len(graphs)
                    )
                )
        return graphs

    def drop_existing_graph(self, graph_name):
        """
        Delete a single graph from the GDS graph catalog by graph name.

        Parameters
        ----------
        graph_name : str
        A name of a graph, corresponding to the `'graphName'` field in the
        graph's entry within the GDS graph catalog.

        Returns
        -------
        dict
        A dict object describing the graph that was dropped as a result of
        calling this method. The dict follows the same format as one of the list
        elements returned by calling `list_current_graphs()`.
        """
        try:
            res = self.run_cypher('CALL gds.graph.drop("{0}")'.format(graph_name))
            return res[0]
        except ClientError:
            if self.verbose:
                print("Error: Graph {0} does not exist.".format(graph_name))
            return None

    def drop_all_existing_graphs(self):
        """
        Delete all graphs currently stored in the GDS graph catalog.

        Returns
        -------
        list
        A list of dicts describing the graphs that were dropped as a result of
        calling this method. The dicts  follow the same format as one of the list
        elements returned by calling `list_current_graphs()`.
        """
        current_graphs = self.list_existing_graphs()

        deleted_graphs = list()

        if current_graphs is None:
            if self.verbose:
                print("Warning - the graph catalog is already empty.")
        else:
            for cg in current_graphs:
                deleted_graph = self.drop_existing_graph(cg["graphName"])
                deleted_graphs.append(deleted_graph)

        return deleted_graphs

    def export_graph(self, graph_name, to="db"):
        """
        Export a graph stored in the GDS graph catalog to a set of CSV files.

        Parameters
        ----------
        graph_name : str
            A name of a graph, corresponding to the `'graphName'` field in the
            graph's entry within the GDS graph catalog.
        """
        if to == "csv":
            res = self.run_cypher(
                f"CALL gds.beta.graph.export('{graph_name}', {{exportName: '{graph_name}'}})"
            )
        elif to == "db":
            res = self.run_cypher(
                f"CALL gds.graph.export('{graph_name}', {{dbName: '{graph_name}'}});"
            )
        return res

    def stream_named_graph(self, graph_name):
        """
        Stream a named GDS graph into Python for further processing.

        Parameters
        ----------
        graph_name : str
            A name of a graph in the GDS catalog.
        """
        self.exporter.stream_subgraph

    # TODO: Recycle this code to send graphs to DGL instead of Pytorch Geometric
    # def to_pytorch(self, graph_name, node_list):
    #   """
    #   Construct dataset from exported graph to be used by PyTorch Geometric.

    #   Parameters
    #   ----------
    #   graph_name : str
    #     A name of a graph, corresponding to the `'graphName'` field in the
    #     graph's entry within the GDS graph catalog.
    #   """
    #   dir_abspath = os.path.join(os.getcwd(), 'comptox_ai/db/exports', f"{graph_name}")

    #   ## create dataframe containing all nodes
    #   node_df = pd.DataFrame()
    #   for node in node_list:
    #     node_files = glob.glob(f"{dir_abspath}/nodes_{node}_[0-9].csv")
    #     curr_df = pd.concat([pd.read_csv(fp, names=['id'], index_col=False) for fp in node_files])
    #     curr_df.insert(loc=1, column='type', value=f"{node}")
    #     node_df = pd.concat([node_df, curr_df])

    #   ## map node IDs to indices
    #   node_indices = dict(zip(node_df['id'].to_list(), range(len(node_df['id']))))
    #   node_df['index'] = node_df['id'].map(node_indices)

    #   ## convert node type to one hot encoded values
    #   node_df['type_encoded'] = LabelEncoder().fit_transform(node_df['type'])
    #   ohe = OneHotEncoder(sparse=False).fit_transform(node_df['type_encoded'].values.reshape(len(node_df), 1))
    #   x = torch.LongTensor(ohe)

    #   ## create dataframe containing all edges
    #   edge_files = glob.glob(f"{dir_abspath}/relationships_*_[0-9].csv")
    #   edge_df = pd.concat([pd.read_csv(fp, names=['start_id', 'end_id'], index_col=False) for fp in edge_files])

    #   ## map edges to indices
    #   edge_df['start_index'] = edge_df['start_id'].map(node_indices)
    #   edge_df['end_index'] = edge_df['end_id'].map(node_indices)
    #   edge_index = torch.tensor([edge_df['start_index'].to_numpy(), edge_df['end_index'].to_numpy()], dtype=torch.long)

    #   ## create torch_geometric data object
    #   data = Data(x=x, edge_index=edge_index)
    #   data.train_mask = data.val_mask = data.test_mask = data.y = None

    #   return data

    def convert_ids(self, node_type, from_id, to_id, ids):
        """
        Produce a mapping of IDs for a given node type from one terminology /
        database to another.

        Parameters
        ----------
        node_type : str
            Node type of the entities.
        from_id : str
        to_id : str
        ids : list of str

        Returns
        -------
        Dict[str, str]
            Dictionary of from_id : to_id pairs.
        """
        res = self.run_cypher(
            f"""
            MATCH (n:{node_type})
            WHERE n.{from_id} IN {ids}
            RETURN n.{from_id} as from_id, n.{to_id} AS to_id;
        """
        )

        id_dict = {node["from_id"]: node["to_id"] for node in res}

        return id_dict

    def find_shortest_paths(self, node1, node2, cleaned=True):
        """
        Parameters
        ----------
        node1 : comptox
        """
