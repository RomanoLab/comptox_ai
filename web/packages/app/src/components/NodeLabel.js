import { Box } from '@material-ui/core';
import React from 'react';


const NodeLabel = (props) => {
  return(
    // <span className="node-label">
    //   {props.nodeType}
    // </span>
    <Box
      component="span"
      border={1}
      borderRadius={10}
      borderColor="primary.main"
      p={0.3}
      m="auto"
    >
      {props.nodeType}
    </Box>
  );
}

export default NodeLabel;
