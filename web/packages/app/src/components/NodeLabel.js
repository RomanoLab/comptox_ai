import { Avatar, Chip, Typography } from '@material-ui/core';
import React from 'react';

const colorMap = {
  "Chemical": '#ff5252',
  "Gene": '#c158dc',
  "Pathway": '#6f74dd',
  "KeyEvent": '#039be5',
  "MolecularInitiatingEvent": '#4ebaaa',
  "AdverseOutcome": '#aee571',
  "AOP": '#fdd835',
  "Assay": '#8eacbb',
}

const NodeLabel = (props) => {
  const bgcolor = colorMap[props.nodeType];
  const avatar = props.nodeType.charAt(0);
  
  return(
    <div style={{marginLeft:'6px'}}>
      <Chip
        variant="outlined"
        size="small"
        label={props.nodeType}
        style={{backgroundColor:bgcolor, marginBottom:'7px'}}
        avatar={<Avatar>{avatar}</Avatar>}
      />
      <Typography 
        display="inline"
        variant='h5'
        style={{marginLeft:'6px'}}
      >
        {props.nodeName}
      </Typography>
    </div>
  );
}

export default NodeLabel;
