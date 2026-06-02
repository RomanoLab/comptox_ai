const _ = require('lodash');

const EDGE_SCHEMA = [
  { source: 'Chemical', rel: 'chemicalIncreasesExpression', target: 'Gene', display: 'increases expression of' },
  { source: 'Chemical', rel: 'chemicalDecreasesExpression', target: 'Gene', display: 'decreases expression of' },
  { source: 'Chemical', rel: 'chemicalHasActiveAssay', target: 'Assay', display: 'is active in assay' },
  { source: 'Chemical', rel: 'chemicalHasInactiveAssay', target: 'Assay', display: 'is inactive in assay' },
  { source: 'Chemical', rel: 'chemicalInList', target: 'ChemicalList', display: 'is in list' },
  { source: 'Gene', rel: 'geneInPathway', target: 'Pathway', display: 'participates in' },
  { source: 'Gene', rel: 'geneInteractsWithGene', target: 'Gene', display: 'interacts with' },
  { source: 'Gene', rel: 'geneAssociatesWithDisease', target: 'Disease', display: 'associated with' },
  { source: 'Pathway', rel: 'PathwayContainsGene', target: 'Gene', display: 'contains gene' },
  { source: 'AOP', rel: 'aopIncludesKE', target: 'KeyEvent', display: 'includes key event' },
  { source: 'KeyEvent', rel: 'keIncludedInAOP', target: 'AOP', display: 'is included in AOP' },
  { source: 'KeyEvent', rel: 'keyEventTriggers', target: 'KeyEvent', display: 'triggers' },
  { source: 'KeyEvent', rel: 'keyEventTriggers', target: 'AdverseOutcome', display: 'triggers adverse outcome' },
  { source: 'KeyEvent', rel: 'keyEventTriggeredBy', target: 'MolecularInitiatingEvent', display: 'triggered by' },
  { source: 'KeyEvent', rel: 'keyEventTriggeredBy', target: 'KeyEvent', display: 'triggered by' },
  { source: 'ChemicalList', rel: 'listIncludesChemical', target: 'Chemical', display: 'includes chemical' },
];

const NODE_TYPES = _.uniq(EDGE_SCHEMA.flatMap((e) => [e.source, e.target])).sort();

function getEdgeSchema() {
  return { edges: EDGE_SCHEMA, nodeTypes: NODE_TYPES };
}

function edgesFromSource(sourceType) {
  return EDGE_SCHEMA.filter((e) => e.source === sourceType);
}

function isValidNodeType(t) {
  return NODE_TYPES.includes(t);
}

function isValidRelType(r) {
  return EDGE_SCHEMA.some((e) => e.rel === r);
}

module.exports = { getEdgeSchema, edgesFromSource, isValidNodeType, isValidRelType, EDGE_SCHEMA, NODE_TYPES };
