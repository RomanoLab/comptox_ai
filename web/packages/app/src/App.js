import React from 'react';
import Container from '@material-ui/core/Container';

import HowToUse from './HowToUse';
import NodeSearch from './NodeSearch';
import RelationshipSearch from './RelationshipSearch';
import PathSearch from './PathSearch';
import BatchQuery from './BatchQuery';

import './App.css';

function App() {
  return (
    <div className="App">
      <body>
        <Container>
          <h1>ComptoxAI interactive data portal</h1>
          <HowToUse />
          <NodeSearch />
          <RelationshipSearch />
          <PathSearch />
          <BatchQuery />
        </Container>
      </body>
    </div>
  );
}

export default App;
