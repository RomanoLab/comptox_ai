import React from 'react';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import TextField from '@material-ui/core/TextField';
import Autocomplete from '@material-ui/lab/Autocomplete';
import CheckBoxOutlineBlankIcon from '@material-ui/icons/CheckBoxOutlineBlank';
import CheckBoxIcon from '@material-ui/icons/CheckBox';
import { Map } from 'react-lodash';

import NodeResult from './NodeResult';
import { useAppSelector } from '../redux/hooks';

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

function NodeSearch() {
  const results = useAppSelector((state) => state.node.searchResults);

  return(
    <div className="node-search">
      <h2>Nodes</h2>
      <h3>Search</h3>
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
      <h3>Search Results</h3>
      {!(results.length === 0) &&
      <Map
        collection={results}
        iteratee={r => (
          <NodeResult
            nodeType={r.nodeType}
            nodeName={r.commonName}
            nodeIDs={r.identifiers}
            nodeIRI={r.ontologyIRI}
          />
        )}
      />
      }
    </div>
  );
}

export default NodeSearch;
