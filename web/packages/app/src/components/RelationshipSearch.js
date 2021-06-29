import { 
  makeStyles,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@material-ui/core';
import React from 'react';
import { Map } from 'react-lodash';

import { useFetchRelationshipsByNodeIdQuery } from '../features/comptoxApiSlice';
import { useAppSelector } from '../redux/hooks';

const columns = [
  { id: 'start', label: 'Start Node' },
  { id: 'relType', label: 'Relationship Type' },
  { id: 'end', label: 'End Node'}
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
                  style={{ minWidth: column.minWidth }}
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
                      <TableCell>
                        {value}
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

  const skip = (selectedRel) ? false : true;
  
  console.log(skip);
  console.log(selectedRel);
  
  const { data = [] } = useFetchRelationshipsByNodeIdQuery(selectedRel, {
    skip,
  });


  
  return(
    <div id="rel-search">
      <h2>Relationships</h2>
      <p>
        <i>Search for a node in the box above and click "See relationships" to show all linked nodes.</i>
      </p>
      <RelationshipTable data={data}/>
    </div>
  );
}


export default RelationshipSearch;
