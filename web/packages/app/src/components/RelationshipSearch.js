import {
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import makeStyles from '@mui/styles/makeStyles';
import React from 'react';

import { setRelStartNode } from '../features/relationshipSlice';
import { useFetchRelationshipsByNodeIdQuery } from '../features/comptoxApiSlice';
import { useAppDispatch, useAppSelector } from '../redux/hooks';

const columns = [
  { id: 'start', label: 'Start Node', align: 'center' },
  { id: 'relType', label: 'Relationship Type', align: 'center'},
  { id: 'end', label: 'End Node', align: 'center' }
];

const useStyles = makeStyles({
  container: {
    maxHeight: 440,
  },  
});

const RelationshipTable = (props) => {
  const { data } = props;
  const classes = useStyles();

  const rows = data.map((d) => ({
    start: d.fromNode.commonName,
    relType: `\u27E8${d.relType}\u27E9`,
    end: (d.toNode.commonName) ? d.toNode.commonName : d.toNode.nodeId  // TODO: FIX THIS! EVERYTHING SHOULD HAVE A COMMON NAME!
  }));

  console.log(data);

  return (
    <Paper>
      <TableContainer className={classes.container}>
        <Table stickyHeader aria-label="sticky table">
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align}
                  style={{ minWidth:column.minWidth, fontWeight:'bold' }}
                >
                  {column.label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => {
              return (
                <TableRow>
                  {columns.map((column) => {
                    const value = row[column.id];
                    return (
                      <TableCell align='center'>
                        {
                          (column.id === 'start') ? (
                            <Button style={{justifyContent: "flex-start"}}>{value}</Button>
                          ) : (column.id === 'end') ? (
                            <Button>{value}</Button>
                          ) : value
                        }
                        {/* {value} */}
                      </TableCell>
                    )
                  })}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}

const RelationshipSearch = (props) => {
  const selectedRel = useAppSelector((state) => state.relationship.relStartNode)
  const dispatch = useAppDispatch();

  const skip = (selectedRel) ? false : true;
  
  const { data = [], error, isLoading, isUninitialized } = useFetchRelationshipsByNodeIdQuery(selectedRel, {
    skip,
  });


  const handleResetRelSearch = () => {
    dispatch(setRelStartNode(null));
  }
  
  return(
    <div id="rel-search">
      <h2>Relationships</h2>
      {error ? (
        <></>
      ) : isUninitialized ? (
        <p><i>Search for a node in the box above and click "Load relationships" to show all linked nodes.</i></p>
      ) : isLoading ? (
        <>Loading relationships...</>
      ) : data ? (
        <div>
          <Button 
            onClick={handleResetRelSearch}
            variant="outlined"
            style={{marginBottom:'6px'}}
          >
            Clear reationship results
          </Button>
          <RelationshipTable data={data}/>
        </div>
      ) : null}
      
      {/* <RelationshipTable data={data}/> */}
    </div>
  );
}


export default RelationshipSearch;
