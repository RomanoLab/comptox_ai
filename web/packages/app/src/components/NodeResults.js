import React from 'react';

import {
  Map,
  Paper
} from '@mui/material';

const NodeResults = (props) => {
  
  
  return (
    <h3>Search Results</h3>
    {error ? (
      <>Error - the requested node was not found. Please try again with a new query.</>
    ) : isUninitialized ? (
      <>Please enter a search query and click "Search" to find nodes.</>
    ) : isLoading ? (
      <>Loading...</>
    ) : nodeResults ? (
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
            collection={nodeResults}
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
  );
}