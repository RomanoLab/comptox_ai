import React from 'react';
import TextField from '@material-ui/core/TextField';

class PathSearch extends React.Component {
  render() {
    return(
      <div>
        <h2>Search for a path</h2>
        <p>
          <i>Paths are chains of two or more nodes in the graph database along with the relationships that link them.</i>
        </p>
        <TextField
          id="startNodeValue"
          label="Start node"
          variant="outlined"
          style={{ width: 500, paddingBottom: 8 }}
        />
        <TextField
          id="endNodeValue"
          label="End node"
          variant="outlined"
          style={{ width: 500, paddingBottom: 8 }}
        />
      </div>
    );
  }
}

export default PathSearch;
