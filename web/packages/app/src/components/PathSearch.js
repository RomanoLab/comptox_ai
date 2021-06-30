import React from 'react';
import { Graph } from "react-d3-graph";

const iriPrefixRe = /^.*#(.+)$/;
const nameSplitRe = /^([^_]+)_(.+)$/;

const graphConfig = {
  directed: true,
  initialZoom: 2,
  node: {
    color: "#216a05",
  }
};

/**
 * Extract a node class and (hopefully) unique identifier from a node, given
 * its ontology IRI.
 * @param {string} full_iri 
 * @returns 
 */
function processOntologyNodeIRI(full_iri) {
  const stripPrefixMatch = full_iri.match(iriPrefixRe);
  const fullName = stripPrefixMatch[1];

  const fullNameSplit = fullName.match(nameSplitRe);

  return {
    nodeClass: fullNameSplit[1],
    nodeId: fullNameSplit[2],
  }
}

function parseNodeToVertex(node) {
  const parsedNodeIRI = processOntologyNodeIRI(node.ontologyIRI);
  
  const nodeLabel = parsedNodeIRI.nodeClass;
  const nodeName = parsedNodeIRI.nodeId;

  return {
    id: nodeName,
    nodeLabel: nodeLabel
  }
};

function parseRelationshipToEdge(relationship) {
  const parsedSourceIRI = processOntologyNodeIRI(relationship.fromIRI);
  const parsedTargetIRI = processOntologyNodeIRI(relationship.toIRI);
  
  return {
    source: parsedSourceIRI.nodeId,
    target: parsedTargetIRI.nodeId,
    relType: relationship.relType,
  }
}

const PathSearch = (props) => {
  const getNodes = () => {
    var nodes = [];

    // Do start node;
    if (typeof this.state.startNode !== undefined) {
      nodes.push(parseNodeToVertex(this.state.startNode));
    }
    if (typeof this.state.endNode !== undefined) {
      nodes.push(parseNodeToVertex(this.state.endNode));
    }

    return nodes;
  }

  const getRelationships = () => {
    var rels = [];

    this.state.relationships.forEach(r => {
      rels.push(parseRelationshipToEdge(r));
    });

    return rels;
  }
  
  return(
    <div id="path-search">
      <h2>Paths</h2>
      <p>
        <i>Load a "start node" and "end node" by clicking the corresponding button on node search results.</i>
      </p>
      {!(this.state.pathResults === undefined) &&
      <Graph
        id="path-search-result"
        data={this.graphData}
        config={graphConfig}
      />
      }
    </div>
  );
}

export default PathSearch;
