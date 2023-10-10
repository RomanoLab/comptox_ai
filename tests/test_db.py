from comptox_ai.db import GraphDB

import pytest
import warnings
import os
from pprint import pprint, pformat
import sys

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


# Module-level scope so we don't keep reconnecting with every test
@pytest.fixture(scope="module")
def G():
    G = GraphDB(verbose=True, hostname="neo4j.comptox.ai")
    return G


class TestGraphDB(object):

    def test_neo4j_connection_does_exist(self, G):
        with warnings.catch_warnings():
            # Supress the ExperimentalWarning for now
            warnings.simplefilter("ignore")
            assert G._driver.verify_connectivity() is not None

    def test_cypher_query_does_run(self, G):
        x = G.run_cypher("RETURN 'hello';")
        assert len(x[0]) > 0

    def test_dsstox_to_casrn_converts(self, G):
        converted_ids = G.convert_ids(
            node_type='Chemical',
            from_id='xrefDTXSID',
            to_id='xrefCasRN',
            ids=['DTXSID40857898', 'DTXSID40858749']
        )

        # Hopefully DSSTOX -> CASRN mappings are stable between versions...
        assert converted_ids == ['69313-80-0', '4559-79-9']

    def test_fetch_chemical_one_chemical_by_commonName(self, G):
        expected_chemicals = {
            'commonName': 'Trisodium hydrogen diphosphate',
            'maccs': '0000000000000000000000000000100000100000000100011000000000000000000010000000000000000000100000000000010001000001000000000001010001000001001100000101000000000010000101',
            'sMILES': '[Na+].[Na+].[Na+].OP([O-])(=O)OP([O-])([O-])=O',
            'synonyms': 'Trisodium diphosphate|Diphosphoric acid, trisodium salt|Diphosphoric acid, sodium salt (1:3)',
            'uri': 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid70872534',
            'xrefCasRN': '14691-80-6',
            'xrefDTXSID': 'DTXSID70872534',
            'xrefPubchemCID': '161081',
            'xrefPubchemSID': '316388586'
        }

        # Perform the fetch operation
        fetched_chemicals = G.fetch_chemicals(
            property='commonName',
            values='Trisodium hydrogen diphosphate'
        )

        # Assert that the result is a list
        assert isinstance(fetched_chemicals, list)

        # Assert that the result is not empty
        assert fetched_chemicals

        # Assert that the expected chemical data is in the result
        assert expected_chemicals in fetched_chemicals

    def test_fetch_chemical_two_chemicals_by_CasRN(self, G):
        expected_chemicals = [
            {
                'commonName': 'Silidianin',
                'maccs': '0000000000000000001000000000000000000000000000000100100010000100000000010001000000100000111010010110000010001001100000010010111000100001101100111100010111001011011110',
                'sMILES': 'COC1=C(O)C=CC(=C1)[C@@H]1[C@H]2CO[C@]3(O)[C@H]2C(=C[C@H]1C3=O)[C@H]1OC2=C(C(O)=CC(O)=C2)C(=O)[C@@H]1O',
                'synonyms': 'Silydianin|3,6-Methanobenzofuran-7(6H)-one, 4-[(2R,3R)-3,4-dihydro-3,5,7-trihydroxy-4-oxo-2H-1-benzopyran-2-yl]-2,3,3a,7a-tetrahydro-7a-hydroxy-8-(4-hydroxy-3-methoxyphenyl)-, (3R,3aR,6R,7aR,8R)-|EINECS 249-848-5|Silidianina|Silidianine|Silidianinum|UNII-7P89L7W179',
                'uri': 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid70858696',
                'xrefCasRN': '29782-68-1',
                'xrefDTXSID': 'DTXSID70858696',
                'xrefMeSH': 'MESH:C015505',
                'xrefPubchemCID': '11982272',
                'xrefPubchemSID': '316388226',
            },
            {
                'commonName': '3-Chloro-6-fluoro-2H-indazole',
                'maccs': '0000000000000000000000000000000000000000010000000001000000000000100010000000000100100010000001010000001010100000000000011001000000000100100001000000001000010000111010',
                'sMILES': 'FC1=CC2=NNC(Cl)=C2C=C1',
                'synonyms': '',
                'uri': 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid80857655',
                'xrefCasRN': '1243360-12-4',
                'xrefDTXSID': 'DTXSID80857655',
                'xrefPubchemCID': '71748561',
                'xrefPubchemSID': '316387196',
            }
        ]

        # Perform the fetch operation
        fetched_chemicals = G.fetch_chemicals(
            property='xrefCasRN',
            values=['29782-68-1', '1243360-12-4']
        )

        # Assert that the result is a list
        assert isinstance(fetched_chemicals,
                          list), f"Result is not a list: {fetched_chemicals}"

        # Assert that the result is not empty
        assert fetched_chemicals, f"Result is empty: {fetched_chemicals}"

        # Define the path to the test_results directory
        test_results_dir = "./test_results"

        # Ensure the directory exists; create it if it doesn't
        os.makedirs(test_results_dir, exist_ok=True)

        # Specify the result file name with the full path
        result_filename = os.path.join(
            test_results_dir, "test_fetch_chemical_two_chemicals_by_CasRN.txt")

        # Open the result file for writing
        with open(result_filename, "w") as result_file:
            # Redirect print output to the result file
            original_stdout = sys.stdout
            sys.stdout = result_file

            # Print the result to the file
            print(fetched_chemicals)

            # Compare the expected_chemicals with res
            for i, (expected, fetched) in enumerate(zip(expected_chemicals, fetched_chemicals), start=1):
                for key in expected.keys():
                    if expected[key] != fetched[key]:
                        print(f"Difference in chemical {i}, key: {key}")
                        print(f"Expected: {expected[key]}")
                        print(f"Result: {fetched[key]}")
                        print()

            # Restore the original stdout
            sys.stdout = original_stdout

        # Check if each expected chemical is in fetched_chemicals
        for expected in expected_chemicals:
            assert (
                expected in fetched_chemicals
            ), f"Expected chemical not found in result: {expected}"

    # THE FOLLOWING ARE OBSOLETE UNTIL GDS GRAPH CATALOG IS COMPATIBLE WITH
    # def test_raise_when_config_file_not_found(self):
    #   with pytest.raises(RuntimeError) as e_info:
    #     G_pre = GraphDB(config_file="/dev/null")

    # def test_raise_when_bad_config_given(self):
    #   bad_config_file = os.path.join(TEST_DIR, 'badconfig.txt')
    #   with pytest.raises(RuntimeError) as e_info:
    #     G_pre = GraphDB(config_file=bad_config_file)

    # def test_raise_when_database_unavailable(self):
    #   unavail_config_file = os.path.join(TEST_DIR, 'unavailconfig.txt')
    #   with pytest.raises(RuntimeError) as e_info:
    #     G_pre = GraphDB(config_file=unavail_config_file)
    # STRING PROPERTIES:

    # def test_gds_list_existing_graphs(self, G):
    #   x = G.list_existing_graphs()
    #   assert isinstance(x, list)

    # def test_gds_delete_existing_graphs(self, G):
    #   x = G.drop_all_existing_graphs()

    #   y = G.list_existing_graphs()

    #   assert len(y) is 0

    # def test_gds_create_graph_native_projection(self, G):
    #   newgraph1 = G.build_graph_native_projection(
    #     "testgraph1",
    #     ["Chemical", "Disease"],
    #     "*",
    #   )

    #   def test_gds_new_num_graphs_is_1(self, G):
    #     y = G.list_existing_graphs()
    #     assert len(y) == 1

    # def test_gds_delete_graph_native_projection(self, G):
    #   x = G.drop_existing_graph("testgraph1")
    #   assert x['graphName'] == "testgraph1"

    # def test_gds_create_graph_cypher_projection(self, G):
    #   newgraph2 = G.build_graph_cypher_projection(
    #     "testgraph2",
    #     "MATCH (n) WHERE n:Chemical OR n:Disease RETURN id(n) AS id, labels(n) AS labels",
    #     "MATCH (c:Chemical)-->(d:Disease) RETURN id(c) as source, id(d) as target"
    #   )

    # def test_gds_delete_graph_cypher_projection(self, G):
    #   # Note: this test will fail if the previous test fails
    #   x = G.drop_existing_graph("testgraph2")
    #   assert x['graphName'] == "testgraph2"
