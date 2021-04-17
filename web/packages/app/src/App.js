import React from 'react';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import TextField from '@material-ui/core/TextField';
import Autocomplete from '@material-ui/lab/Autocomplete';
import CheckBoxOutlineBlankIcon from '@material-ui/icons/CheckBoxOutlineBlank';
import CheckBoxIcon from '@material-ui/icons/CheckBox';
import './App.css';

const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;

const nodeTypes = [
  { type: 'Chemical' },
  { type: 'Gene' },
  { type: 'Disease' }
];

class SearchNode extends React.Component {
  render() {
    return(
      <div>
        <h2>Search for a node</h2>
        <p>
          <i>A node is an individual entity in ComptoxAI's graph database. For example, individual genes, diseases, and chemicals are all represented as nodes in the graph database.</i>
        </p>
        <Autocomplete
          multiple
          id="node-types-tags"
          options={nodeTypes}
          disableCloseOnSelect
          getOptionLabel={(option) => option.type}
          renderOption={(option, { selected }) => (
            <React.Fragment>
              <Checkbox
                icon={icon}
                checkedIcon={checkedIcon}
                style={{ marginRight: 8 }}
                checked={selected}
              />
              {option.type}
            </React.Fragment>
          )}
          style={{ width: 500 }}
          renderInput={(params) => (
            <TextField {...params} variant="outlined" label="Node Types" placeholder="Types" />
          )}
        />
        <TextField
          id="nodeIdValue"
          label="Value"
          variant="outlined"
          style={{ width: 500 }}
        />
        <Button variant="contained" color="primary">Search</Button>
      </div>
    );
  }
}

class SearchRelationship extends React.Component {
  render() {
    return(
      <div>
        <h2>Search for a relationship</h2>
        <p>
          <i>Relationships are associations or other conceptual links between any two entities in the graph database. For example, a relationship may represent a chemical interacting with a gene, or a symptom manifesting a disease.</i>
        </p>
      </div>
    );
  }
}

class SearchPath extends React.Component {
  render() {
    return(
      <div>
        <h2>Search for a path</h2>
        <p>
          <i>Paths are chains of two or more nodes in the graph database along with the relationships that link them.</i>
        </p>
      </div>
    );
  }
}

class FetchBatch extends React.Component {
  render() {
    return(
      <div>
        <h2>Bulk data fetch</h2>
        <p>
          This tool is used to retrieve node and/or relationship properties for many nodes or relationships simultaneously.
        </p>
      </div>
    );
  }
}

function App() {
  return (
    <div className="App">
      <body>
        <h1>ComptoxAI interactive data portal</h1>
        <SearchNode />
        <SearchRelationship />
        <SearchPath />
        <FetchBatch />
      </body>
    </div>
  );
}

export default App;
