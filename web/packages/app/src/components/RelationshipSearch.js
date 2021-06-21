import React from 'react';
import { IsEmpty, Map } from 'react-lodash';


class RelationshipSearch extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      relSubject: props.relationshipResults.startNode,
      relObjects: props.relationshipResults.endNodes
    }
  }
  
  render() {
    return(
      <div id="rel-search">
        <h2>Search for relationships</h2>
        <p>
          Search for a node in the box above and click "Send to relationship search" to see all linked nodes.
        </p>
        {/* Show start node (main information only) */}
        <div id="rel-start-node">

        </div>
        {/* Show a list of all linked nodes */}
        <div id="rel-end-node-list">
          <IsEmpty
            value={this.state.relObjects}
            yes="No relationships found for selected node! This usually means the node is understudied or incorrectly annotated in source databases."
            no={() => (
              <div id="rel-objects">
                <Map
                  collection={this.state.relObjects}
                  iteratee= {i => (
                    <div className="rel-result">
                      <p >Start node: <span className="node-name">{this.state.relSubject.commonName}</span></p>
                      <p className="rel-type">Relationship Type: <span class="tt">{i.relationshipType}</span></p>
                      <p>End node: <span className="node-name">{i.node.commonName}</span></p>
                    </div>
                  )}
                />
              </div>
            )}
          />
        </div>
      </div>
    );
  }
}

export default RelationshipSearch;