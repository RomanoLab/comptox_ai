import React from 'react';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Button from '@material-ui/core/Button';
import { 
  Dialog,
  DialogContent,
  DialogContentText,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Paper,
  Grid
} from '@material-ui/core';

import { useAppDispatch } from '../redux/hooks';
import { setRelStartNode } from '../features/relationshipSlice';
import { setPathStartNodeId, setPathEndNodeId, setPathStartNodeName, setPathEndNodeName } from '../features/pathSlice';
import NodeLabel from './NodeLabel';
import { Box, createMuiTheme } from '@material-ui/core';
import { ThemeProvider } from '@material-ui/styles';
import FileCopyIcon from '@material-ui/icons/FileCopy';

const nodeResultTheme = createMuiTheme({
  typography: {
    fontFamily: [
      // '-apple-system',
      // 'BlinkMacSystemFont',
      // '"Segoe UI"',
      // 'Roboto',
      // '"Helvetica Neue"',
      // 'Arial',
      // 'sans-serif',
      // '"Apple Color Emoji"',
      // '"Segoe UI Emoji"',
      // '"Segoe UI Symbol"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif'
    ].join(','),
  },
});

const NodeResult = (props) => {
  const { nodeType, nodeName, nodeIRI, nodeIDs, nodeNeo4jID, nodeFeatures } = props;
  const dispatch = useAppDispatch();

  const [popupOpen, setPopupOpen] = React.useState(false);

  const { config } = props;

  const handleRelSearch = () => {
    dispatch(setRelStartNode(nodeNeo4jID));
  }

  const handleSetPathStartNode = () => {
    dispatch(setPathStartNodeId(nodeNeo4jID));
    dispatch(setPathStartNodeName(nodeName));
  }

  const handleSetPathEndNode = () => {
    dispatch(setPathEndNodeId(nodeNeo4jID));
    dispatch(setPathEndNodeName(nodeName));
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
    <ThemeProvider theme={nodeResultTheme}>
      <Box
        border={2}
        borderRadius="4px"
        borderColor="grey.500"
        p={1}
      >
        {/* <span style={{textAlign: 'left'}}><Typography display="inline">Node details:</Typography></span> */}
        <Typography variant='h6' display="inline" color='textSecondary'>Node details:</Typography>
        <Button
          onClick={handleCopyJson}
          style={{float: 'right'}}
          variant="outlined"
        >
          <FileCopyIcon color="action"/>{'\u00A0'}Copy JSON
        </Button>
        <Dialog
          open={popupOpen}
          onClose={handleClose}
          aria-labelledby="json-copy-alert"
          aria-describedby="json data copied to clipboard"
        >
          <DialogContent>
            <DialogContentText>Node data copied to the clipboard.</DialogContentText>
          </DialogContent>
        </Dialog>
        
        <p>
          <NodeLabel nodeType={nodeType} nodeName={nodeName}/>
        </p>

        <Grid container spacing={1}>
          <Grid item xs={6}>
            <Typography style={{marginLeft:'3px'}}>External Identifiers:</Typography>
            <Paper>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell style={{fontWeight:'bold'}}>Database</TableCell>
                    <TableCell style={{fontWeight:'bold'}}>Identifier</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {nodeIDs.map((row) => (
                    <TableRow key={row.idType}>
                      <TableCell>{getXrefDisplayString(row.idType)}</TableCell>
                      <TableCell>{row.idValue}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Paper>
          </Grid>

          <Grid item xs={6}>
            <Typography style={{marginLeft:'3px'}}>Other node features:</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell style={{minWidth:'100px',fontWeight:'bold'}}>Feature name</TableCell>
                    <TableCell style={{fontWeight:'bold'}}>Value</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {nodeFeatures.map((row) => (
                    <TableRow key={row.featType}>
                      <TableCell>{row.featType}</TableCell>
                      <TableCell>{row.featValue}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Grid>

        <p id="uri-text"><Typography>Ontology IRI: <tt>{nodeIRI}</tt></Typography></p>

        <ButtonGroup color="primary" size="small" aria-label="small outlined button group">
          <Button onClick={handleRelSearch}>
            Load relationships
          </Button>
        </ButtonGroup>

        <ButtonGroup color="primary" size="small" style={{marginLeft: '12px'}}>
          <Button onClick={handleSetPathStartNode}>Path start node</Button>
          <Button onClick={handleSetPathEndNode}>Path end node</Button>
        </ButtonGroup>
      </Box>
    </ThemeProvider>
  );
}

export default NodeResult;