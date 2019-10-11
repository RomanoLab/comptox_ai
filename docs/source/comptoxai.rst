.. _comptoxai:

*************************************************************
Top-level wrapper for ComptoxAI analyses (:class:`ComptoxAI`)
*************************************************************

Most users should interact with ComptoxAI by instantiating this class and
calling the provided convenience functions for running the most commonly-used
subroutines.

.. admonition:: Example

   Connecting to the graph database and fetching a list of node degrees for all nodes in the ontology class "AdverseOutcome":

   >>> cai = ComptoxAI(config_file="../CONFIG-default.cfg")
   Loading configuration file...
   bolt://localhost:7687
   >>> cai.graph.get_node_degrees("AdverseOutcome")
   [('http://jdr.bio/ontologies/comptox.owl#ao_decrease_lung_function', 3),
    ('http://jdr.bio/ontologies/comptox.owl#ao_inflamatory_events_in_light-exposed_tissues', 5),
    ('http://jdr.bio/ontologies/comptox.owl#ao_bronchiolitis_obliterans', 3),
    ('http://jdr.bio/ontologies/comptox.owl#ao_increase_adenomas/carcinomas_bronchioloalveolar', 4),

.. currentmodule:: comptox_ai

.. autoclass:: ComptoxAI
   :members:
