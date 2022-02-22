import React from 'react';
import {
    TextField
} from '@mui/material';

const placeholderText = `CALL apoc.path.spanningTree(
    879088,
    {
        maxLevel: 5
    })
YIELD path
RETURN path;`;

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
                    rows={7}
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
