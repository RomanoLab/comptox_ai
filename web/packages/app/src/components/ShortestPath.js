import React from 'react';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Button,
  Dialog,
  DialogContent,
  DialogContentText,
  TextField,
  Typography,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FileCopyIcon from '@mui/icons-material/FileCopy';

import { useAppSelector } from '../redux/hooks';

import endent from 'endent';

const ShortestPath = (props) => {
  const shortestPathStartNodeId = useAppSelector(
    (state) => state.modules.shortestPathStart
  );
  const shortestPathEndNodeId = useAppSelector(
    (state) => state.modules.shortestPathEnd
  );

  const startNodeId = shortestPathStartNodeId ? shortestPathStartNodeId : null;
  const endNodeId = shortestPathEndNodeId ? shortestPathEndNodeId : null;
  const boxDisabled = startNodeId === null ?? endNodeId === null;

  const shortestPathCypherQuery =
    startNodeId && endNodeId
      ? endent(`MATCH
        (n1), (n2), p= allShortestPaths((n1)-[*]-(n2))
    WHERE
        id(n1) = ${startNodeId} AND
        id(n2) = ${endNodeId}
    RETURN p;`)
      : "Select a 'start' and an 'end' node using Node Search (above).";

  const [popupOpen, setPopupOpen] = React.useState(false);

  const handleCopyCypher = () => {
    // see: https://stackoverflow.com/a/58406346/1730417
    let selBox = document.createElement('textarea');
    selBox.style.position = 'fixed';
    selBox.style.left = '0';
    selBox.style.top = '0';
    selBox.style.opacity = '0';
    selBox.value = shortestPathCypherQuery;
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
    <div className="shortestPath subject-container">
      <div className="shortestPathHeader">
        <h2>Make all shortest paths query</h2>
        <p>
          <i>
            Create a Cypher query to find the set of all shortest paths linking
            two nodes in the knowledge base.
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
                Find a starting node using the search feature at the top of the
                page, and click "Shortest Path (Start)".
              </li>
              <li>
                Find an ending node using the search feature at the top of the
                page, and click "Shortest Path (End)".
              </li>
              <li>
                Click the "Copy Database Query" button below to copy the query
                to your clipboard.
              </li>
              <li>
                Click the "Open Database Browser" button below to open the Neo4j
                interface.
              </li>
              <li>Paste the contents in the query bar and run the search.</li>
            </ol>
          </AccordionDetails>
        </Accordion>
        <TextField
          type="text"
          defaultValue={shortestPathCypherQuery}
          value={shortestPathCypherQuery}
          multiline
          rows={6}
          inputProps={{
            readOnly: true,
            style: { fontFamily: 'monospace' },
          }}
          style={{ width: '100%' }}
          variant="outlined"
          disabled={boxDisabled}
        />
        <Button
          onClick={handleCopyCypher}
          variant="outlined"
          disabled={boxDisabled}
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

export default ShortestPath;
