import os
import warnings

import pytest

from comptox_ai.db import GraphDB

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

    def test_graph_statistics(self, G):
        graph_statistics = G.get_graph_statistics()

        assert set(graph_statistics.keys()) == {
            "nodeCount",
            "relCount",
            "labelCount",
            "relTypeCount",
        }

    def test_find_node(self, G):
        warfarin_node = G.find_node(properties={"commonName": "Warfarin"})
        assert warfarin_node["commonName"] == "Warfarin"
        assert warfarin_node["xrefPubchemCID"] == "54678486"

    def test_find_nodes(self, G):
        nodes = G.find_nodes(
            {
                "Chemical": {"commonName": ["Hydroxychloroquine", "Warfarin"]},
                "Gene": {"xrefNcbiGene": 1031, "geneSymbol": "CDKN1A"},
            }
        )

        expected_output = {
            "Chemical": [
                {
                    "commonName": "Hydroxychloroquine",
                    "synonyms": "+-|Ethanol, 2-[[4-[(7-chloro-4-quinolinyl)amino]pentyl]ethylamino]-|(.+-.)-Hydroxychloroquine|7-Chloro-4-[4-(N-ethyl-N-β-hydroxyethylamino)-1-methylbutylamino]quinoline|7-Chloro-4-[4'-[ethyl (2''-hydroxyethyl) amino]-1'-methylbutylamino]quinoline|7-Chloro-4-[4-[ethyl(2-hydroxyethyl)amino]-1-methylbutylamino]quinoline|7-Chloro-4-[5-(N-ethyl-N-2-hydroxyethylamino)-2-pentyl]aminoquinoline|Ethanol, 2-[[4-[(7-chloro-4-quinolyl)amino]pentyl]ethylamino]-|hidroxicloroquina|Hydroxychlorochin|Oxichloroquine|Oxychlorochin|Oxychloroquine|Racemic Hydroxychloroquine|5-22-10-00280|BRN 0253894|7-Chloro-4-(4-(N-ethyl-N-beta-hydroxyethylamino)-1-methylbutylamino)quinoline|7-Chloro-4-(5-(N-ethyl-N-2-hydroxyethylamino)-2-pentyl)aminoquinoline|EINECS 204-249-8|Oxichlorochinum|Hydroxychloroquinum|Idrossiclorochina|UNII-4QWG6N8QKH|(+-)-hydroxychloroquine|2-((4-((7-chloro-4-quinolyl)amino)pentyl)ethylamino)ethanol|2-(N-(4-(7-chlor-4-chinolylamino)-4-methylbutyl)ethylamino)ethanol|7-chloro-4-(4-(N-ethyl-N-beta-hydroxyethylamino)-1-methylbutylamino)quinoline|7-chloro-4-(4-(ethyl(2-hydroxyethyl)amino)-1-methylbutylamino)quinoline|7-chloro-4-[4-(N-ethyl-N-beta-hydroxyethylamino)-1-methylbutylamino]quinoline|7-chloro-4-[5-(N-ethyl-N-2-hydroxyethylamino)-2-pentyl]aminoquinoline|NSC4375|oxichlorochine",
                    "xrefDrugbank": "DB01611",
                    "xrefMeSH": "MESH:D006886",
                    "xrefDTXSID": "DTXSID8023135",
                    "xrefPubchemSID": "315673741.0",
                    "xrefCasRN": "118-42-3",
                    "uri": "http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid8023135",
                    "monoisotopicMass": "335.1764402000",
                    "maccs": "00000000000000000000000000000000000000000000000000000000000000000100000000000000101001110011000100101101110111010011101001100100110111110111001001011101010111101111110",
                    "molFormula": "C18H26ClN3O",
                    "sMILES": "CCN(CCO)CCCC(C)NC1=CC=NC2=CC(Cl)=CC=C12",
                    "xrefPubchemCID": "3652",
                    "molWeight": "335.8800000000",
                },
                {
                    "commonName": "Warfarin",
                    "synonyms": "Coumadin|2H-1-Benzopyran-2-one, 4-hydroxy-3-(3-oxo-1-phenylbutyl)-|(.+-.)-Warfarin|(.+-.)-Warfarin-alcohol|(RS)-Warfarin|1-(4'-Hydroxy-3'-coumarinyl)-1-phenyl-3-butanone|3-(1'-Phenyl-2'-acetylethyl)-4-hydroxycoumarin|3-(α-Acetonylbenzyl)-4-hydroxycoumarin|3-(α-Phenyl-β-acetylethyl)-4-hydroxycoumarin|3-(α-Phenyl-β-acetylethyl)-4-hydroxy-coumarin|4-Hydroxy-3-(3-oxo-1-phenylbutyl)-2H-1-benzopyran-2-one|4-Hydroxy-3-(3-oxo-1-phenylbutyl)-2H-chromen-2-one|Athrombine-K|BENZOPYRAN(2H-1)-2-ONE, 4-HYDROXY-3-(3-OXO-1- PHENYLBUTYL)-|Brumolin|Coumafen|Coumafene|Coumaphen|Coumarin, 3-(α-acetonylbenzyl)-4-hydroxy-|Coumefene|Dethmor|DL-3-(α-Acetonylbenzyl)-4-hydroxycoumarin|Kumader|Kumatox|NSC 59813|rac-Warfarin|Ratron G|Rodafarin|Rodafarin C|Temus W|Vampirinip II|Vampirinip III|W.A.R.F. 42|WARF compound 42|warfarina|Warfarine|Zoocoumarin|5-18-04-00162|200 coumarin|Arab Rat Death|BRN 1293536|Caswell No. 903|Compound 42|Coumaphene|Coumarins|Cov-R-Tox|Dethnel|Eastern states duocide|EINECS 201-377-6|EPA Pesticide Chemical Code 086002|Frass-ratron|4-Hydroxy-3-(3-oxo-1-phenylbutyl)coumarin|Kypfarin|Liqua-tox|Maag rattentod cum|Mar-frin|Martin's mar-frin|Maveran|Mouse pak|3-(alpha-Phenyl-beta-acetylethyl)-4-hydroxycoumarin|Rat & mice bait|Rat-o-cide #2|Rat-Gard|Rat-B-gon|Rat-Kill|Rat-Mix|Rat-ola|Ratorex|Ratoxin|Rats-No-More|Ratten-koederrohr|Rattenstreupulver Neu Schacht|Rattenstreupulver new schacht|Rattentraenke|Rat-Trol|Rattunal|Rat-A-way|RCRA waste number P001|Ro-Deth|Rodex blox|Rough & ready mouse mix|Solfarin|Spray-trol brand roden-trol|Tox-Hid|Twin light rat away|Warfarat|Warfarin Q|Warfarin plus|DL-3-(alpha-Acetonylbenzyl)-4-hydroxycoumarin|Dicusat E|(Phenyl-1 acetyl-2 ethyl) 3-hydroxy-4 coumarine|3-(alpha-Phenyl-beta-acetylaethyl)-4-hydroxycumarin|4-Hydroxy-3-(3-oxo-1-fenyl-butyl) cumarine|4-Hydroxy-3-(3-oxo-1-phenyl-butyl)-cumarin|4-Idrossi-3-(3-oxo-1-fenil-butil)-cumarine|Warfarinum|UNII-5Q7ZVV76EI",
                    "xrefDrugbank": "DB00682",
                    "xrefMeSH": "MESH:D014859",
                    "xrefDTXSID": "DTXSID5023742",
                    "xrefPubchemSID": "315674265.0",
                    "uri": "http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid5023742",
                    "xrefCasRN": "81-81-2",
                    "monoisotopicMass": "308.1048589950",
                    "maccs": "00000000000000000000000000000000000000000000000000000000010000000000000000000000000000000101000000100100010000000101000000010101000010001101100111100010101101011011110",
                    "molFormula": "C19H16O4",
                    "sMILES": "CC(=O)CC(C1=CC=CC=C1)C1=C(O)C2=CC=CC=C2OC1=O",
                    "xrefAOPWikiStressorID": 195,
                    "xrefPubchemCID": "54678486",
                    "molWeight": "308.3330000000",
                },
            ],
            "Gene": [
                {
                    "typeOfGene": "protein-coding",
                    "commonName": "cyclin dependent kinase inhibitor 2C",
                    "xrefOMIM": "603369",
                    "xrefHGNC": "1789",
                    "xrefEnsembl": "ENSG00000123080",
                    "geneSymbol": "CDKN2C",
                    "uri": "http://jdr.bio/ontologies/comptox.owl#gene_cdkn2c",
                    "xrefNcbiGene": 1031,
                },
                {
                    "typeOfGene": "protein-coding",
                    "commonName": "cyclin dependent kinase inhibitor 1A",
                    "xrefOMIM": "116899",
                    "xrefHGNC": "1784",
                    "xrefEnsembl": "ENSG00000124762",
                    "geneSymbol": "CDKN1A",
                    "uri": "http://jdr.bio/ontologies/comptox.owl#gene_cdkn1a",
                    "xrefNcbiGene": 1026,
                },
            ],
        }

        assert nodes == expected_output

    def test_dsstox_to_casrn_converts(self, G):
        converted_ids = G.convert_ids(
            node_type="Chemical",
            from_id="xrefDTXSID",
            to_id="xrefCasRN",
            ids=["DTXSID40857898", "DTXSID40858749"],
        )

        # Hopefully DSSTOX -> CASRN mappings are stable between versions...
        assert converted_ids == {
            "DTXSID40857898": "69313-80-0",
            "DTXSID40858749": "4559-79-9",
        }

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
