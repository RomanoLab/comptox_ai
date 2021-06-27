import React, { useReducer, useState } from 'react';
import { Map } from 'react-lodash';

import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import InputLabel from '@material-ui/core/InputLabel';

import NodeResult from './NodeResult';
import { useSearchNodesQuery } from '../features/comptoxApi/comptoxApiSlice';

const formReducer = (state, event) => {
  return {
    ...state,
    [event.name]: event.value
  }
}

const formResetReducer = () => {
  return {
    nodeType: null,
    nodeField: null,
    nodeValue: null
  }
}

const submitReducer = (state, event) => {
  return {
    label: event.label,
    field: event.field,
    value: event.value
  }
}

// See: https://www.digitalocean.com/community/tutorials/how-to-build-forms-in-react
const NodeSearch = (props) => {
  const { config } = props;
  
  const [formData, setFormData] = useReducer(formReducer, {});
  const [submitData, setSubmitData] = useReducer(submitReducer, {});
  // eslint-disable-next-line
  const [resetData, setResetData] = useReducer(formResetReducer, {});
  const [skip, setSkip] = useState(true); // Don't render search results until we've hit "search" at least once
  
  const { data = [] } = useSearchNodesQuery([submitData.label, submitData.field, submitData.value], {
    skip,
  });

  const handleSubmit = event => {
    event.preventDefault();
    setSkip(false);
    setSubmitData({
      label: formData.nodeType,
      field: formData.nodeField,
      value: formData.nodeValue
    })
  }

  const handleChange = event => {
    setFormData({
      name: event.target.name,
      value: event.target.value,
    });
  }

  const handleReset = () => {
    setResetData({});

    console.log("handleReset:")
    console.log(formData);
  }

  const fetchNodeFields = selectedNodeLabel => {
    if (selectedNodeLabel === undefined) {
      return []
    } else {
      return config.nodeConfig.nodeLabelProperties[selectedNodeLabel]
    }
  } 

  console.log(data);
  
  return(
    <div className="node-search">
      <h2>Nodes</h2>
      <h3>Search</h3>
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
              value={formData.nodeField || ''}
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
          <Button variant="contained" color="primary" type="submit">Search</Button>
          <Button variant="contained" color="primary" onClick={handleReset}>Reset</Button>
        </form>
      </div>

      <h3>Search Results</h3>
      {!(data.length === 0) &&
        <Map
          collection={data}
          iteratee={r => (
            <NodeResult
              nodeType={r.nodeType}
              nodeName={r.commonName}
              nodeIDs={r.identifiers}
              nodeIRI={r.ontologyIRI}
              nodeNeo4jID={r.nodeId}
            />
          )}
        />
      }
    </div>
  )
}

export default NodeSearch;
