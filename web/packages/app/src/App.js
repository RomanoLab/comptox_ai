import React from 'react';
import Container from '@material-ui/core/Container';

import HowToUse from './HowToUse';
import NodeSearch from './components/nodeSearch/NodeSearch';
import RelationshipSearch from './components/RelationshipSearch';
import PathSearch from './components/PathSearch';
import BatchQuery from './BatchQuery';

import './App.css';

const testNode = {
  nodeType: 'Chemical',
  commonName: "3-Fluoro-4-(1-methyl-5,6-dihydro-1,2,4-triazin-4(1H)-yl)aniline",
  ontologyURI: 'http://jdr.bio/ontologies/comptox.owl@chemical_dtxsid9085',
  identifiers: {
    PubchemSID: "316386667",
    DTXSID: "DTXSID90857126",
    PubchemCID: "71741499",
    CasRN: "1334167-69-9"
  }
};

const testRelationship = {
  startNode: {
    nodeType: 'Chemical',
    commonName: "3-Fluoro-4-(1-methyl-5,6-dihydro-1,2,4-triazin-4(1H)-yl)aniline",
    ontologyURI: 'http://jdr.bio/ontologies/comptox.owl@chemical_dtxsid9085',
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
        ontologyURI: 'http://jdr.bio/ontologies/comptox.owl@chemical_dtxsid9085',
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
    ontologyURI: 'http://jdr.bio/ontologies/comptox.owl@chemical_dtxsid9085',
    identifiers: {
      PubchemSID: "316386667",
      DTXSID: "DTXSID90857126",
      PubchemCID: "71741499",
      CasRN: "1334167-69-9"
    }
  },
  subsequentNodes: [
    {
      relationshipType: "NODE_RELATES_SELF",
      endNodes: [
        {
          nodeType: 'Chemical',
          commonName: "3-Fluoro-4-(1-methyl-5,6-dihydro-1,2,4-triazin-4(1H)-yl)aniline",
          ontologyURI: 'http://jdr.bio/ontologies/comptox.owl@chemical_dtxsid9085',
          identifiers: {
            PubchemSID: "316386667",
            DTXSID: "DTXSID90857126",
            PubchemCID: "71741499",
            CasRN: "1334167-69-9"
          }
        }
      ]
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
            <HowToUse />
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
