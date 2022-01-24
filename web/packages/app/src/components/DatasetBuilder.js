import React, { useState } from 'react';
import {
  Button,
  Container,
  FormControl,
  FormControlLabel,
  Switch,
  TextField
} from '@material-ui/core';
import Autocomplete from '@material-ui/lab/autocomplete';

const qsarBuilderConfig = require('../data/qsar_params_data.json');

const DatasetBuilderQueryForm = (props) => {

  const [chemListValue, setChemListValue] = useState({'acronym': '', 'name': ''});
  const [chemListInputValue, setChemListInputValue] = React.useState('');

  const [assayValue, setAssayValue] = useState({'assayId': '', 'assayName': ''});
  const [assayInputValue, setAssayInputValue] = React.useState('');

  const handleSubmit = event => {
    event.preventDefault();
    // Open new tab with API URL
    window.open(`http://localhost:3000/datasets/makeQsarDataset?assay=${assayValue.assayId}&chemList=${chemListValue.acronym}`);
  }

  return (
    <form onSubmit={handleSubmit}>

      <Container>

        {/* <Grid container spacing={3} style={{ paddingBottom: 8 }}>
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
              <InputLabel id="select-outlined-label-filter-value">Filter value</InputLabel>
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
        </Grid> */}


        <FormControl
          variant="outlined"
          size="small"
          style={{ width: '100%', paddingBottom: 8 }}
        >
          <Autocomplete
            id="autocomplete-outlined-chemicallist"
            // options={chemLists}
            size="small"
            onChange={(event, newValue) => {
              setChemListValue(newValue);
            }}
            inputValue={chemListInputValue}
            onInputChange={(event, newInputValue) => {
              setChemListInputValue(newInputValue);
            }}
            value={chemListValue || ''}
            options={qsarBuilderConfig.chemicalLists}
            getOptionLabel={(option) => (option.name + " (n=" + option.num_chems + ")")}
            getOptionSelected={(option, value) => option.acronym === value.acronym}
            renderInput={(params) => <TextField {...params} label="EPA Chemical List filter" variant="outlined" />}
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
            onChange={(event, newValue) => {
              setAssayValue(newValue);
            }}
            inputValue={assayInputValue}
            onInputChange={(event, newInputValue) => {
              setAssayInputValue(newInputValue)
            }}
            value={assayValue || ''}
            options={qsarBuilderConfig.assays}
            getOptionLabel={(option) => (option.assayName + " (id: " + option.assayId + ")")}
            getOptionSelected={(option, value) => option.assayId === value.assayId}
            renderInput={(params) => <TextField {...params} label="Assay endpoint for QSAR" variant="outlined" />}
          />
        </FormControl>

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
