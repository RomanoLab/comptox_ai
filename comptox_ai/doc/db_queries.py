r'''
================
Database Queries
================

Introduction
============

ComptoxAI is largely built around a *graph database* of entities, their semantic
types, and the relationships that link these entities. This is implemented using
Neo4j.

This document is meant to show how you can interact with these two databases to
learn meaningful things about computational toxicology data. We'll start by
taking at how these data are formatted in the source database, and then we'll
discuss how to retrieve and manipulate them using ComptoxAI.

Graph database representation of an entity
==========================================

For example, consider the chemical *hydroxychloroquine* (118-42-3 |
DTXSID8023135). Hydroxychloroquine's node in the graph database looks roughly
like::

  {
    "identity": 32519,
    "labels": [
      "Chemical",
      "NamedIndividual",
      "Resource"
    ],
    "properties": {
      "commonName": "Hydroxychloroquine",
      "inchiKey": "XXSMGPRMXLTPCZ-UHFFFAOYSA-N",
      "inchi": "InChI=1S/C18H26ClN3O/c1-3-22(11-12-23)10-4-5-14(2)21-17-8-9-20-18-13-15(19)6-7-16(17)18/h6-9,13-14,23H,3-5,10-12H2,1-2H3,(H,20,21)",
      "xrefDrugbank": "DB01611",
      "xrefMeSHUI": "D006886",
      "xrefPubchemSID": 315673741,
      "xrefCasRN": "118-42-3",
      "uri": "http://jdr.bio/ontologies/comptox.owl#chem_hydroxychloroquine",
      "chemicalIsInCTD": true,
      "chemicalIsDrug": true,
      "xrefPubchemCID": 3652,
      "xrefDtxsid": "DTXSID8023135"
    }
  }

These are mainly just identifiers, but things get more interesting when we look
at relationships to other nodes in the graph database. At the time of writing,
the node is directly linked to 480 other nodes in the database. Here is one of
those relationships::

  {
    "identity": 1210864,
    "start": 32519,
    "end": 19842,
    "type": "CHEMICALASSOCIATESWITHDISEASE",
    "properties": {}
  }

In this case, the start node (32519) is hydroxychloroquine, the relationship
type is ``CHEMICAL_ASSOCIATES_WITH_DISEASE`` the end node (22421) is *spinal
cord compression*::

  {
    "identity": 19842,
    "labels": [
      "Resource",
      "NamedIndividual",
      "Disease"
    ],
    "properties": {
      "commonName": "Spinal Cord Compression",
      "uri": "http://jdr.bio/ontologies/comptox.owl#dis_spinalcordcompression",
      "xrefMeSH": "D013117"
    }
  }

Or in other words:

.. math:: \langle\textit{hydroxychloroquine}\rangle\,\texttt{CHEMICAL\_ASSOCIATES\_WITH\_DISEASE}\,\langle\textit{spinal cord compression}\rangle

Finding nodes using Cypher
==========================

Queries in Neo4j are usually performed using the Cypher query language, which
looks almost like a dialect of SQL that has been adapted to graph data. You can
search for a node either directly by the node's ID, or by any node property. In
the case of hydroxychloroquine, we can find it using the following Cypher
query::

   $ MATCH (n:Chemical {commonName: "Hydroxychloroquine"}) RETURN n;

The ``MATCH`` clause searches for entities in the database (in this case, any
node with the ``Chemical`` label and the property ``commonName`` equal to
``"Hydroxychloroquine"``) and binds them to the placeholder variable ``n``, and
the RETURN clause says what to give back to the user who made the query (in this
case, it just provides ``n`` without any further filtering or processing).

To retrieve the same node by ID (e.g., if you ran a query previously and took
note of the node's ID), you could say::

   $ MATCH (n) WHERE id(n) = 32519 RETURN n;

Notice that in this case we have added a ``WHERE`` clause, which applies more
complex filtering and other processing operations than can be specified in the
``MATCH`` clause alone. We also use the ``id()`` function, which (as you can
probably imagine) accepts a node and returns the ID of that node as an integer
value.

Of course, there are many Cypher queries that can yield the same node.

Finding nodes using Python
==========================

ComptoxAI's Python interface makes it easier to retrieve entities from the graph
database, compared to the Cypher-based methods introduced above. Let's see how
to find the same node as above, but using Python instead::

   >>> from comptox_ai.db.graph_db import GraphDB
   >>> db = GraphDB()
   >>> db.find_node(properties={'commonName': 'Hydroxychloroquine'})

This returns the same node, just as a Python object. The value of the
``properties`` argument is a dict that can contain any node properties and
associated values for those properties. Instead of properties, we can also use
the node's ID::

   >>> db.find_node(node_id=32519)

Finding relationships using Cypher
==================================

Cypher's syntax for relationships (equivalently 'edges') actually looks like two
nodes linked by a directed edge in a graph::

   $ MATCH (n1:Chemical)-[r]->(n2:Disease) WHERE id(n1) = 32519 RETURN r;

In this case, we bind the 'from' node (hydroxychloroquine) to ``n1``, the
relationship to ``r``, and the 'to' node (any Disease) to ``n2``, but we only
return ``r`` to the user.

Finding relationships using Python
==================================

ComptoxAI provides a method called ``find_relationships``::

   >>> from comptox_ai.db.graph_db import GraphDB
   >>> db = GraphDB()
   >>> db.find_relationships(from_type="Chemical", to_type="Disease", from_id=32519) 

A pretty wide variety of arguments can be fed into ``find_relationships()``, but
the command will return an error if not enough arguments are provided to
unambiguously resolve the search query. Please refer to :class:`GraphDB`
for details.

'''
