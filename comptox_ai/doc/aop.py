'''
========================
Adverse Outcome Pathways
========================

What is an adverse outcome pathway?
===================================

An Adverse Outcome Pathway (AOP) is a conceptual framework for structuring the
series of events and entities that lead to an adverse phenotypic effect
following exposure to a toxicant [1]_ . In other words, an AOP is the set of
steps that links a toxin to its clinical effects.

AOPs are naturally compatible with ComptoxAI, since they can be reduced to
directed graphs (nodes are key events and/or adverse outcomes, and edges are
links between them) that can be integrated directly into ComptoxAI's graph
database.

For example, an AOP can be used to describe the processes that lead from PPARα
activation to decreased male fertility through the following steps:

.. figure:: ../_static/img/aop_fertility.jpg
   :width: 360px
   :align: center
   :alt: AOP 18

   `AOP 18`_ - PPARα activation in utero leading to impaired fertility in males

If you would like to learn more about specific AOPs, a good external resource
is the community-maintained `AOP Wiki`_, which provides detailed information on
specific AOPs and the KEs that comprise them.

.. _`AOP Wiki`: https://aopwiki.org/

.. _`AOP 18`: https://aopwiki.org/aops/18

Main components of an AOP
=========================

AOPs consist of the following major components:

Toxicant
  A chemical or biological agent that causes stress to an organism, leading to
  mechanisms of toxicity.

Stressor
  A slightly more generalized equivalent of a toxicant, possibly comprising a
  set of multiple chemicals that have similar molecular effects

Key Event (KE)
  An event linked to one or more other key events making up a *node* in the
  AOP. KEs occur when either a stressor or a previous event act on a biological
  entity. These entities can come from many levels of biological organization,
  ranging from molecules to tissue systems and clinical phenotypes. KEs usually
  describe action on more fine-grained structures when close to an MIE (see
  below), and on more general concepts when close to an AO (also described
  below).

Molecular Initiating Event (MIE)
  A specific type of KE that is caused by the direct action of a chemical
  stressor, and is not preceded by other KEs (at least within the context of
  the AOP of interest). As the name implies, MIEs describe activity exerted at
  the level of molecules.

Adverse Outcome (AO)
  A measurable phenotypic change in a biological system (usually, a clinically
  important disease) that acts as a point of termination in an AOP. Like MIEs,
  AOs are a specific type of KE. Importantly, AOs are not necessarily confined
  to a single organism (e.g., exposure of a marine toxicant can lead to a
  declining population trajectory in a certain species of fish).

These components are arranged as nodes in a directed acyclic graph (DAG), where
the directed edges between the nodes imply a causal relationship between two
KEs (e.g., :math:`\mathbf{A} \\rightarrow \mathbf{B}` means that key event
:math:`\mathbf{A}` causes key event :math:`\mathbf{B}`). Keep in mind that
causal links often bridge two or more levels of biological organization.

How are adverse outcome pathways used in ComptoxAI?
===================================================

AOPs form subgraphs in ComptoxAI's graph database. Several node labels in the
graph database correspond to AOP-related concepts:

.. list-table:: :header-rows: 1

   * - Node label
     - Conceptual class

   * - ``AOP``
     - Adverse outcome pathway

   * - ``KE``
     - Key event

   * - ``MIE``
     - Molecular initiating event

   * - ``AO``
     - Adverse outcome

Like all node labels in the graph database, each of these also corresponds to a
class in the ComptoxAI ontology.

Note that there are no explicitly created node labels for stressors - instead,
links to previous existing ``Chemical`` nodes are drawn to their corresponding
MIEs when an AOP is added to the database.

We are developing an entire AOP module as part of ComptoxAI's Python package,
to make it easier to retrieve, manipulate, and analyze AOPs, as well as the
roles they play in the larger perspective of the entire graph database.

.. seealso::

    :ref:`aop`

References
==========

.. [1] Ankley, Gerald T., et al. "Adverse outcome pathways: a conceptual
  framework to support ecotoxicology research and risk assessment." Environmental
  Toxicology and Chemistry: An International Journal 29.3 (2010): 730-741.
'''
