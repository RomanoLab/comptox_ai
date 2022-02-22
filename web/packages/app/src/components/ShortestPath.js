import React from 'react';
import {
    TextField
} from '@mui/material';

const placeholderText = `MATCH 
    (d:Disease {commonName: "Non-alcoholic Fatty Liver Disease"}),
    (c:Chemical {commonName: "PFOA"}),
    p= allShortestPaths((d)-[*]-(c))
RETURN p;`;

const ShortestPath = (props) => {
    return(
        <div className="shortestPath">
            <div className="shortestPathHeader">
                <h2>Make shortest path query</h2>
                <p><i>Create a Cypher query to find the set of shortest paths linking two nodes in the knowledge base.</i></p>
                <TextField
                    type='text'
                    defaultValue={placeholderText}
                    multiline
                    rows={5}
                    inputProps={
                        {readOnly: true,}
                    }
                    style={{width: '100%'}}
                    variant="outlined"
                />
            </div>
        </div>
    );
}

export default ShortestPath;
