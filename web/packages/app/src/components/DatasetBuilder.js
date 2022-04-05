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
} from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';

const qsarBuilderConfig = require('../data/qsar_params_data.json');

const DatasetBuilderQueryForm = (props) => {

  const [chemListValue, setChemListValue] = useState({'acronym': '', 'name': ''});
  const [assayValue, setAssayValue] = useState({'assayId': '', 'assayName': ''});
  const [checkedState, setCheckedState] = useState({ checkedIncludeDiscovery: true });
  const [formatValue, setFormatValue] = useState('json');

  const handleSubmit = event => {
    event.preventDefault();
    // Open new tab with API URL (should we refactor to use Redux or is this good enough?)
    window.open(`https://comptox.ai/api/datasets/makeQsarDataset?assay=${assayValue.assayId}&chemList=${chemListValue.acronym}`);
  }

  const handleToggleCheckbox = (event) => {
    setCheckedState({ ...checkedState, [event.target.name]: event.target.checked });
  };

  const handleChangeFormat = (event) => {
    setFormatValue(event.target.value);
  };

  return (
    <form onSubmit={handleSubmit}>

      <Container>

        <FormControl
          variant="outlined"
          size="small"
          style={{ width: '100%', paddingBottom: 10 }}
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
            isOptionEqualToValue={(option, value) => option.acronym === value.acronym}
            renderInput={(params) => <TextField {...params} label="Filter chemicals by EPA Chemical List (optional)" variant="outlined" />}
          />
        </FormControl>

        <FormControl
          variant="outlined"
          size="small"
          style={{ width: '100%', paddingBottom: 8 }}
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
            isOptionEqualToValue={(option, value) => option.assayId === value.assayId}
            renderInput={(params) => <TextField {...params} label="QSAR assay endpoint" variant="outlined" />}
          />
        </FormControl>

        <br/>
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
          style={{ marginBottom: 6}}
        />

        <br/>
        <FormControl variant="outlined" size="small">
          <InputLabel id="select-outlined-label-format">Format</InputLabel>
          <Select
            name="selectFormat"
            label="Format"
            labelId="select-outlined-label-format"
            onChange={handleChangeFormat}
            value={formatValue}
            defaultValue="json"
            style={{ width: 120, marginRight: 8}}
          >
            <MenuItem value="json">JSON</MenuItem>
            {/* <MenuItem value="tsv">TSV</MenuItem>
            <MenuItem value="csv">CSV</MenuItem> */}
          </Select>
        </FormControl>
        <Button variant="contained" color="primary" type="submit" style={{marginRight: 6, paddingTop: 9}}>Build QSAR Dataset</Button>
        <i>(Results will open in a new tab)</i>

      </Container>
    </form>
  );
}

const DatasetBuilder = (props) => {
  const { config, chemLists } = props;

  return(
    <div className="datasetBuilder">
      <div className="datasetBuilderHeader">
        <h2>Build QSAR Dataset</h2>
        <p><i>Build a new dataset to use in Quantitative Structure-Activity Relationship modeling.</i></p>
      </div>
      <div className="datasetBuilderQuery">
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
