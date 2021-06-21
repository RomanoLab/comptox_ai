import React from 'react';
import Container from '@material-ui/core/Container';

// import HowToUse from './HowToUse';
import NodeSearch from './components/nodeSearch/NodeSearch';
import RelationshipSearch from './components/RelationshipSearch';
import PathSearch from './components/PathSearch';
import BatchQuery from './BatchQuery';

import './App.css';

const testNode = {
  nodeType: 'Chemical',
  commonName: "3-Fluoro-4-(1-methyl-5,6-dihydro-1,2,4-triazin-4(1H)-yl)aniline",
  ontologyIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9085',
  // identifiers: {
  //   PubchemSID: "316386667",
  //   DTXSID: "DTXSID90857126",
  //   PubchemCID: "71741499",
  //   CasRN: "1334167-69-9"
  // },
  identifiers: {
    PubchemSID: "PubChem SID: 316386667",
    DTXSID: "DSSTOX ID: DTXSID90857126",
    PubchemCID: "PubChem CID: 71741499",
    CasRN: "CasRN: 1334167-69-9"
  }
};

const testRelationship = {
  startNode: {
    nodeType: 'Chemical',
    commonName: "3-Fluoro-4-(1-methyl-5,6-dihydro-1,2,4-triazin-4(1H)-yl)aniline",
    ontologyIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9085',
    identifiers: {
      PubchemSID: "316386667",
      DTXSID: "DTXSID90857126",
      PubchemCID: "71741499",
      CasRN: "1334167-69-9"
    }
  },
  
  endNodes: [
    {
      relationshipType: "NODE_RELATES_SELF",
      node: {
        nodeType: 'Chemical',
        commonName: "3-Fluoro-4-(1-methyl-5,6-dihydro-1,2,4-triazin-4(1H)-yl)aniline",
        ontologyIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9085',
        identifiers: {
          PubchemSID: "316386667",
          DTXSID: "DTXSID90857126",
          PubchemCID: "71741499",
          CasRN: "1334167-69-9"
        }
      }
    }
  ]
};

const testPath = {
  startNode: {
    nodeType: 'Chemical',
    commonName: "3-Fluoro-4-(1-methyl-5,6-dihydro-1,2,4-triazin-4(1H)-yl)aniline",
    ontologyIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9085',
    identifiers: {
      PubchemSID: "316386667",
      DTXSID: "DTXSID90857126",
      PubchemCID: "71741499",
      CasRN: "1334167-69-9"
    }
  },
  midNodes: [],
  endNode: {
    nodeType: 'Chemical',
    commonName: "3-Fluoro-4-(1-methyl-5,6-dihydro-1,2,4-triazin-4(1H)-yl)aniline",
    ontologyIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9086',
    identifiers: {
      PubchemSID: "316386667",
      DTXSID: "DTXSID90857126",
      PubchemCID: "71741499",
      CasRN: "1334167-69-9"
    }
  },
  relationships: [
    {
      fromIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9085',
      toIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9086',
      relType: 'GENE_RELATES_GENE'
    }
  ]
};

class App extends React.Component {
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
              nodeResults={[testNode]}
            />
            <RelationshipSearch
              relationshipResults={testRelationship}
            />
            <PathSearch
              pathResults={testPath}
            />
            <BatchQuery />
          </Container>
        </body>
      </div>
    );
  }
}

export default App;
