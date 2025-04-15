import React from 'react';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FileCopyIcon from '@mui/icons-material/FileCopy';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Button,
  Dialog,
  DialogContent,
  DialogContentText,
  TextField,
  Typography
} from '@mui/material';
import endent from 'endent';

import { useAppSelector } from '../redux/hooks';

const ExpandNetwork = (props) => {
  const expandNetworkNode = useAppSelector(
    (state) => state.modules.expandNetworkNode
  );

  const selectedNodeId = expandNetworkNode ? expandNetworkNode : null;

  const expandNetworkCypherQuery = selectedNodeId
    ? endent(`CALL apoc.path.spanningTree(
        ${selectedNodeId},
        {
            maxLevel: 3
        })
    YIELD path
    RETURN path;`)
    : 'Find a node in the search interface and select \'Expand Network\'.';

  const [popupOpen, setPopupOpen] = React.useState(false);

  const handleCopyCypher = () => {
    // see: https://stackoverflow.com/a/58406346/1730417
    let selBox = document.createElement('textarea');
    selBox.style.position = 'fixed';
    selBox.style.left = '0';
    selBox.style.top = '0';
    selBox.style.opacity = '0';
    selBox.value = expandNetworkCypherQuery;
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

  const openInNewTab = (url) => {
    const newWindow = window.open(url, '_blank', 'noopener,noreferrer');
    if (newWindow) newWindow.opener = null;
  };

  return (
    <div id="expand-network" className="subject-container">
      <div className="expandNetworkHeader">
        <h2>Expand a network around a query node</h2>
        <p>
          <i>
            Create a Cypher query that builds a spanning tree outward from a
            starting node, showing their local neighborhood in the overall
            knowledge graph.
          </i>
        </p>
        <Accordion style={{ margin: '6px' }}>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="shortestpathhelp-content"
            id="shortestpathhelp-header"
          >
            <Typography>Usage instructions</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <ol>
              <li>
                Find a node using the search feature at the top of the page, and
                click &quot;Expand Network&quot;.
              </li>
              <li>
                Click the &quot;Copy Database Query&quot; button below to copy the query
                to your clipboard.
              </li>
              <li>
                Click the &quot;Open Database Browser&quot; button below to open the Neo4j
                interface.
              </li>
              <li>Paste the contents in the query bar and run the search.</li>
            </ol>
          </AccordionDetails>
        </Accordion>
        <TextField
          type="text"
          defaultValue={expandNetworkCypherQuery}
          value={expandNetworkCypherQuery}
          multiline
          rows={7}
          inputProps={{
            readOnly: true,
            style: { fontFamily: 'monospace' }
          }}
          style={{ width: '100%' }}
          variant="outlined"
          disabled={selectedNodeId == null}
        />
        <Button
          onClick={handleCopyCypher}
          variant="outlined"
          disabled={selectedNodeId == null}
        >
          <FileCopyIcon color="action" />
          {'\u00A0'}Copy database query
        </Button>
        <Button
          onClick={() => openInNewTab('http://neo4j.comptox.ai/browser/')}
          variant="outlined"
          style={{ margin: '4px' }}
        >
          Open database browser
        </Button>
        <Dialog
          open={popupOpen}
          onClose={handleClose}
          aria-labelledby="cypher-copy-alert"
          aria-describedby="cypher data copied to clipboard"
        >
          <DialogContent>
            <DialogContentText>
              Cypher database query copied to the clipboard.
            </DialogContentText>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default ExpandNetwork;
