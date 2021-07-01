import React from 'react';
import { Graph } from "react-d3-graph";
import { Box } from "@material-ui/core";

import { useAppSelector } from '../redux/hooks';
import { useFindPathByNodeIdsQuery } from '../features/comptoxApiSlice';

const graphConfig = {
  directed: true,
  initialZoom: 2,
  node: {
    color: "#216a05",
    labelProperty: "name",
  }
};

const colorMap = {
  "Chemical": '#e53935',
  "Gene": '#c158dc',
  "Pathway": '#6f74dd',
  "KeyEvent": '#039be5',
  "MolecularInitiatingEvent": '#4ebaaa',
  "AdverseOutcome": '#aee571',
  "AOP": '#fdd835',
  "Assay": '#8eacbb',
}

const PathSearch = (props) => {
  const pathStartId = useAppSelector((state) => state.path.pathStartNodeId);
  const pathEndId = useAppSelector((state) => state.path.pathEndNodeId);

  const skip = ((!pathStartId) || (!pathEndId)) ? true : false;
  
  console.log("skip path query?");
  console.log(skip);
  
  const { data = [], error, isLoading, isUninitialized } = useFindPathByNodeIdsQuery([pathStartId, pathEndId], {
    skip,
  });

  const nodes = data.nodes ? data.nodes : [];
  const relationships = data.relationships ? data.relationships : [];

  console.log("DATA:")
  console.log(data);

  const nodes_parsed = nodes.map(n => ({
    id: n.id,
    name: n.name,
    nodeType: n.labels[0],
    color: colorMap[n.labels[0]],
  }));

  const links_parsed = relationships.map(r => ({
    source: r.source,
    target: r.target
  }));

  const parsed_data = {
    nodes: nodes_parsed,
    links: links_parsed
  };

  console.log("PARSED DATA:")
  console.log(parsed_data);
  
  return(
    <div id="path-search">
      <h2>Paths</h2>
      <p>
        Start node: {pathStartId}
      </p>
      <p>
        End node: {pathEndId}
      </p>
      {error ? (
        <>Error: No path can be found between the two nodes!</>
      ) : isUninitialized ? (
        <>Uninitialized</>
      ) : isLoading ? (
        <>Loading</>
      ) : data ? (
        <Box
          border={2}
          borderRadius="3px"
        >
          <Graph
            id="path-search-result"
            data={parsed_data}
            config={graphConfig}
          />
        </Box>
      ) : null }
      {/* <p>
        <i>Load a "start node" and "end node" by clicking the corresponding button on node search results.</i>
      </p> */}
      {/* {!(this.state.pathResults === undefined) &&
      <Graph
        id="path-search-result"
        data={this.graphData}
        config={graphConfig}
      />
      } */}
    </div>
  );
}

export default PathSearch;


 // const selectedPath = useAppSelector((state) => {
  //   // return {
  //   //   startId: state.pathStartNodeId,
  //   //   endId: state.pathEndNodeId
  //   // }
  //   return [
  //     state.pathStartNodeId,
  //     state.pathEndNodeId
  //   ]
  // });
 
// const getNodes = () => {
//   // var nodes = [];
//   // if (typeof this.state.startNode !== undefined) {
//   //   nodes.push(parseNodeToVertex(this.state.startNode));
//   // }
//   // if (typeof this.state.endNode !== undefined) {
//   //   nodes.push(parseNodeToVertex(this.state.endNode));
//   // }
//   // return nodes;
// }

// const getRelationships = () => {
//   var rels = [];
//   this.state.relationships.forEach(r => {
//     rels.push(parseRelationshipToEdge(r));
//   });
//   return rels;
// }