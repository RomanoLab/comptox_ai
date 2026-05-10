# ComptoxAI Demo Queries for Memgraph Lab

Copy-paste these Cypher queries into the Memgraph Lab browser.
Queries that return graph patterns (nodes + relationships) will render
as interactive visual graphs; tabular queries render as tables.

Target chemicals: Benzene, 1,3-Butadiene, Chlordane, Diethanolamine,
1,2-Propylene oxide, Arsenic (III).
Swap any chemical name in the queries below to explore others.

---

## 0. Database overview

### Node counts by type

```cypher
MATCH (n)
RETURN labels(n)[0] AS label, count(*) AS cnt
ORDER BY cnt DESC;
```

### Relationship counts by type

```cypher
MATCH ()-[r]->()
RETURN type(r) AS rel, count(*) AS cnt
ORDER BY cnt DESC;
```

---

## 1. Information retrieval

### 1a. Chemical profile -- look up a single chemical

Returns identifiers (CAS, DTXSID) and properties for a chemical.

```cypher
MATCH (c:Chemical {commonName: 'Benzene'})
RETURN c;
```

### 1b. Regulatory list membership

Shows the chemical node and all ChemicalList nodes it belongs to.
Renders as a star graph in the browser.

```cypher
MATCH (c:Chemical {commonName: 'Benzene'})-[r:chemicalInList]->(l:ChemicalList)
RETURN c, r, l;
```

### 1c. Genes associated with lung cancer

Returns the disease node surrounded by its associated genes.

```cypher
MATCH (g:Gene)-[r:geneAssociatesWithDisease]->(d:Disease {commonName: 'Malignant neoplasm of lung'})
RETURN g, r, d;
```

---

## 2. Neighborhood expansion

### 2a. Benzene's gene targets (expression changes)

All genes whose expression Benzene increases or decreases.
Renders as a large star graph -- upregulation and downregulation
edges are visually distinguishable by relationship type.

```cypher
MATCH (c:Chemical {commonName: 'Benzene'})
      -[r:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
RETURN c, r, g;
```

### 2b. Multi-hop: Chemical -> Gene -> Disease (lung cancer)

Two-hop path from Benzene through intermediate genes to lung cancer.
Each path is a chain: Chemical -- Gene -- Disease.

```cypher
MATCH (c:Chemical {commonName: 'Benzene'})
      -[r1:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
      -[r2:geneAssociatesWithDisease]->(d:Disease {commonName: 'Malignant neoplasm of lung'})
RETURN c, r1, g, r2, d;
```

### 2c. Multi-hop: Chemical -> Gene -> Pathway (oxidative stress & DNA repair)

Connects Benzene to oxidative stress and DNA repair pathways via
intermediate genes. Shows the biological mechanism chain.

```cypher
MATCH (c:Chemical {commonName: 'Benzene'})
      -[r1:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
      -[r2:geneInPathway]->(p:Pathway)
WHERE toLower(p.commonName) CONTAINS 'oxidative stress'
   OR toLower(p.commonName) CONTAINS 'dna repair'
RETURN c, r1, g, r2, p;
```

---

## 3. Shortest path finding

### 3a. Shortest path: Benzene to lung cancer (2-hop)

Explicit 2-hop paths from Benzene to lung cancer via any relationship
to a gene, then gene-disease association. Shows the top 5 shortest chains.

```cypher
MATCH p = (c:Chemical {commonName: 'Benzene'})
          -[r1]->(g:Gene)
          -[r2:geneAssociatesWithDisease]->(d:Disease {commonName: 'Malignant neoplasm of lung'})
RETURN p
LIMIT 5;
```

### 3b. Shortest path: Diethanolamine to lung cancer (2-hop)

```cypher
MATCH p = (c:Chemical {commonName: 'Diethanolamine'})
          -[r1]->(g:Gene)
          -[r2:geneAssociatesWithDisease]->(d:Disease {commonName: 'Malignant neoplasm of lung'})
RETURN p
LIMIT 5;
```

### 3c. Longer paths via gene-gene interaction (3-hop)

For chemicals without a direct 2-hop path to lung cancer, traverse
through gene-gene interactions to find a 3-hop route.

```cypher
MATCH p = (c:Chemical {commonName: 'Chlordane'})
          -[r1]->(g1:Gene)
          -[r2:geneInteractsWithGene]-(g2:Gene)
          -[r3:geneAssociatesWithDisease]->(d:Disease {commonName: 'Malignant neoplasm of lung'})
RETURN p
LIMIT 5;
```

---

## 4. Graph data science

### 4a. Degree centrality -- most connected Benzene gene targets

Ranks Benzene's gene targets by how many gene-gene interactions they
participate in (a proxy for biological importance / hub status).

```cypher
MATCH (c:Chemical {commonName: 'Benzene'})
      -[:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
OPTIONAL MATCH (g)-[r:geneInteractsWithGene]-()
WITH g.geneSymbol AS gene, g.commonName AS gene_name, count(r) AS degree
ORDER BY degree DESC
LIMIT 15
OPTIONAL MATCH (g2:Gene {geneSymbol: gene})-[:geneAssociatesWithDisease]->(d:Disease)
RETURN gene, gene_name, degree, count(DISTINCT d) AS disease_count
ORDER BY degree DESC;
```

### 4b. Chemical similarity -- shared gene targets (Benzene vs Diethanolamine)

Visualizes genes that are targeted by both chemicals simultaneously.
Each shared gene has edges coming from both chemical nodes.

```cypher
MATCH (a:Chemical {commonName: 'Benzene'})
      -[r1:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
      <-[r2:chemicalIncreasesExpression|chemicalDecreasesExpression]-(b:Chemical {commonName: 'Diethanolamine'})
RETURN a, r1, g, r2, b;
```

### 4c. Intra-community connectivity -- Benzene gene target interaction network

Shows how Benzene's gene targets interact with each other (edges within
the Benzene-affected gene set). Reveals tightly connected gene clusters.

```cypher
MATCH (c:Chemical {commonName: 'Benzene'})
      -[:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
WITH collect(DISTINCT g) AS genes
UNWIND genes AS g
MATCH (g)-[r:geneInteractsWithGene]-(g2:Gene)
WHERE g2 IN genes
RETURN g, r, g2;
```

### 4d. Adverse Outcome Pathway traversal -- oxidative stress AOPs (full structure)

Finds all AOPs that include key events related to oxidative stress,
then shows the complete AOP structure: the AOP node, all of its member
key events, and the keyEventTriggers chains between them. Renders as
a connected cascade graph rather than a disconnected star.

```cypher
MATCH (ke:KeyEvent)-[:keIncludedInAOP]->(aop:AOP)
WHERE toLower(ke.commonName) CONTAINS 'oxidative'
WITH DISTINCT aop
MATCH (ke1:KeyEvent)-[r_inc:keIncludedInAOP]->(aop)
OPTIONAL MATCH (ke1)-[r_trig:keyEventTriggers]->(ke2:KeyEvent)-[:keIncludedInAOP]->(aop)
RETURN aop, r_inc, ke1, r_trig, ke2;
```

### 4e. AOP key event cascade -- oxidative stress event chains

Shows just the key-event-triggers chains within oxidative-stress AOPs
(without the AOP hub node), so the cascade sequence is front and center.

```cypher
MATCH (ke:KeyEvent)-[:keIncludedInAOP]->(aop:AOP)
WHERE toLower(ke.commonName) CONTAINS 'oxidative'
WITH DISTINCT aop
MATCH (ke1:KeyEvent)-[r_inc1:keIncludedInAOP]->(aop)
MATCH (ke1)-[r:keyEventTriggers]->(ke2:KeyEvent)-[r_inc2:keIncludedInAOP]->(aop)
RETURN ke1, r, ke2;
```

### 4f. Cross-chemical analysis -- all chemicals to lung cancer via genes

Shows every path from the target chemicals through genes to lung cancer.
Multiple chemicals converging on the same gene are visible as a fan pattern.

```cypher
MATCH (c:Chemical)
      -[r1:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
      -[r2:geneAssociatesWithDisease]->(d:Disease {commonName: 'Malignant neoplasm of lung'})
WHERE c.commonName IN ['Benzene', '1,3-Butadiene', 'Chlordane',
                        'Diethanolamine', '1,2-Propylene oxide', 'Arsenic (III)']
RETURN c, r1, g, r2, d;
```

---

## Bonus queries

### DNA repair pathway genes affected by Benzene

```cypher
MATCH (c:Chemical {commonName: 'Benzene'})
      -[r1:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
      -[r2:geneInPathway]->(p:Pathway {commonName: 'DNA Repair'})
RETURN c, r1, g, r2, p;
```

### Oxidative stress pathway genes affected by Benzene

```cypher
MATCH (c:Chemical {commonName: 'Benzene'})
      -[r1:chemicalIncreasesExpression|chemicalDecreasesExpression]->(g:Gene)
      -[r2:geneInPathway]->(p:Pathway {commonName: 'Oxidative Stress'})
RETURN c, r1, g, r2, p;
```

### Tox21 assay activity for Benzene

Shows which Tox21 assays Benzene is active in.

```cypher
MATCH (c:Chemical {commonName: 'Benzene'})-[r:chemicalHasActiveAssay]->(a:Assay)
RETURN c, r, a;
```

### Full neighborhood of a single gene (e.g., TP53)

Explore everything connected to a hub gene -- chemicals that affect it,
diseases it associates with, pathways it belongs to, and interacting genes.

```cypher
MATCH (g:Gene {geneSymbol: 'TP53'})-[r]-(n)
RETURN g, r, n;
```
