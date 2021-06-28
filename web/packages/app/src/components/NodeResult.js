import React from 'react';
import { IsEmpty } from 'react-lodash';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Button from '@material-ui/core/Button';

import { useAppDispatch } from '../redux/hooks';
import { setRelStartNode } from '../features/relationshipSlice';
import NodeLabel from './NodeLabel';
import { createMuiTheme } from '@material-ui/core';
import { ThemeProvider } from '@material-ui/styles';
import { List, ListItem, ListItemText } from '@material-ui/core';

const theme = createMuiTheme({
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
      '"Apple Color Emoji"',
      '"Segoe UI Emoji"',
      '"Segoe UI Symbol"',
    ].join(','),
  },
});

const NodeResult = (props) => {
  const { nodeType, nodeName, nodeIRI, nodeIDs, nodeNeo4jID } = props;
  const dispatch = useAppDispatch();

  const { config } = props;

  const handleRelSearch = event => {
    dispatch(setRelStartNode(nodeNeo4jID));
  }

  const getXrefDisplayString = xrefName => {
    return config.nodeConfig.translateIdType[xrefName]
  }

  return(
    <ThemeProvider theme={theme}>
      <div className="node-detail">
        <p>Data type(s): <NodeLabel nodeType={nodeType}/></p>
        <p>Name: <span className="node-name">{nodeName}</span></p>

        <IsEmpty
          value={nodeIDs}
          yes="No external IDs found"
          no={() => (
            <div>
              <p>Hello there</p>
              <List dense={true}>
                {nodeIDs.map((i) => (
                  <ListItem>
                    <ListItemText
                      primary={
                        <span>{getXrefDisplayString(i.idType)}: {i.idValue}</span>
                      }
                    />
                  </ListItem>
                ))
                }
              </List>
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
    </ThemeProvider>
  );
}

export default NodeResult;