"""
Algorithms and search strategies for extracting subgraphs from a larger parent
graph.
"""


class BigraphExtractor(object):
  """
  Algorithm for extracting all subgraphs from a larger parent graph.

  Given two ontology classes (i.e., node types) $A$ and $B$ and a path template
  defining allowed intermediate nodes and edges, this algorithm constructs a
  bipartite graph linking entities in $A$ to entities in $B$.

  This algorithm is especially useful as a first step in an enrichment analysis
  experiment. For example, if $A$ is chemicals and $B$ is genes, the output can
  be used to construct a statistical model that searches for chemicals enriched
  for a certain set of genes.

  Another (related) application is cluster analysis, where you can search for
  similar members of $A$ based upon overlapping connections to members of $B$.
  """
  
  def __init__(self, class_A, class_B, template):

    
    self.A = class_A
    self.B = class_B

  def run(self):
    pass