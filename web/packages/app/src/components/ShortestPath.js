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
    Typography
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FileCopyIcon from '@mui/icons-material/FileCopy';

const placeholderText = `MATCH 
    (d:Disease {commonName: "Non-alcoholic Fatty Liver Disease"}),
    (c:Chemical {commonName: "PFOA"}),
    p= allShortestPaths((d)-[*]-(c))
RETURN p;`;

const ShortestPath = (props) => {
    const [popupOpen, setPopupOpen] = React.useState(false);
    
    const handleCopyCypher = () => {
        // see: https://stackoverflow.com/a/58406346/1730417
        let selBox = document.createElement('textarea');
        selBox.style.position = 'fixed';
        selBox.style.left = '0';
        selBox.style.top = '0';
        selBox.style.opacity = '0';
        selBox.value = placeholderText;
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

    return(
        <div className="shortestPath">
            <div className="shortestPathHeader">
                <h2>Make shortest path query</h2>
                <p><i>Create a Cypher query to find the set of shortest paths linking two nodes in the knowledge base.</i></p>
                <Accordion
                    style={{margin: '6px'}}
                >
                    <AccordionSummary
                        expandIcon={<ExpandMoreIcon />}
                        aria-controls="shortestpathhelp-content"
                        id="shortestpathhelp-header"
                    >
                        <Typography>Usage instructions</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <ol>
                            <li>Find a node using the search feature at the top of the page, and click "Send to shortest path".</li>
                            <li>Click the "Copy Database Query" button below to copy the query to your clipboard.</li>
                            <li>Click the "Open Database Browser" button below to open the Neo4j interface.</li>
                            <li>Paste the contents in the query bar and run the search.</li>
                        </ol>
                    </AccordionDetails>
                </Accordion>
                <TextField
                    type='text'
                    defaultValue={placeholderText}
                    multiline
                    rows={5}
                    inputProps={{
                            readOnly: true,
                            style: {fontFamily: 'monospace'}
                    }}
                    style={{width: '100%'}}
                    variant="outlined"
                />
                <Button
                    onClick={handleCopyCypher}
                    variant="outlined"
                >
                    <FileCopyIcon color="action"/>{'\u00A0'}Copy database query
                </Button>
                <Button
                    onClick={() => openInNewTab('http://neo4j.comptox.ai/browser/')}
                    variant="outlined"
                    style={{margin:'4px'}}
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
                        <DialogContentText>Cypher database query copied to the clipboard.</DialogContentText>
                    </DialogContent>
                </Dialog>
            </div>
        </div>
    );
}

export default ShortestPath;
