import React from 'react';

import ChemicalizeMarvinJs from '../marvin/client';


class ChemicalSearch extends React.Component {
    componentDidMount() {
        ChemicalizeMarvinJs.createEditor("#marvin-test");
    }
    
    render() {
        return (
            <div className="chemical-search">
                <h2>Chemical Search</h2>
                <p><i>Find chemicals by drawing a molecular structure.</i></p>
                <div id="marvin-test" style={{width: '100%', height: '480px'}}></div>
            </div>
        );
    }
}

export default ChemicalSearch;
