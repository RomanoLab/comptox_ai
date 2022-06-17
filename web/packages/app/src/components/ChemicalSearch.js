import React from 'react';

import { Button, TextField } from '@mui/material';

import ChemicalizeMarvinJs from './marvin/client';


class ChemicalSearch extends React.Component {
    
    
    componentDidMount() {
        // ChemicalizeMarvinJs.createEditor("#marvin-test");
        ChemicalizeMarvinJs.createEditor("#marvin-editor").then(function (marvin) {
            function handleMolChange() {
                console.log(marvin);
                marvin.exportStructure("smiles").then(function (smiles) {
                    document.getElementById("current-smiles").innerHTML = "SMILES: " + smiles;
                })
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
            <div className="chemical-search">
                <h2>Chemical Search</h2>
                <p><i>Find chemicals by drawing a molecular structure.</i></p>
                <div id="marvin-editor" style={{width: '100%', height: '480px'}}></div>
                {/* Display the SMILES string: */}
                <div id="marvin-bottom-controls">
                {/* <div id="current-smiles"></div> */}
                <TextField
                    id="current-smiles"
                    fullWidth
                    variant="outlined"
                    size="small"
                />
                <TextField
                    id="current-mol"
                    multiline
                    rows={10}
                    fullWidth
                    variant="outlined"
                    size="small"
                />
                <Button
                    variant="contained"
                    color="primary"
                    size="small"
                >
                    Search for structure
                </Button>
                </div>
            </div>
        );
    }
}

export default ChemicalSearch;
