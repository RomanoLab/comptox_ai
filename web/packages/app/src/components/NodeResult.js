import React from 'react';
import { IsEmpty } from 'react-lodash';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Button from '@material-ui/core/Button';
import { Dialog, DialogContent, DialogContentText } from '@material-ui/core';

import { useAppDispatch } from '../redux/hooks';
import { setRelStartNode } from '../features/relationshipSlice';
import NodeLabel from './NodeLabel';
import { Box, createMuiTheme } from '@material-ui/core';
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

  const [popupOpen, setPopupOpen] = React.useState(false);

  const { config } = props;

  const handleRelSearch = () => {
    dispatch(setRelStartNode(nodeNeo4jID));
  }

  const handleCopyJson = () => {
    // see: https://stackoverflow.com/a/58406346/1730417
    let selBox = document.createElement('textarea');
    selBox.style.position = 'fixed';
    selBox.style.left = '0';
    selBox.style.top = '0';
    selBox.style.opacity = '0';
    selBox.value = JSON.stringify(props);
    document.body.appendChild(selBox);
    selBox.focus();
    selBox.select();
    document.execCommand('copy');
    document.body.removeChild(selBox);
    setPopupOpen(true);
  };

  const handleClose = () => {
    setPopupOpen(false);
  };

  const getXrefDisplayString = xrefName => {
    return config.nodeConfig.translateIdType[xrefName]
  }

  return(
    <ThemeProvider theme={theme}>
      <Box
        border={2}
        borderRadius="4px"
        borderColor="grey.500"
        p={1}
      >
        <span style={{textAlign: 'left'}}>Node details:</span><Button onClick={handleCopyJson} style={{float: 'right'}}>Copy JSON</Button>
        <Dialog
          open={popupOpen}
          onClose={handleClose}
          aria-labelledby="json-copy-alert"
          aria-describedby="json data copied to clipboard"
        >
          <DialogContent>
            <DialogContentText>JSON data for the selected node has been copied to the clipboard.</DialogContentText>
          </DialogContent>
        </Dialog>
        
        <p>Data type(s): <NodeLabel nodeType={nodeType}/> Name: <span className="node-name">{nodeName}</span></p>

        <IsEmpty
          value={nodeIDs}
          yes="No external IDs found"
          no={() => (
            <div>
              External Identifiers:
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

        <ButtonGroup color="primary" size="small" aria-label="small outlined button group">
          <Button onClick={handleRelSearch}>
            View relationships
          </Button>
        </ButtonGroup>

        <ButtonGroup color="primary" size="small">
          <Button>Path start node</Button>
          <Button>Path end node</Button>
        </ButtonGroup>
      </Box>
    </ThemeProvider>
  );
}

export default NodeResult;