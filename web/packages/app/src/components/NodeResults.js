import React from 'react';
import { Map } from 'react-lodash';
import {
  Button,
  Paper
} from '@mui/material';

import { useAppSelector } from '../redux/hooks';

import NodeResult from './NodeResult';

const NodeResults = (props) => {
  const { config } = props;

  const error = false;
  const isLoading = false;
  const isUninitialized = false;

  const searchResults = useAppSelector((state) => state.node.searchResults);

  const handleResetNodeSearch = () => {

  }
  
  return (
    <div>
      <h3>Search Results</h3>
      {error ? (
        <>Error - the requested node was not found. Please try again with a new query.</>
      ) : isUninitialized ? (
        <>Please enter a search query and click "Search" to find nodes.</>
      ) : isLoading ? (
        <>Loading...</>
      ) : searchResults ? (
        <div>
          <Button 
            onClick={handleResetNodeSearch}
            variant="outlined"
            style={{marginBottom:'6px'}}
          >
            Clear node search results
          </Button>
          <Paper>
            <Map
              collection={searchResults}
              iteratee={r => (
                <NodeResult
                  nodeType={r.nodeType}
                  nodeName={r.commonName}
                  nodeIDs={r.identifiers}
                  nodeIRI={r.ontologyIRI}
                  nodeNeo4jID={r.nodeId}
                  nodeFeatures={r.nodeFeatures}
                  config={config}
                />
              )}
            />
          </Paper>
        </div>
      ) : null}
    </div>
  );
}

export default NodeResults;