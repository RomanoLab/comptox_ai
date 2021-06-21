import React from 'react';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import TextField from '@material-ui/core/TextField';
import Autocomplete from '@material-ui/lab/Autocomplete';
import CheckBoxOutlineBlankIcon from '@material-ui/icons/CheckBoxOutlineBlank';
import CheckBoxIcon from '@material-ui/icons/CheckBox';

import NodeResult from './NodeResult';

const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;

const nodeTypes = [
  { type: 'Chemical' },
  { type: 'Gene' },
  { type: 'Disease' },
  { type: 'Adverse Outcome Pathway' },
  { type: 'Key Event' },
  { type: 'Molecular Initiating Event' }
];

class NodeSearch extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      // nodeData: this.props.nodeData
      nodeData: this.props.nodeResults
    }
  }
  
  render() {
    return(
      <div class="node-search">
        <h2>Search for a node</h2>
        <p>
          <i>A node is an individual entity in ComptoxAI's graph database. For example, individual genes, diseases, and chemicals are all represented as nodes in the graph database.</i>
        </p>
        <Autocomplete
          // multiple
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
          size="small"
          renderInput={(params) => (
            <TextField {...params} variant="outlined" label="Node Types" placeholder="Types" />
          )}
        />
        <TextField
          id="nodeField"
          label="Search field"
          variant="outlined"
          size="small"
          style={{ width: 500, paddingBottom: 8 }}
        />
        <TextField
          id="nodeValue"
          label="Value"
          variant="outlined"
          size="small"
          style={{ width: 500, paddingBottom: 8 }}
        />
        <br/>
        <Button variant="contained" color="primary">Search</Button>
        {!(this.state.nodeData === undefined) &&
        <NodeResult
          nodeType={this.state.nodeData[0].nodeType}
          nodeName={this.state.nodeData[0].commonName}
          nodeIDs={this.state.nodeData[0].identifiers}
          nodeIRI={this.state.nodeData[0].ontologyIRI}
        />
        }
      </div>
    );
  }
}

export default NodeSearch;
