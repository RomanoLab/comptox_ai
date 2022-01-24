import React, { useState } from 'react';
import {
  Button,
  Checkbox,
  Container,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Select,
  TextField
} from '@material-ui/core';
import Autocomplete from '@material-ui/lab/autocomplete';

const qsarBuilderConfig = require('../data/qsar_params_data.json');

const DatasetBuilderQueryForm = (props) => {

  const [chemListValue, setChemListValue] = useState({'acronym': '', 'name': ''});
  const [assayValue, setAssayValue] = useState({'assayId': '', 'assayName': ''});
  const [checkedState, setCheckedState] = useState({ checkedIncludeDiscovery: true });
  const [formatValue, setFormatValue] = useState('json');

  const handleSubmit = event => {
    event.preventDefault();
    // Open new tab with API URL
    window.open(`http://localhost:3000/datasets/makeQsarDataset?assay=${assayValue.assayId}&chemList=${chemListValue.acronym}`);
  }

  const handleToggleCheckbox = (event) => {
    setCheckedState({ ...checkedState, [event.target.name]: event.target.checked });
  };

  return (
    <form onSubmit={handleSubmit}>

      <Container>

        <FormControl
          variant="outlined"
          size="small"
          style={{ width: '100%', paddingBottom: 8 }}
        >
          <Autocomplete
            id="autocomplete-outlined-chemicallist"
            autoComplete
            size="small"
            onChange={(event, newValue) => {
              setChemListValue(newValue);
            }}
            value={chemListValue || null}
            options={qsarBuilderConfig.chemicalLists}
            getOptionLabel={(option) => option.name ? (option.name + " (n=" + option.num_chems + ")") : ''}
            getOptionSelected={(option, value) => option.acronym === value.acronym}
            renderInput={(params) => <TextField {...params} label="EPA Chemical List filter" variant="outlined" />}
          />
        </FormControl>

        <FormControl
          variant="outlined"
          size="small"
          style={{ width: '100%'}}
        >
          <Autocomplete
            id="autocomplete-outlined-assayendpoint"
            size="small"
            autoComplete
            onChange={(event, newValue) => {
              setAssayValue(newValue);
            }}
            value={assayValue || null}
            options={qsarBuilderConfig.assays}
            getOptionLabel={(option) => option.assayId ? (option.assayName + " (id: " + option.assayId + ")") : ''}
            getOptionSelected={(option, value) => option.assayId === value.assayId}
            renderInput={(params) => <TextField {...params} label="Assay endpoint for QSAR" variant="outlined" />}
          />
        </FormControl>

        <br/>
        <FormControl variant="outlined" size="small">
          <InputLabel id="select-outlined-label-format">Format</InputLabel>
          <Select
            name="selectFormat"
            label="Results format"
            labelId="select-outlined-label-format"
            onChange={(event, newValue) => {
              setFormatValue(newValue);
            }}
            value={formatValue}
            defaultValue="json"
            style={{ width: 120 }}
          >
            <MenuItem value="json">JSON</MenuItem>
            <MenuItem value="tsv">TSV</MenuItem>
            <MenuItem value="csv">CSV</MenuItem>
          </Select>
        </FormControl>
        
        <FormControlLabel
          control={
            <Checkbox
              checked={checkedState.checked}
              onChange={handleToggleCheckbox}
              name="checkedIncludeDiscovery"
              color="primary"
            />
          }
          label="Include 'discovery' dataset of chemicals with unknown assay activity"
        />

        <br/>
        <Button variant="contained" color="primary" type="submit" style={{marginRight: 6}}>Build QSAR Dataset</Button>
        <i>(Results will open in a new tab)</i>

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
    </div>
  );
}

export default DatasetBuilder;
