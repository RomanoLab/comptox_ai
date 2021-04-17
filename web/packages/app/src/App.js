import React from 'react';

import NodeSearch from './NodeSearch';
import RelationshipSearch from './RelationshipSearch';
import PathSearch from './PathSearch';
import BatchQuery from './BatchQuery';

import './App.css';

function App() {
  return (
    <div className="App">
      <body>
        <h1>ComptoxAI interactive data portal</h1>
        <NodeSearch />
        <RelationshipSearch />
        <PathSearch />
        <BatchQuery />
      </body>
    </div>
  );
}

export default App;
