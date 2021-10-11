.. _docs:

*************
API Reference
*************

This is a reference guide for the modules, classes, and functions in 
ComptoxAI's Python interface. For a more general overview of ComptoxAI,
computational toxicology, and graph databases, please refer to the :ref:`User
Guide <user_guide>`.

.. note::

   This is the API documentation for ComptoxAI's Python package. If you are
   looking for documentation for the REST web API, please see :ref:`web_api` in the User Guide.

.. _db_ref:

:mod:`comptox_ai.db`: ComptoxAI's graph database
================================================
.. currentmodule:: comptox_ai

Tools to access, query, and export data from ComptoxAI's Neo4j graph database.

**User Guide:** See :ref:`graph_db` and :ref:`` for further details.

.. autoclass:: comptox_ai.db.GraphDB
   :members:
   :undoc-members:

    .. rubric:: Methods

    .. autoclasssummary:: comptox_ai.db.GraphDB
        :methods:

    .. rubric:: Attributes

    .. autoclasssummary:: comptox_ai.db.GraphDB
        :attributes:


.. _graph_ref:

:mod:`comptox_ai.graph`: Graphs
===============================
.. currentmodule:: comptox_ai

Tools for Python-based representation and manipulation of graphs (and/or 
subgraphs) extracted from the :ref:`graph database <db_ref>`.

**User Guide:** See :ref:`graphs` for further details.

.. autosummary::
   :toctree: generated/
   :template: class.rst

   graph.Graph
   graph.io

..
   :mod:`comptox_ai.algorithm`: Graph algorithms
   =============================================
   .. currentmodule:: comptox_ai

.. _ml_ref::

:mod:`comptox_ai.ml`: Machine learning models
=============================================
.. currentmodule:: comptox_ai

Machine learning models designed (and tuned) with ComptoxAI's graph database in
mind. These include both *shallow* and *deep* models, and operate on both
*tabular* and *graph* data.

Graph ML
--------

.. autosummary::
   :toctree: generated/
   :template: class.rst

Non-graph ML
------------

.. autosummary::
   :toctree: generated/
   :template: class.rst

..
   :mod:`comptox_ai.ontology`: Ontology tools
   ==========================================
   .. currentmodule:: comptox_ai

..
   Miscellaneous
   =============
   .. currentmodule:: comptox_ai