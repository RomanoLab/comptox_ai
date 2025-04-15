"""
Entity Types
************

.. seealso:: :ref:`Source databases <guide_databases>`

Node types
----------

In Neo4j nomenclature, these are referred to as "node labels".

Chemicals
^^^^^^^^^

Any chemical substance. Special emphasis is given to xenobiotic chemicals.

Metadata:

==============  ===========  ===========
 Data element    Data type     Example
--------------  -----------  -----------
commonName      string       "Gentamicin
chemicalIsDrug  bool         true
xrefCasRN       string       "1403-66-3"
xrefDrugbank    string       "DB00798"
==============  ===========  ===========

Chemical features:

============  =========  ==============
Feature name  Data type  Dimensionality
------------  ---------  --------------
SMILEs        String     n/a
============  =========  ==============

Genes
^^^^^

+--------------+-----------+---------+
| Data element | Data type | Example |
+==============+===========+=========+
|              |           |         |
+--------------+-----------+---------+

Diseases
^^^^^^^^

AOPs
^^^^

Relationship types
------------------
"""
