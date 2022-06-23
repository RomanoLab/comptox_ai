import React, { useReducer, useState } from 'react';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Button,
    TextField,
    Typography
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import ChemicalizeMarvinJs from './marvin/client';
import { useRunStructureSearchQuery } from '../features/comptoxApiSlice';


class StructureEditor extends React.Component {
    componentDidMount() {
        // ChemicalizeMarvinJs.createEditor("#marvin-test");
        ChemicalizeMarvinJs.createEditor("#marvin-editor").then(function (marvin) {
            function handleMolChange() {
                marvin.exportStructure("mol").then(function (mol) {
                    document.getElementById("current-mol").innerHTML = mol;
                    // this.setState({molString: mol});
                    // console.log(mol);
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


const StructureResultSummary = (props) => {
    return (
        <div className="structure-result">
            <ul>
                <li>{props.data.Preferred_name}</li>
                <li>{props.data.Mol_Formula}</li>
                <li>{props.data.SIMILARITY}</li>
            </ul>
        </div>
    );
}

const setCurrentMolReducer = (state, event) => {
    console.log("in setCurrentMolReducer:");
    console.log(event);

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
        console.log(current_mol)
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
            <div className="structure-search-results">
                {error ? (
                    <>Error!</>
                ) : isUninitialized ? (
                    <>Uninitialized</>
                ) : isLoading ? (
                    <>Loading...</>
                ) : data ? (
                    <>{data.map((structure) => <StructureResultSummary data={structure}/>)}</>
                ) : null}
            </div>
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
