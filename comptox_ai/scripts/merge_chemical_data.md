## Neo4j commands for merging completed chemical data into graph database

```
LOAD CSV WITH HEADERS FROM 'file:///chemicals.csv' AS row
MERGE (c:Chemical {ns0__xrefCasRN: row.casrn,
                   ns0__
                   })
```