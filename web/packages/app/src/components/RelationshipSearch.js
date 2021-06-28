import React from 'react';
import { Map, IsEmpty } from 'react-lodash';

import { useFetchRelationshipsByNodeIdQuery } from '../features/comptoxApiSlice';
import { useAppSelector } from '../redux/hooks';

const RelationshipSearch = (props) => {
  const selectedRel = useAppSelector((state) => state.relationship.relStartNode)

  const skip = () => {
    
  }
  
  const { data = [] } = useFetchRelationshipsByNodeIdQuery(selectedRel, {
    skip,
  });

  return(
    <div id="rel-search">
      <h2>Relationships</h2>
      <p>
        <i>Search for a node in the box above and click "See relationships" to show all linked nodes.</i>
      </p>
      {/* Show start node (main information only) */}
      <div id="rel-start-node">

      </div>
      {/* Show a list of all linked nodes */}
      <div id="rel-list">
        <Map
          collection={data}
          iteratee={i => (
            <div className="rel-result">
              <p>Start Node: <tt>{i.fromNode.nodeId}</tt></p>
              <p>End Node: <tt>{i.toNode.nodeId}</tt></p>
            </div>
          )}
        />
      </div>
    </div>
  );
}


export default RelationshipSearch;
