import React from 'react';
import { IsEmpty, Map } from 'react-lodash';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Button from '@material-ui/core/Button';

class NodeResult extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      nodeType: props.nodeType,
      nodeName: props.nodeName,
      nodeIDs: props.nodeIDs,
      nodeIRI: props.nodeIRI
    }
  }

  render() {
    return(
      <div className="node-detail">
        <p>Data type(s): {this.state.nodeType}</p>
        <p>Name: <span class="node-name">{this.state.nodeName}</span></p>
        <IsEmpty
          value={this.state.nodeIDs}
          yes="No external IDs found"
          no={() => (
            <div>
              <p>External Identifiers:</p>
              <ul>
                <Map
                  collection={this.state.nodeIDs}
                  iteratee={i => <li key={i}>{i}</li>}
                />
              </ul>
            </div>
          )}
        />
        {/* <p>Send result to relationship search:</p>
        <ButtonGroup color="primary" size="small" aria-label="small outlined button group">
          <Button>Start node</Button>
          <Button>End node</Button>
        </ButtonGroup> */}
        <p id="uri-text">Ontology IRI: <tt>{this.state.nodeIRI}</tt></p>
        <p>Send result to path search:</p>
        <ButtonGroup color="primary" size="small" aria-label="small outlined button group">
          <Button>Start node</Button>
          <Button>End node</Button>
        </ButtonGroup>
      </div>
    );
  }
}

export default NodeResult;