import React from 'react';
import ButtonGroup from '@mui/material/ButtonGroup';
import Button from '@mui/material/Button';
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
  Grid,
  adaptV4Theme,
} from '@mui/material';

import { useAppDispatch } from '../redux/hooks';
import { setRelStartNode } from '../features/relationshipSlice';
import { setPathStartNodeId, setPathEndNodeId, setPathStartNodeName, setPathEndNodeName } from '../features/pathSlice';
import NodeLabel from './NodeLabel';
import { Box, createTheme } from '@mui/material';
import { ThemeProvider } from '@mui/styles';
import { StyledEngineProvider } from '@mui/material';
import FileCopyIcon from '@mui/icons-material/FileCopy';
import { setExpandNetworkNode, setShortestPathEndNode, setShortestPathStartNode } from '../features/modulesSlice';

const nodeResultTheme = createTheme(adaptV4Theme({
  typography: {
    fontFamily: [
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif'
    ].join(','),
  },
}));

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

  const handleSetExpandNetworkNode = () => {
    dispatch(setExpandNetworkNode(nodeNeo4jID));
  }

  const handleSetShortestPathStartNode = () => {
    dispatch(setShortestPathStartNode(nodeNeo4jID));
  }

  const handleSetShortestPathEndNode = () => {
    dispatch(setShortestPathEndNode(nodeNeo4jID));
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

  return (
    <StyledEngineProvider injectFirst>
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

          <p id="uri-text"><Typography>ComptoxAI Node ID: <tt>{nodeNeo4jID}</tt></Typography></p>
          <p id="uri-text"><Typography>Ontology IRI: <tt>{nodeIRI}</tt></Typography></p>

          <Typography>Actions:</Typography>

          <ButtonGroup color="primary" size="small" aria-label="small outlined button group">
            <Button onClick={handleRelSearch}>
              Load relationships
            </Button>
          </ButtonGroup>

          <ButtonGroup color="primary" size="small" style={{marginLeft: '12px'}}>
            <Button onClick={handleSetPathStartNode}>Path start node</Button>
            <Button onClick={handleSetPathEndNode}>Path end node</Button>
          </ButtonGroup>

          <br/>

          <ButtonGroup color="primary" size="small" style={{marginTop: '10px'}}>
            <Button onClick={handleSetShortestPathStartNode}>Shortest Path (start)</Button>
            <Button onClick={handleSetShortestPathEndNode}>Shortest Path (end)</Button>
          </ButtonGroup>
          <ButtonGroup color="primary" size="small" style={{marginLeft: '12px'}}>
            <Button onClick={handleSetExpandNetworkNode}>Expand network</Button>
          </ButtonGroup>
        </Box>
      </ThemeProvider>
    </StyledEngineProvider>
  );
}

export default NodeResult;