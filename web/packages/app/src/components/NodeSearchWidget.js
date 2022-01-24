import React from 'react';
import {
    FormControl,
    Grid,
    InputLabel,
    MenuItem,
    Select,
    TextField
} from '@material-ui/core';

const NodeSearchWidget = (props) => {
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
    </Grid>
}

export default NodeSearchWidget;
