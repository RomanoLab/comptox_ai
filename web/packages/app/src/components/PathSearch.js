import React from 'react';
import { Graph } from 'react-d3-graph';
import { Box, Button, Typography } from '@mui/material';

import { useFindPathByNodeIdsQuery } from '../features/comptoxApiSlice';
import {
  setPathEndNodeId,
  setPathEndNodeName,
  setPathStartNodeId,
  setPathStartNodeName
} from '../features/pathSlice';
import { useAppDispatch, useAppSelector } from '../redux/hooks';

const graphConfig = {
  directed: true,
  initialZoom: 2,
  node: {
    color: '#216a05',
    labelProperty: 'name'
  }
};

const colorMap = {
  Chemical: '#e53935',
  Gene: '#c158dc',
  Pathway: '#6f74dd',
  KeyEvent: '#039be5',
  MolecularInitiatingEvent: '#4ebaaa',
  AdverseOutcome: '#aee571',
  AOP: '#fdd835',
  Assay: '#8eacbb'
};

const PathSearch = (props) => {
  const pathStartId = useAppSelector((state) => state.path.pathStartNodeId);
  const pathStartName = useAppSelector((state) => state.path.pathStartNodeName);
  const pathEndId = useAppSelector((state) => state.path.pathEndNodeId);
  const pathEndName = useAppSelector((state) => state.path.pathEndNodeName);

  const dispatch = useAppDispatch();

  const skip = !pathStartId || !pathEndId ? true : false;

  const {
    data = [],
    error,
    isLoading,
    isUninitialized
  } = useFindPathByNodeIdsQuery([pathStartId, pathEndId], {
    skip
  });

  const nodes = data.nodes ? data.nodes : [];
  const relationships = data.relationships ? data.relationships : [];

  const nodes_parsed = nodes.map((n) => ({
    id: n.id,
    name: n.name,
    nodeType: n.labels[0],
    color: colorMap[n.labels[0]]
  }));

  const links_parsed = relationships.map((r) => ({
    source: r.source,
    target: r.target
  }));

  const parsed_data = {
    nodes: nodes_parsed,
    links: links_parsed
  };

  const handleClearPathSearch = () => {
    dispatch(setPathStartNodeId(null));
    dispatch(setPathEndNodeId(null));
    dispatch(setPathStartNodeName(''));
    dispatch(setPathEndNodeName(''));
  };

  const handleLoadExamplePath = () => {
    dispatch(setPathStartNodeId(660070));
    dispatch(setPathEndNodeId(723548));
    dispatch(
      setPathStartNodeName('cytochrome P450 family 2 subfamily E member 1')
    );
    dispatch(setPathEndNodeName('Capsaicin'));
  };

  return (
    <div id="path-search" className="subject-container">
      <h2>Paths</h2>
      <p>
        <i>
          Find a single shortest path linking two nodes in the knowledge graph.
          To find all paths with the shortest length, use the &quot;Make all shortest
          paths query&quot; tool, below.
        </i>
      </p>
      {pathStartId && (
        <Typography variant="h6">Start node: {pathStartName}</Typography>
      )}
      {pathEndId && (
        <Typography variant="h6">End node: {pathEndName}</Typography>
      )}
      <Button variant="outlined" onClick={handleLoadExamplePath}>
        Load example path
      </Button>
      <Button
        variant="outlined"
        style={{ margin: '4px' }}
        onClick={handleClearPathSearch}
      >
        Clear path search
      </Button>
      <hr />
      {error ? (
        <>Error: No path can be found between the two nodes!</>
      ) : isUninitialized ? (
        <i>
          Set start and end nodes using the Node Search interface above to
          search for a shortest path between the two nodes.
        </i>
      ) : isLoading ? (
        <>Loading</>
      ) : data ? (
        <>
          <Box border={2} borderRadius="3px">
            <Graph
              id="path-search-result"
              data={parsed_data}
              config={graphConfig}
            />
          </Box>
          <i>Zoom, pan, and scroll via mouse controls.</i>
        </>
      ) : null}
    </div>
  );
};

export default PathSearch;
