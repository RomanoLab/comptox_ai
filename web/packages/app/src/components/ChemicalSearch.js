import React from 'react';

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



class ChemicalSearch extends React.Component {
    // constructor(props) {
    //     super(props);
    //     this.state = {
    //         molString: ""
    //     }
    // }

    handleStructureQuery(event) {
        console.log("Clicked!");
        // The following retrieves the mol file from the #current-mol component
        console.log(document.getElementById("current-mol").innerHTML)
    }
    
    componentDidMount() {
        // ChemicalizeMarvinJs.createEditor("#marvin-test");
        ChemicalizeMarvinJs.createEditor("#marvin-editor").then(function (marvin) {
            function handleMolChange() {
                marvin.exportStructure("mol").then(function (mol) {
                    document.getElementById("current-mol").innerHTML = mol;
                    // this.setState({molString: mol});
                    console.log(mol);
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
                    onClick={this.handleStructureQuery}
                >
                    Search for structure
                </Button>
                </div>
            </div>
        );
    }
}

export default ChemicalSearch;
