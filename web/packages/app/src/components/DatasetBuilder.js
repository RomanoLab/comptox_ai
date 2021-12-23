import React, { useReducer, useState } from 'react';

import {
  Collapse,
  Container,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Switch,
  TextField
} from '@material-ui/core';
import Autocomplete from '@material-ui/lab/autocomplete';


const formReducer = (state, event) => {
  return {
    ...state,
    [event.name]: event.value
  }
}

const DatasetBuilderQueryForm = (props) => {
  const { config, chemLists } = props;

  const [formData, setFormData] = useReducer(formReducer, {});

  const [checked, setChecked] = React.useState(false);

  //const chemicalFields = config.nodeConfig.nodeLabelProperties['Chemical'];
  const chemicalFields = [
    {
      "property": "commonName",
      "display": "Chemical Name"
    },
    {
      "property": "uri",
      "display": "Ontology URI"
    },
    {
      "property": "xrefCasRN",
      "display": "CAS Registry Number"
    },
    {
      "property": "xrefDTXSID",
      "display": "DSSTOX ID"
    },
    {
      "property": "xrefPubchemCID",
      "display": "PubChem CID"
    },
    {
      "property": "xrefPubchemSID",
      "display": "PubChem SID"
    }
  ];

  const handleChange = event => {
    console.log(event);
    setFormData({
      name: event.target.name,
      value: event.target.value,
    });
  }
  
  const handleSubmit = event => {
    event.preventDefault();
  }

  const handleToggleChemFilter = () => {
    setChecked((prev) => !prev);
  };

  return (
    <form onSubmit={handleSubmit}>

      <Container>
        <FormControlLabel
          control={<Switch color="primary" checked={checked} onChange={handleToggleChemFilter} />}
          label="Filter Chemicals"
          style={{ paddingBottom: 8 }}
        />
        <Collapse in={checked}>

          <Grid container spacing={3} style={{ paddingBottom: 8 }}>
            <Grid item xs={2}>
              <FormControl
                variant="outlined"
                size="small"
                // style={{ width: '20%', paddingBottom: 8, paddingRight: 8 }}
                style={{ width: '100%' }}
              >
                <InputLabel id="select-outlined-label-filter-prop">Filter by...</InputLabel>
                <Select
                  name="chemicalFilterPropertySelect"
                  label="Filter by..."
                  labelId="select-outlined-label-filter-prop"
                  onChange={handleChange}
                  value={formData.chemicalFilterPropertySelect || ''}
                  defaultValue=""
                >
                  {chemicalFields.map((cf) => (
                    <MenuItem value={cf.property}>{cf.display}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={1}>
              <FormControl
                variant="outlined"
                size="small"
                style={{ width: '100%' }}
              >
                <Select
                  defaultValue="="
                >
                  <MenuItem value="=">=</MenuItem>
                  <MenuItem value="contains">contains</MenuItem>
                  <MenuItem value="not">not</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={9}>
              <FormControl
                variant="outlined"
                size="small"
                style={{ width: '100%' }}
              >
                {/* <InputLabel id="select-outlined-label-filter-value">Filter value</InputLabel> */}
                <TextField
                  name="chemicalFilterValue"
                  label="Filter value"
                  labelId="select-outlined-label-filter-value"
                  onChange={handleChange}
                  value={formData.chemicalFilterValue || ''}
                  defaultValue=""
                  variant="outlined"
                  size="small"
                />
              </FormControl>
            </Grid>
          </Grid>


          <FormControl
            variant="outlined"
            size="small"
            style={{ width: '100%'}}
          >
            {/* <InputLabel id="select-outlined-label-chemicallist">Chemical List</InputLabel>
            <Select
              name="selectChemicalList"
              label="Chemical List"
              labelId="select-outlined-label-chemicallist"
              onChange={handleChange}
              value={formData.chemicalListSelect}
            /> */}
            <Autocomplete
              id="autocomplete-outlined-chemicallist"
              options={chemLists}
              getOptionLabel={(option) => option.listName}
            />
          </FormControl>

        </Collapse>
      </Container>
    </form>
  )
}

const DatasetBuilder = (props) => {
  const { config, chemLists } = props;

  return(
    <div className="datasetBuilder">
      <div className="datasetBuilderHeader">
        <h2>Build QSAR Dataset</h2>
        <p><i>Build a new dataset to use in Quantitative Structure Activity Relationship modeling.</i></p>
      </div>
      <div className="datasetBuilderQuery">
        <h3>Dataset options</h3>
        <div className="formWrapper">

          <DatasetBuilderQueryForm
            config={config}
            chemLists={chemLists}
          />

        </div>
      </div>
      <div className="datasetBuilderResults">
        <h3>Download available dataset</h3>
        <p><i>Datasets will be available to download for 1 hour after creation.</i></p>
      </div>
    </div>
  );
}

export default DatasetBuilder;
