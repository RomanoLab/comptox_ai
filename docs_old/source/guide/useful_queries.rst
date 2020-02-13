Useful Cypher queries
*********************

This is a list of Cypher queries that came up during the development of
ComptoxAI. We've written them down both for our own reference and for the
benefit of our users.

Export all nodes to JSON (except for orphan Individuals)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

   MATCH (n)
   MATCH ()-[r]-()
   WHERE ((n:owl__NamedIndividual)-[r]-(:owl__NamedIndividual))
     OR (not (n:owl__NamedIndividual))
    WITH collect(n) as a, collect(r) as b
   CALL apoc.export.json.data(a, b, "x.json", null)
   YIELD file
   RETURN file

The export feature of APOC doesn't seem to play well with large graphs. On my
fairly powerful laptop with a Neo4j heap size of 8GB the procedure was still
running after over 3 hours, so I terminated it.

I tried again with a simpler query - just all non-orphan individual nodes and
the relationships that link them. I also used a different procedure call -
instead collecting nodes and relationships as lists, I simply provide the
Cypher query to the export procedure:

.. code-block::

   CALL apoc.export.json.query(
     "MATCH (n:owl__NamedIndividual)-[r]-(:owl__NamedIndividual) WITH COLLECT(DISTINCT n) as a, COLLECT(DISTINCT r) as b RETURN a, b",
     "x.json",
     {}
   )

