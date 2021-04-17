import React from 'react';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import TextField from '@material-ui/core/TextField';
import Autocomplete from '@material-ui/lab/Autocomplete';
import CheckBoxOutlineBlankIcon from '@material-ui/icons/CheckBoxOutlineBlank';
import CheckBoxIcon from '@material-ui/icons/CheckBox';


const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;

const nodeTypes = [
  { type: 'Chemical' },
  { type: 'Gene' },
  { type: 'Disease' }
];

class NodeSearch extends React.Component {
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
          style={{ width: 500, paddingBottom: 8 }}
          renderInput={(params) => (
            <TextField {...params} variant="outlined" label="Node Types" placeholder="Types" />
          )}
        />
        <TextField
          id="nodeIdValue"
          label="Value"
          variant="outlined"
          style={{ width: 500, paddingBottom: 8 }}
        />
        <br/>
        <Button variant="contained" color="primary">Search</Button>
      </div>
    );
  }
}

export default NodeSearch;
