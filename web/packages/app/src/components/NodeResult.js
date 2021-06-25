import React from 'react';
import { IsEmpty, Map } from 'react-lodash';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Button from '@material-ui/core/Button';

function NodeResult(props) {
  console.log(props);
  
  return(
    <div className="node-detail">
      <p>Data type(s): {props.nodeType}</p>
      <p>Name: <span className="node-name">{props.nodeName}</span></p>

      <IsEmpty
        value={props.nodeIDs}
        yes="No external IDs found"
        no={() => (
          <div>
            <p>External Identifiers:</p>
            <ul>
              <Map
                collection={props.nodeIDs}
                iteratee={i => <li key={i.idValue}>{i.idValue}</li>}
              />
            </ul>
          </div>
        )}
      />

      <p id="uri-text">Ontology IRI: <tt>{props.nodeIRI}</tt></p>

      <p>Send result to path search:</p>
      <ButtonGroup color="primary" size="small" aria-label="small outlined button group">
        <Button>Start node</Button>
        <Button>End node</Button>
      </ButtonGroup>
    </div>
  );
}

export default NodeResult;