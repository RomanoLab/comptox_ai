import React, { useReducer, useState } from 'react';
import { Map } from 'react-lodash';

import { Button, TextField, Select, MenuItem, FormControl, InputLabel, Paper } from '@mui/material';

import makeStyles from '@mui/styles/makeStyles';

import NodeResult from './NodeResult';
import { useSearchNodesQuery } from '../features/comptoxApiSlice';

const formReducer = (state, event) => {
  return {
    ...state,
    [event.name]: event.value
  }
}

const submitReducer = (state, event) => {
  return {
    label: event.label,
    field: event.field,
    value: event.value,
  }
}

const useStyles = makeStyles((theme) => ({
  root: {
    '& > *': {
      margin: theme.spacing(1),
    },
  },
}));

// See: https://www.digitalocean.com/community/tutorials/how-to-build-forms-in-react
const NodeSearch = (props) => {
  const { config } = props;
  const [formData, setFormData] = useReducer(formReducer, {});
  const [submitData, setSubmitData] = useReducer(submitReducer, {});

  // eslint-disable-next-line
  const [skip, setSkip] = useState(true); // Don't render search results until we've hit "search" at least once

  const { data = [], error, isLoading, isUninitialized } = useSearchNodesQuery([submitData.label, submitData.field, submitData.value], {
    skip,
  });

  const classes = useStyles()

  const handleSubmit = event => {
    event.preventDefault();
    setSkip(false);
    setSubmitData({
      label: formData.nodeType,
      field: formData.nodeField,
      value: formData.nodeValue,
    })
  }

  const handleChange = event => {
    setFormData({
      name: event.target.name,
      value: event.target.value,
    });
  }

  const handleReset = () => {
    setFormData({
      name: 'nodeType',
      value: ''
    })
    setFormData({
      name: 'nodeField',
      value: ''
    })
    setFormData({
      name: 'nodeValue',
      value: ''
    })
    
    console.log("handleReset:")
    console.log(formData);
  }

  const handleLoadExampleQuery = event => {
    setFormData({
      name: 'nodeType',
      value: 'Gene'
    });
    setFormData({
      name: 'nodeField',
      value: 'geneSymbol'
    });
    setFormData({
      name: 'nodeValue',
      value: 'CYP2E1'
    });
  }

  const fetchNodeFields = selectedNodeLabel => {
    if (selectedNodeLabel === undefined) {
      return []
    } else {
      return config.nodeConfig.nodeLabelProperties[selectedNodeLabel]
    }
  } 

  const handleResetNodeSearch = () => {
    handleReset(); // resets the form
    setSkip(true); // prevents error message from rendering
    setSubmitData({ // clears the results
      label: '',
      field: '',
      value: ''
    })
  }

  return(
    <div className="node-search">
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
          <FormControl variant="outlined" size="small" style={{ width: 500, paddingBottom: 8 }}>
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
          
          <FormControl variant="outlined" size="small" style={{ width: 500, paddingBottom: 8 }}>
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
          
          <br/>
          <div className={classes.root}>
            <Button 
              variant="contained"
              color="primary"
              type="submit"
            >
              Search
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={handleReset}
            >
              Clear Form
            </Button>
          </div>
        </form>
      </div>

      <h3>Search Results</h3>
      {error ? (
        <>Error - the requested node was not found. Please try again with a new query.</>
      ) : isUninitialized ? (
        <>Please enter a search query and click "Search" to find nodes.</>
      ) : isLoading ? (
        <>Loading...</>
      ) : data ? (
        <div>
          <Button 
            onClick={handleResetNodeSearch}
            variant="outlined"
            style={{marginBottom:'6px'}}
          >
            Clear node search results
          </Button>
          <Paper>
            <Map
              collection={data}
              iteratee={r => (
                <NodeResult
                  nodeType={r.nodeType}
                  nodeName={r.commonName}
                  nodeIDs={r.identifiers}
                  nodeIRI={r.ontologyIRI}
                  nodeNeo4jID={r.nodeId}
                  nodeFeatures={r.nodeFeatures}
                  config={config}
                />
              )}
            />
          </Paper>
        </div>
      ) : null}
    </div>
  )
}

export default NodeSearch;
