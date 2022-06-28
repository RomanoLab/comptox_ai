import React, { useReducer, Fragment } from 'react';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Box,
    Button,
    Collapse,
    IconButton,
    Paper,
    Skeleton,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown'
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp'

import ChemicalizeMarvinJs from './marvin/client';
import {
    useRunStructureSearchQuery,
    useFetchChemicalByDtsxidQuery
} from '../features/comptoxApiSlice';
import { readSearchResults } from '../features/nodeSlice';
import { useAppDispatch } from '../redux/hooks';


const TEST_DATA = [
    {
        "DSSTox_Compound_id": "DTXCID904115",
        "DSSTox_Substance_id": "DTXSID2024115",
        "CASRN": "64-18-6",
        "QC_Level": "DSSTox_Low",
        "Preferred_name": "Formic acid",
        "Mol_Weight": "46.0250000000",
        "Mol_Formula": "CH2O2",
        "Monoisotopic_Mass": "46.0054793040",
        "Dashboard_URL": "https://comptox.epa.gov/dashboard/DTXSID2024115",
        "dissimilarity": "0.0",
        "SIMILARITY": "1.000"
    },
    {
        "DSSTox_Compound_id": "DTXCID10161515",
        "DSSTox_Substance_id": "DTXSID90239024",
        "CASRN": "925-94-0",
        "QC_Level": "Public_Medium",
        "Preferred_name": "Formic (2H)acid",
        "Mol_Weight": "47.0310000000",
        "Mol_Formula": "CHDO2",
        "Monoisotopic_Mass": "47.0117560500",
        "Dashboard_URL": "https://comptox.epa.gov/dashboard/DTXSID90239024",
        "dissimilarity": "0.0",
        "SIMILARITY": "1.000"
    },
    {
        "DSSTox_Compound_id": "DTXCID7023801",
        "DSSTox_Substance_id": "DTXSID9043801",
        "CASRN": "463-79-6",
        "QC_Level": "DSSTox_High",
        "Preferred_name": "Carbonic acid",
        "Mol_Weight": "62.0240000000",
        "Mol_Formula": "CH2O3",
        "Monoisotopic_Mass": "62.0003939240",
        "Dashboard_URL": "https://comptox.epa.gov/dashboard/DTXSID9043801",
        "dissimilarity": "0.16666669",
        "SIMILARITY": "0.833"
    }
]


class StructureEditor extends React.Component {
    componentDidMount() {
        // ChemicalizeMarvinJs.createEditor("#marvin-test");
        ChemicalizeMarvinJs.createEditor("#marvin-editor").then(function (marvin) {
            function handleMolChange() {
                marvin.exportStructure("mol").then(function (mol) {
                    document.getElementById("current-mol").innerHTML = mol;
                })
            }

            marvin.importStructure("name", "arachidonic acid");

            marvin.on("molchange", handleMolChange);
        });
    }

    render() {
        return (
            <div id="marvin-editor" style={{width: '100%', height: '480px'}}></div>
        );
    }
}

/*
    {
      "DSSTox_Compound_id": "DTXCID7023801",
      "DSSTox_Substance_id": "DTXSID9043801",
      "CASRN": "463-79-6",
      "QC_Level": "DSSTox_High",
      "Preferred_name": "Carbonic acid",
      "Mol_Weight": "62.0240000000",
      "Mol_Formula": "CH2O3",
      "Monoisotopic_Mass": "62.0003939240",
      "Dashboard_URL": "https://comptox.epa.gov/dashboard/DTXSID9043801",
      "dissimilarity": "0.16666669",
      "SIMILARITY": "0.833"
    }
 */
const StructureResult = (props) => {
    const data = props.data;
    
    return (
        <Box className="structure-result">
            <ul>
                <li>{data.Preferred_name}</li>
                <li>{data.Mol_Formula}</li>
                <li>{data.SIMILARITY}</li>
            </ul>
        </Box>
    );
}



const StructureResultsRow = (props) => {
    const { row } = props;
    const [open, setOpen]  = React.useState(false);
    const [buttonHasBeenClicked, setButtonHasBeenClicked] = React.useState(false);
    const dispatch = useAppDispatch();

    const { data = [], error, isLoading, isUninitialized } = useFetchChemicalByDtsxidQuery(row.DSSTox_Substance_id, {
        skip: !buttonHasBeenClicked
    });

    // "Correct" usage of RTK query would have the node search results request
    // the cached data using the same hook we use in this component, but that
    // feels messy and weird to me. Instead, we are doing it the 'wrong' way, by
    // copying the data retrieved from the API into the nodeSlice portion of
    // the redux store. Then, the node search component will render the results.
    if (data.length > 0) {
        // put the data into the store
        dispatch(readSearchResults(data));
    }

    const handleNodeSearch = event => {
        event.preventDefault();
        setButtonHasBeenClicked(true);
    }
    
    return (
        <Fragment>
            <TableRow>
                <TableCell>
                    <IconButton
                        aria-label="expand row"
                        size="small"
                        onClick={() => setOpen(!open)}
                    >
                        {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell component="th" scope="row">{row.Preferred_name}</TableCell>
                <TableCell align="left">{row.DSSTox_Substance_id}</TableCell>
                <TableCell align="left">{row.Mol_Formula}</TableCell>
                <TableCell align="right">{row.SIMILARITY}</TableCell>
                <TableCell align="right">{row.Mol_Weight}</TableCell>
            </TableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1 }}>
                            <Button
                                variant="outlined"
                                onClick={handleNodeSearch}
                            >
                                Send to Node Search
                            </Button>
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </Fragment>
    );
}

const StructureResultsTable = (props) => {
    const rows = props.data;

    return (
        <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
            <Table stickyHeader size="small" aria-label="structure result table">
                <TableHead>
                    <TableRow>
                        <TableCell />
                        <TableCell>Chemical name</TableCell>
                        <TableCell align="left">DSSTox ID</TableCell>
                        <TableCell align="left">Molecular formula</TableCell>
                        <TableCell align="right">Similarity score</TableCell>
                        <TableCell align="right">MW</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {rows.map((row) => (
                        <StructureResultsRow key={row.Preferred_name} row={row} />
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

const setCurrentMolReducer = (state, event) => {
    return event;
}

const StructureSearchControls = (props) => {
    const [currentMolData, setCurrentMolData] = useReducer(setCurrentMolReducer, "");

    const skip = (currentMolData === "") ? true : false;

    const { data, error, isLoading, isUninitialized } = useRunStructureSearchQuery(currentMolData, {
        skip
    });

    const handleStructureQuery = (event) => {
        const current_mol = document.getElementById("current-mol").innerHTML
        setCurrentMolData(current_mol);
    }
    
    return (
        <div className="chemical-search">
            <div id="marvin-bottom-controls">
            
                <Accordion id="structure-info">
                    <AccordionSummary
                        expandIcon={<ExpandMoreIcon />}
                        aria-controls="panel1a-content"
                        id="panel1a-header"
                    >
                        <Typography>Show structure information</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        MOL structure document:
                        <TextField
                            id="current-mol"
                            multiline
                            rows={10}
                            fullWidth
                            variant="outlined"
                            size="small"
                            disabled={true}
                            // value={this.state.molString}
                        />
                    </AccordionDetails>
                </Accordion>
                <Button
                    variant="contained"
                    color="primary"
                    size="small"
                    id="structure-search-button"
                    onClick={handleStructureQuery}
                >
                    Search for structure
                </Button>
            </div>
            <Box
                className="structure-search-results"
                style={{
                    margin: 12
                }}
            >
                {error ? (
                    <>Error!</>
                ) : isUninitialized ? (
                    <>
                        Draw a structure and click "Search for Structure"
                        <Box
                            style={{
                                marginTop: 8,
                                // minHeight: 300,
                                // maxHeight: 300,
                                // overflow: 'auto'
                            }}
                        >
                            <Box
                                style={{
                                    marginBottom: '5px'
                                }}
                            >
                                <StructureResultsTable
                                    data={TEST_DATA}
                                    // data={[].concat(...new Array(30).fill(TEST_DATA))}
                                />
                            </Box>
                        </Box>                        
                    </>
                ) : isLoading ? (
                    <>
                        Loading...
                        <Box
                            style={{
                                marginTop: 8,
                                maxHeight: 300,
                                overflow: 'auto'
                            }}
                        >
                            {Array.from(new Array(6)).map((i, idx) => (
                                <Box
                                    style={{
                                        marginBottom: '5px'
                                    }}
                                >
                                    <Skeleton 
                                        variant="rectangular"
                                        height={60}
                                        style={{

                                        }}
                                    />
                                </Box>
                            ))}
                        </Box>
                    </>
                ) : data ? (
                    <>{data.map((structure) => <StructureResult data={structure}/>)}</>
                ) : null}
            </Box>
        </div>
    );

}

const ChemicalSearch = (props) => {
    return (
        <div className="chemical-search">
            <h2>Chemical Search</h2>
            <p><i>Find chemicals by drawing a molecular structure.</i></p>
            <StructureEditor/>
            <StructureSearchControls/>
        </div>
    );
}


export default ChemicalSearch;
