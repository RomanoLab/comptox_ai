# ComptoxAI TODO

## ista mapping preprocessing tasks

### 1. NCBI Gene `dbXrefs` compound field preprocessing
The `Homo_sapiens.gene_info` file has a `dbXrefs` column containing pipe-delimited key-value pairs (e.g. `MIM:603369|HGNC:HGNC:1789|Ensembl:ENSG00000123080`). The ista YAML format doesn't support compound field splitting natively. Write a preprocessing script (`comptox_ai/build/scripts/preprocess_ncbi_gene.py`) that reads the TSV and adds separate `MIM`, `HGNC`, and `Ensembl` columns. Then uncomment the three xref property lines in `comptox_ai/build/comptox_mapping.yaml` under the Gene entity_type.

### 2. MolecularInitiatingEvent / AdverseOutcome `append_class`
The original `db.py` adds MolecularInitiatingEvent and AdverseOutcome as additional OWL class assertions on existing KeyEvent individuals (`append_class=True`). The ista YAML `mode: enrich` adds data properties but may not add class assertions. If ista doesn't support this, run these Cypher queries against Memgraph after `owl2memgraph` import:

```cypher
// Get MIE event IDs from aopdb.event_info WHERE event_type = 'molecular-initiating-event'
MATCH (n:KeyEvent) WHERE n.xrefAOPWikiKEID IN [<MIE event_ids>]
SET n:MolecularInitiatingEvent;

// Get AO event IDs from aopdb.event_info WHERE event_type = 'adverse-outcome'
MATCH (n:KeyEvent) WHERE n.xrefAOPWikiKEID IN [<AO event_ids>]
SET n:AdverseOutcome;
```

### 3. AOP-DB `keIncludedInAOP` multi-value field expansion
The `event_info` table's `AOP_ids` column contains `"; "`-delimited lists of AOP IDs per KeyEvent row (e.g. `"12; 45; 78"`). If ista doesn't auto-expand multi-value fields during relationship mapping, write a preprocessing step or custom SQL view that explodes each row into one `(event_id, AOP_id)` pair per row before the relationship mapping runs.
