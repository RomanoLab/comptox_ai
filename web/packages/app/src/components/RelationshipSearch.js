import React from 'react';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import TextField from '@material-ui/core/TextField';
import Autocomplete from '@material-ui/lab/Autocomplete';
import CheckBoxOutlineBlankIcon from '@material-ui/icons/CheckBoxOutlineBlank';
import CheckBoxIcon from '@material-ui/icons/CheckBox';

const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;

const relTypes = [
  { type: 'CHEMICAL_BINDS_GENE' },
];

class RelationshipSearch extends React.Component {
  render() {
    return(
      <div>
        <h2>Search for a relationship</h2>
        <p>
          <i>Relationships are associations or other conceptual links between any two entities in the graph database. For example, a relationship may represent a chemical interacting with a gene, or a symptom manifesting a disease.</i>
        </p>
        <TextField
          id="startNodeValue"
          label="Start node"
          variant="outlined"
          style={{ width: 500, paddingBottom: 8 }}
        />
        <Autocomplete
          multiple
          id="relationship-types-tags"
          options={relTypes}
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
            <TextField {...params} variant="outlined" label="Relationship Type" placeholder="Type" />
          )}
        />
        <TextField
          id="endNodeValue"
          label="End node"
          variant="outlined"
          style={{ width: 500, paddingBottom: 8 }}
        />
        <br/>
        <Button variant="contained" color="primary">Search</Button>
      </div>
    );
  }
}

export default RelationshipSearch;