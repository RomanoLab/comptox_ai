import React, { useReducer } from 'react';

import {
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import makeStyles from '@mui/styles/makeStyles';

import { useAppDispatch } from '../redux/hooks';
import { setSearch } from '../features/nodeSlice';

const formReducer = (state, event) => {
  return {
    ...state,
    [event.name]: event.value,
  };
};

const useStyles = makeStyles((theme) => ({
  root: {
    '& > *': {
      margin: theme.spacing(1),
    },
  },
}));

const NodeSearch = (props) => {
  const { config } = props;
  const [formData, setFormData] = useReducer(formReducer, {});
  const dispatch = useAppDispatch();

  const classes = useStyles();

  const handleSubmit = (event) => {
    event.preventDefault();
    dispatch(
      setSearch({
        searchType: 'node',
        params: {
          label: formData.nodeType,
          field: formData.nodeField,
          value: formData.nodeValue,
        },
      })
    );
  };

  const handleChange = (event) => {
    setFormData({
      name: event.target.name,
      value: event.target.value,
    });
  };

  const handleReset = () => {
    setFormData({
      name: 'nodeType',
      value: '',
    });
    setFormData({
      name: 'nodeField',
      value: '',
    });
    setFormData({
      name: 'nodeValue',
      value: '',
    });
  };

  const handleLoadExampleQuery = (event) => {
    setFormData({
      name: 'nodeType',
      value: 'Gene',
    });
    setFormData({
      name: 'nodeField',
      value: 'geneSymbol',
    });
    setFormData({
      name: 'nodeValue',
      value: 'CYP2E1',
    });
  };

  const fetchNodeFields = (selectedNodeLabel) => {
    if (selectedNodeLabel === undefined) {
      return [];
    } else {
      return config.nodeConfig.nodeLabelProperties[selectedNodeLabel];
    }
  };

  return (
    <div className="node-search subject-container">
      <h2>Nodes</h2>
      <div className="search-header">
        <span className="search-text">Search</span>
        <Button
          variant="outlined"
          color="primary"
          size="small"
          onClick={handleLoadExampleQuery}
        >
          Load example query
        </Button>
      </div>
      <div className="formWrapper">
        <form onSubmit={handleSubmit}>
          <FormControl
            variant="outlined"
            size="small"
            style={{ width: 500, paddingBottom: 8 }}
          >
            <InputLabel id="select-outlined-label-type">Node Type</InputLabel>
            <Select
              labelId="select-outlined-label-type"
              label="Node Type"
              name="nodeType"
              onChange={handleChange}
              value={formData.nodeType || ''}
              defaultValue=""
            >
              {config.nodeConfig.nodeLabels.map((nodeLabel) => (
                <MenuItem value={nodeLabel}>{nodeLabel}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl
            variant="outlined"
            size="small"
            style={{ width: 500, paddingBottom: 8 }}
          >
            <InputLabel id="select-outlined-label-field">Node Field</InputLabel>
            <Select
              name="nodeField"
              label="Search field"
              labelId="select-outlined-label-field"
              onChange={handleChange}
              value={formData.nodeField || []}
              defaultValue=""
            >
              {fetchNodeFields(formData.nodeType).map((nf) => (
                <MenuItem value={nf.property}>{nf.display}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Value"
            variant="outlined"
            size="small"
            style={{ width: 500, paddingBottom: 8 }}
            onChange={handleChange}
            name="nodeValue"
            value={formData.nodeValue || ''}
          />

          <br />
          <div className={classes.root}>
            <Button variant="contained" color="primary" type="submit">
              Search
            </Button>
            <Button variant="contained" color="primary" onClick={handleReset}>
              Clear Form
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NodeSearch;
