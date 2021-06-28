import React from 'react';

const NodeLabel = (props) => {
  return(
    <span className="node-label">
      {props.nodeType}
    </span>
  );
}

export default NodeLabel;
