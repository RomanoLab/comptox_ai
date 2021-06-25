import React from 'react';
import PropTypes from 'prop-types';
import { Map } from 'react-lodash';


class RelationshipSearch extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      relationships: props.relationshipResults
    }

  }
  
  render() {
    return(
      <div id="rel-search">
        <h2>Relationships</h2>
        <p>
          Search for a node in the box above and click "Send to relationship search" to see all linked nodes.
        </p>
        {/* Show start node (main information only) */}
        <div id="rel-start-node">

        </div>
        {/* Show a list of all linked nodes */}
        <div id="rel-end-node-list">
          {!(this.state.relationships.length === 0) &&
            <div id="rel-objects">
              <Map
                collection={this.state.relationships}
                iteratee= {i => (
                  <div className="rel-result">
                    <p >Start node: <span className="node-name">{this.state.relSubject.commonName}</span></p>
                    <p className="rel-type">Relationship Type: <span class="tt">{i.relationshipType}</span></p>
                    <p>End node: <span className="node-name">{i.node.commonName}</span></p>
                  </div>
                )}
              />
            </div>
          }
          {/* <IsEmpty
            value={this.state.relationships}
            yes="Empty"
            no={() => (
              <div id="rel-objects">
                <Map
                  collection={this.state.relationships}
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
          /> */}
        </div>
      </div>
    );
  }
}

RelationshipSearch.propTypes = {
  relationships: PropTypes.array
};

RelationshipSearch.defaultProps = {
  relationships: [],
};

export default RelationshipSearch;