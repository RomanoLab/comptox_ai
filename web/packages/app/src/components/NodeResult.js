import React from 'react';
import { IsEmpty, Map } from 'react-lodash';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Button from '@material-ui/core/Button';

import { useAppDispatch } from '../redux/hooks';
import { setRelStartNode } from '../features/relationships/relationshipSlice';

const NodeResult = (props) => {
  const { nodeType, nodeName, nodeIRI, nodeIDs, nodeNeo4jID } = props;
  const dispatch = useAppDispatch();

  const handleRelSearch = event => {
    dispatch(setRelStartNode(nodeNeo4jID));
  }
  
  return(
    <div className="node-detail">
      <p>Data type(s): {nodeType}</p>
      <p>Name: <span className="node-name">{nodeName}</span></p>

      <IsEmpty
        value={nodeIDs}
        yes="No external IDs found"
        no={() => (
          <div>
            <p>External Identifiers:</p>
            <ul>
              <Map
                collection={nodeIDs}
                iteratee={i => <li key={i.idValue}>{i.idValue}</li>}
              />
            </ul>
          </div>
        )}
      />

      <p id="uri-text">Ontology IRI: <tt>{nodeIRI}</tt></p>

      <Button color="primary" variant="outlined" size="small" onClick={handleRelSearch}>
        View relationships
      </Button>
      <ButtonGroup color="primary" size="small" aria-label="small outlined button group">
        <Button>Path start node</Button>
        <Button>Path end node</Button>
      </ButtonGroup>
    </div>
  );
}

export default NodeResult;