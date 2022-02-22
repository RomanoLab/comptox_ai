import React from 'react';
import { TextField, createTheme } from '@mui/material';

const placeholderText = `CALL apoc.path.spanningTree(
    879088,
    {
        maxLevel: 5
    })
YIELD path
RETURN path;`;

const monospaceFontTheme = createTheme({

});

const ExpandNetwork = (props) => {
    return(
        <div id="expand-network">
            <div className="expandNetworkHeader">
                <h2>Expand a network around a query node</h2>
                <p><i>Create a Cypher query that builds a spanning tree outward from a starting node, showing their local neighborhood in the overall knowledge graph.</i></p>
                <TextField
                    type='text'
                    defaultValue={placeholderText}
                    multiline
                    rows={7}
                    inputProps={
                        {readOnly: true,}
                    }
                    style={{width: '100%'}}
                    variant="outlined"
                    theme={monospaceFontTheme}
                />
            </div>
        </div>
    );
}

export default ExpandNetwork;
