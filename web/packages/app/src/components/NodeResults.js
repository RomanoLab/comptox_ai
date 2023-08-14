import React from 'react';
import { Map } from 'react-lodash';
import { Button, Paper } from '@mui/material';

import { useAppSelector, useAppDispatch } from '../redux/hooks';

import NodeResult from './NodeResult';
import {
  useFetchChemicalByDtsxidQuery,
  useSearchNodesQuery,
} from '../features/comptoxApiSlice';
import { setSearch } from '../features/nodeSlice';

const NodeResults = (props) => {
  const { config } = props;
  const dispatch = useAppDispatch();

  const searchParams = useAppSelector((state) => state.node.searchParams);

  const dsstoxResults = useFetchChemicalByDtsxidQuery(
    searchParams.params.dtxsid,
    {
      skip: !(searchParams.searchType === 'dsstox'),
    }
  );
  const nodeResults = useSearchNodesQuery(
    [
      searchParams.params.label,
      searchParams.params.field,
      searchParams.params.value,
    ],
    {
      skip: !(searchParams.searchType === 'node'),
    }
  );

  const searchResults =
    searchParams.searchType === 'dsstox' ? dsstoxResults : nodeResults;

  const handleResetNodeSearch = () => {
    dispatch(
      setSearch({
        searchType: null,
        params: {},
      })
    );
  };

  return (
    <div class="subject-container">
      <h3>Search Results</h3>
      {searchResults.isError ? (
        <>
          Error - the requested node was not found. Please try again with a new
          query.
        </>
      ) : searchResults.isUninitialized ? (
        <>Please enter a search query and click "Search" to find nodes.</>
      ) : searchResults.isLoading ? (
        <>Loading...</>
      ) : searchResults.data ? (
        <div>
          <Button
            onClick={handleResetNodeSearch}
            variant="outlined"
            style={{ marginBottom: '6px' }}
          >
            Clear node search results
          </Button>
          <Paper>
            <Map
              collection={searchResults.data}
              iteratee={(r) => (
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
};

export default NodeResults;
