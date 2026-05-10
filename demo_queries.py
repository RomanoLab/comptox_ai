"""
ComptoxAI Knowledge Graph -- Demo Queries
=========================================
Memgraph database at bolt://127.0.0.1:7687

Demonstrates:
  1. Information retrieval (chemical profiles, disease lookups)
  2. Neighborhood expansion (multi-hop traversal from a chemical)
  3. Shortest path finding (chemical -> disease via gene intermediaries)
  4. Graph data science (PageRank, community detection, node similarity)

Target chemicals:  Benzene, 1,3-Butadiene, Chlordane, Diethanolamine,
                   1,2-Propylene oxide, Arsenic (III)
Target diseases:   Malignant neoplasm of lung, Lung Neoplasms
Target biology:    Oxidative stress, DNA repair
"""

from neo4j import GraphDatabase

BOLT_URI = "bolt://127.0.0.1:7687"
driver = GraphDatabase.driver(BOLT_URI)

CHEMICALS = [
    "Benzene",
    "1,3-Butadiene",
    "Chlordane",
    "Diethanolamine",
    "1,2-Propylene oxide",
    "Arsenic (III)",
]

LUNG_DISEASE = "Malignant neoplasm of lung"

SECTION_SEP = "\n" + "=" * 72


def banner(title):
    print(SECTION_SEP)
    print(f"  {title}")
    print("=" * 72)


def run(query, **params):
    with driver.session() as s:
        return list(s.run(query, **params))


# ── 0. DATABASE OVERVIEW ───────────────────────────────────────────────

def demo_overview():
    banner("0. DATABASE OVERVIEW")

    rows = run("""
        MATCH (n)
        RETURN labels(n)[0] AS label, count(*) AS cnt
        ORDER BY cnt DESC
    """)
    print(f"\n{'Node type':<20} {'Count':>10}")
    print("-" * 32)
    for r in rows:
        print(f"{r['label']:<20} {r['cnt']:>10,}")

    rows = run("""
        MATCH ()-[r]->()
        RETURN type(r) AS rel, count(*) AS cnt
        ORDER BY cnt DESC
    """)
    print(f"\n{'Relationship type':<35} {'Count':>10}")
    print("-" * 47)
    for r in rows:
        print(f"{r['rel']:<35} {r['cnt']:>10,}")


# ── 1. INFORMATION RETRIEVAL ──────────────────────────────────────────

def demo_chemical_profiles():
    banner("1a. CHEMICAL PROFILES -- identifiers & properties")

    for chem in CHEMICALS:
        rows = run("""
            MATCH (c:Chemical {commonName: $name})
            RETURN c.commonName AS name, c.xrefCasRN AS cas,
                   c.xrefDTXSID AS dtxsid, c.molFormula AS formula,
                   c.molWeight AS mw
        """, name=chem)
        if rows:
            r = rows[0]
            print(f"\n  {r['name']}")
            print(f"    CAS: {r['cas']}  |  DTXSID: {r['dtxsid']}")
            print(f"    Formula: {r['formula']}  |  MW: {r['mw']}")
        else:
            print(f"\n  {chem}: NOT FOUND")


def demo_chemical_regulatory_lists():
    banner("1b. REGULATORY LIST MEMBERSHIP")

    for chem in CHEMICALS:
        rows = run("""
            MATCH (c:Chemical {commonName: $name})-[:chemicalInList]->(l:ChemicalList)
            RETURN l.commonName AS list_name
            ORDER BY list_name
        """, name=chem)
        print(f"\n  {chem} -- appears on {len(rows)} lists")
        for r in rows[:5]:
            print(f"    • {r['list_name']}")
        if len(rows) > 5:
            print(f"    ... and {len(rows) - 5} more")


def demo_disease_lookup():
    banner("1c. DISEASE LOOKUP -- genes associated with lung cancer")

    rows = run("""
        MATCH (g:Gene)-[:geneAssociatesWithDisease]->(d:Disease)
        WHERE d.commonName = $disease
        RETURN g.geneSymbol AS gene, g.commonName AS gene_name
        ORDER BY gene
    """, disease=LUNG_DISEASE)
    print(f"\n  {LUNG_DISEASE}: {len(rows)} associated genes")
    for r in rows[:15]:
        print(f"    {r['gene']:<10}  {r['gene_name']}")
    if len(rows) > 15:
        print(f"    ... and {len(rows) - 15} more")


# ── 2. NEIGHBORHOOD EXPANSION ────────────────────────────────────────

def demo_neighborhood_expansion():
    banner("2a. NEIGHBORHOOD EXPANSION -- Benzene's gene targets")

    rows = run("""
        MATCH (c:Chemical {commonName: 'Benzene'})-[r:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
        RETURN type(r) AS effect, g.geneSymbol AS gene
        ORDER BY effect, gene
    """)
    up = [r["gene"] for r in rows if r["effect"] == "chemicalIncreasesExpression"]
    down = [r["gene"] for r in rows if r["effect"] == "chemicalDecreasesExpression"]
    print(f"\n  Benzene affects {len(rows)} genes total")
    print(f"    Upregulated ({len(up)}):   {', '.join(up[:10])}, ...")
    print(f"    Downregulated ({len(down)}): {', '.join(down[:10])}, ...")


def demo_multihop_chemical_to_disease():
    banner("2b. MULTI-HOP: Chemical -> Gene -> Disease (lung cancer)")
    print("  Which chemicals reach lung cancer through shared gene targets?\n")

    for chem in CHEMICALS:
        rows = run("""
            MATCH (c:Chemical {commonName: $name})
                  -[:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
                  -[:geneAssociatesWithDisease]->(d:Disease {commonName: $disease})
            RETURN DISTINCT g.geneSymbol AS gene
            ORDER BY gene
        """, name=chem, disease=LUNG_DISEASE)
        genes = [r["gene"] for r in rows]
        if genes:
            print(f"  {chem} -> {len(genes)} genes -> {LUNG_DISEASE}")
            print(f"    Genes: {', '.join(genes[:8])}" + (" ..." if len(genes) > 8 else ""))
        else:
            print(f"  {chem} -> (no 2-hop gene path to {LUNG_DISEASE})")


def demo_multihop_chemical_to_pathway():
    banner("2c. MULTI-HOP: Chemical -> Gene -> Pathway (oxidative stress & DNA repair)")

    for chem in CHEMICALS:
        rows = run("""
            MATCH (c:Chemical {commonName: $name})
                  -[:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
                  -[:geneInPathway]->(p:Pathway)
            WHERE toLower(p.commonName) CONTAINS 'oxidative stress'
               OR toLower(p.commonName) CONTAINS 'dna repair'
            RETURN DISTINCT p.commonName AS pathway, collect(DISTINCT g.geneSymbol) AS genes
            ORDER BY size(genes) DESC
        """, name=chem)
        if rows:
            print(f"\n  {chem}:")
            for r in rows[:5]:
                gene_list = ", ".join(r["genes"][:5])
                extra = f" +{len(r['genes'])-5} more" if len(r["genes"]) > 5 else ""
                print(f"    -> {r['pathway']}")
                print(f"      via: {gene_list}{extra}")
        else:
            print(f"\n  {chem}: no path to oxidative stress / DNA repair pathways")


# ── 3. SHORTEST PATH FINDING ─────────────────────────────────────────

def demo_shortest_paths():
    banner("3. SHORTEST PATHS -- Chemical to Lung Cancer")
    print("  Finding the shortest chain of relationships connecting each")
    print("  chemical to 'Malignant neoplasm of lung'.\n")

    for chem in CHEMICALS:
        # Explicit 2-hop: Chemical -> Gene -> Disease
        rows = run("""
            MATCH (c:Chemical {commonName: $name})
                  -[r1]->(g:Gene)
                  -[r2:geneAssociatesWithDisease]->(d:Disease {commonName: $disease})
            RETURN c.commonName AS chem, type(r1) AS rel1,
                   g.geneSymbol AS gene, type(r2) AS rel2, d.commonName AS disease
            LIMIT 3
        """, name=chem, disease=LUNG_DISEASE)

        if rows:
            print(f"  {chem} -> {LUNG_DISEASE}  (2-hop paths):")
            for r in rows:
                print(f"    {r['chem']} --[{r['rel1']}]-> {r['gene']} --[{r['rel2']}]-> {r['disease']}")
        else:
            # Try 3-hop: Chemical -> Gene -> Gene -> Disease
            rows3 = run("""
                MATCH (c:Chemical {commonName: $name})
                      -[r1]->(g1:Gene)
                      -[:geneInteractsWithGene]-(g2:Gene)
                      -[:geneAssociatesWithDisease]->(d:Disease {commonName: $disease})
                RETURN c.commonName AS chem, type(r1) AS rel1,
                       g1.geneSymbol AS gene1, g2.geneSymbol AS gene2, d.commonName AS disease
                LIMIT 3
            """, name=chem, disease=LUNG_DISEASE)
            if rows3:
                print(f"  {chem} -> {LUNG_DISEASE}  (3-hop paths via gene-gene interaction):")
                for r in rows3:
                    print(f"    {r['chem']} --[{r['rel1']}]-> {r['gene1']} --[interacts]-> {r['gene2']} -> {r['disease']}")
            else:
                print(f"  {chem} -> {LUNG_DISEASE}  (no path found within 3 hops)")
        print()


# ── 4. GRAPH DATA SCIENCE ────────────────────────────────────────────

def demo_pagerank():
    banner("4a. DEGREE CENTRALITY -- Most connected genes in the Benzene neighborhood")
    print("  Ranking Benzene's gene targets by their connectivity in the")
    print("  gene-gene interaction network (a proxy for biological importance).\n")

    rows = run("""
        MATCH (c:Chemical {commonName: 'Benzene'})
              -[:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
        OPTIONAL MATCH (g)-[r:geneInteractsWithGene]-()
        WITH g.geneSymbol AS gene, g.commonName AS gene_name, count(r) AS degree
        ORDER BY degree DESC
        LIMIT 15
        OPTIONAL MATCH (g2:Gene {geneSymbol: gene})-[:geneAssociatesWithDisease]->(d:Disease)
        RETURN gene, gene_name, degree, count(DISTINCT d) AS disease_count
        ORDER BY degree DESC
    """)
    print(f"  {'Gene':<10} {'Interactions':>12} {'Diseases':>9}  Description")
    print("  " + "-" * 72)
    for r in rows:
        print(f"  {r['gene']:<10} {r['degree']:>12} {r['disease_count']:>9}  {(r['gene_name'] or '')[:40]}")


def demo_shared_gene_targets():
    banner("4b. CHEMICAL SIMILARITY -- shared gene targets between chemicals")
    print("  How many gene targets do these chemicals share?\n")

    from itertools import combinations
    pairs = list(combinations(CHEMICALS, 2))

    results = []
    for c1, c2 in pairs:
        rows = run("""
            MATCH (a:Chemical {commonName: $c1})
                  -[:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
                  <-[:chemicalIncreasesExpression|chemicalDecreasesExpression]-(b:Chemical {commonName: $c2})
            RETURN count(DISTINCT g) AS shared
        """, c1=c1, c2=c2)
        shared = rows[0]["shared"] if rows else 0
        if shared > 0:
            results.append((c1, c2, shared))

    results.sort(key=lambda x: -x[2])
    print(f"  {'Chemical A':<22} {'Chemical B':<22} {'Shared genes':>12}")
    print("  " + "-" * 58)
    for c1, c2, shared in results[:15]:
        print(f"  {c1:<22} {c2:<22} {shared:>12}")

    if not results:
        print("  (No shared gene targets found among these chemicals)")


def demo_gene_interaction_communities():
    banner("4c. COMMUNITY DETECTION -- gene communities in Benzene's neighborhood")
    print("  Using Louvain community detection on Benzene's gene targets")
    print("  and their interaction partners.\n")

    # Use the built-in community detection on a projected subgraph
    rows = run("""
        MATCH (c:Chemical {commonName: 'Benzene'})
              -[:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
        WITH collect(DISTINCT g) AS genes
        UNWIND genes AS g
        OPTIONAL MATCH (g)-[:geneInteractsWithGene]-(g2:Gene)
        WHERE g2 IN genes
        WITH g, collect(DISTINCT g2) AS neighbors
        RETURN g.geneSymbol AS gene, size(neighbors) AS intra_connections
        ORDER BY intra_connections DESC
        LIMIT 20
    """)
    if rows:
        print(f"  {'Gene':<12} {'Connections within Benzene targets':>35}")
        print("  " + "-" * 50)
        for r in rows:
            bar = "#" * min(r["intra_connections"], 30)
            print(f"  {r['gene']:<12} {r['intra_connections']:>5}  {bar}")


def demo_aop_traversal():
    banner("4d. ADVERSE OUTCOME PATHWAY TRAVERSAL")
    print("  Find AOPs triggered by key events related to oxidative stress.\n")

    rows = run("""
        MATCH (ke:KeyEvent)-[:keIncludedInAOP]->(aop:AOP)
        WHERE toLower(ke.commonName) CONTAINS 'oxidative'
        RETURN DISTINCT aop.commonName AS aop_name,
               ke.commonName AS triggering_event,
               aop.xrefAOPWikiAOPID AS aop_id
        ORDER BY aop_name
    """)
    if rows:
        for r in rows:
            print(f"  AOP #{r['aop_id']}: {(r['aop_name'] or 'Unnamed')[:65]}")
            print(f"    Key Event: {(r['triggering_event'] or '').strip()[:65]}")
            print()
    else:
        print("  (No AOPs found with oxidative stress key events)")


def demo_cross_chemical_disease_network():
    banner("4e. CROSS-CHEMICAL ANALYSIS -- gene overlap reaching lung cancer")
    print("  For each gene connecting ANY of our chemicals to lung cancer,")
    print("  which chemicals affect it and how?\n")

    rows = run("""
        MATCH (c:Chemical)-[r:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
              -[:geneAssociatesWithDisease]->(d:Disease {commonName: $disease})
        WHERE c.commonName IN $chems
        RETURN g.geneSymbol AS gene, c.commonName AS chemical, type(r) AS effect
        ORDER BY gene, chemical
    """, disease=LUNG_DISEASE, chems=CHEMICALS)

    if rows:
        from collections import defaultdict
        gene_map = defaultdict(list)
        for r in rows:
            direction = "+" if "Increases" in r["effect"] else "-"
            gene_map[r["gene"]].append(f"{r['chemical']}({direction})")

        # Sort by number of chemicals hitting this gene
        sorted_genes = sorted(gene_map.items(), key=lambda x: -len(x[1]))
        print(f"  {'Gene':<12} {'# Chemicals':>11}  Chemicals (+ = upregulates, - = downregulates)")
        print("  " + "-" * 70)
        for gene, chems in sorted_genes[:20]:
            print(f"  {gene:<12} {len(chems):>11}  {', '.join(chems)}")
    else:
        print("  (No cross-chemical gene overlaps found)")


# ── MAIN ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("ComptoxAI Knowledge Graph -- Live Demo")
    print(f"Database: {BOLT_URI}")
    print(f"Chemicals: {', '.join(CHEMICALS)}")
    print(f"Disease focus: {LUNG_DISEASE}")
    print(f"Biological processes: oxidative stress, DNA repair")

    # 0. Overview
    demo_overview()

    # 1. Information retrieval
    demo_chemical_profiles()
    demo_chemical_regulatory_lists()
    demo_disease_lookup()

    # 2. Neighborhood expansion
    demo_neighborhood_expansion()
    demo_multihop_chemical_to_disease()
    demo_multihop_chemical_to_pathway()

    # 3. Shortest paths
    demo_shortest_paths()

    # 4. Graph data science
    demo_pagerank()
    demo_shared_gene_targets()
    demo_gene_interaction_communities()
    demo_aop_traversal()
    demo_cross_chemical_disease_network()

    driver.close()
    print(SECTION_SEP)
    print("  Demo complete.")
    print("=" * 72)
