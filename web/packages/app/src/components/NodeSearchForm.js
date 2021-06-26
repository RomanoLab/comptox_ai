import React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import InputLabel from '@material-ui/core/InputLabel';

//import { Field, reduxForm } from 'redux-form';
import { Form, Field } from 'react-final-form';

const renderSelectField = ({
  input,
  label,
  meta: { touched, error },
  children,
  ...custom
}) => (
  <Select
    label={label}
    {...input}
    onChange={(event, index, value) => input.onChange(value)}
    style={{ width: 500, paddingBottom: 8 }}
    children={children}
    variant="outlined"
    size="small"
    {...custom}
  />
);

const renderTextField = ({
  input,
  label,
  meta: { touched, error },
  ...custom
}) => (
  <TextField
    label={label}
    variant="outlined"
    size="small"
    style={{ width: 500, paddingBottom: 8 }}
    {...input}
    {...custom}
  />
)

let NodeSearchForm = props => {
  return (
    <Form
      initialValues={{
        nodeClassSelector: "Chemical",
        nodeFieldInput: "",
        nodeFieldValue: ""
      }}
    >
      {({ handleSubmit, pristine, reset, submitting }) => (
        <form onSubmit={handleSubmit}>
          <FormControl variant="outlined" size="small">
            <InputLabel>Node Type</InputLabel>
            <Field name="nodeClassSelector" component={renderSelectField}>
              <MenuItem value="Chemical">Chemical</MenuItem>
              <MenuItem value="Gene">Gene</MenuItem>
              <MenuItem value="Disease">Disease</MenuItem>
            </Field>
          </FormControl>
          <Field name="nodeFieldInput" component={renderTextField} label="Search field"/>
          <Field name="nodeFieldValue" component={renderTextField} label="Value"/>
          <br/>
          <Button variant="contained" color="primary" type="submit">Search</Button>
        </form>
      )}
    </Form>
  )
}

// export default reduxForm({
//   form: 'NodeSearchForm'
// })(NodeSearchForm)
export default NodeSearchForm
