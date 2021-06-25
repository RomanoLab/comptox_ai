import React from 'react';
import Container from '@material-ui/core/Container';

import NodeSearch from './components/NodeSearch';
import RelationshipSearch from './components/RelationshipSearch';
import PathSearch from './components/PathSearch';
import BatchQuery from './BatchQuery';

import './App.css';

// const testPath = {
//   startNode: {
//     nodeType: 'Chemical',
//     commonName: "3-Fluoro-4-(1-methyl-5,6-dihydro-1,2,4-triazin-4(1H)-yl)aniline",
//     ontologyIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9085',
//     identifiers: {
//       PubchemSID: "316386667",
//       DTXSID: "DTXSID90857126",
//       PubchemCID: "71741499",
//       CasRN: "1334167-69-9"
//     }
//   },
//   midNodes: [],
//   endNode: {
//     nodeType: 'Chemical',
//     commonName: "3-Fluoro-4-(1-methyl-5,6-dihydro-1,2,4-triazin-4(1H)-yl)aniline",
//     ontologyIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9086',
//     identifiers: {
//       PubchemSID: "316386667",
//       DTXSID: "DTXSID90857126",
//       PubchemCID: "71741499",
//       CasRN: "1334167-69-9"
//     }
//   },
//   relationships: [
//     {
//       fromIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9085',
//       toIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9086',
//       relType: 'GENE_RELATES_GENE'
//     }
//   ]
// };

class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      nodeSearchParams: {
        nodeTypes: [],
        searchField: "",
        value: ""
      },
      nodeResults: [],
      relationshipResults: [],
      pathResults: []
    }
  }
  
  render() {
    return (
      <div className="App">
        <body>
          <Container>
            <h1>ComptoxAI interactive data portal</h1>
            <p>
              From this page, you can search for individual entities (nodes) in ComptoxAI's graph database. When you select a query result, adjacent nodes (related data elements) are loaded and displayed below.
            </p>
            <p>
              For detailed usage instructions, please see <b>here</b>.
            </p>
            {/* <HowToUse /> */}
            <NodeSearch
              nodeResults={this.state.nodeResults}
            />
            <RelationshipSearch
              relationshipResults={this.state.relationshipResults}
            />
            <PathSearch
              pathResults={this.state.pathResults}
            />
            <BatchQuery />
          </Container>
        </body>
      </div>
    );
  }
}

export default App;
