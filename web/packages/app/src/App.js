import React from 'react';
import './App.css';

class SearchNode extends React.Component {
  render() {
    return(
      <div>
        <h2>Search for a node</h2>
        <p>
          <i>A node is an individual entity in ComptoxAI's graph database. For example, individual genes, diseases, and chemicals are all represented as nodes in the graph database.</i>
        </p>
      </div>
    );
  }
}

class SearchRelationship extends React.Component {
  render() {
    return(
      <div>
        <h2>Search for a relationship</h2>
        <p>
          <i>Relationships are associations or other conceptual links between any two entities in the graph database. For example, a relationship may represent a chemical interacting with a gene, or a symptom manifesting a disease.</i>
        </p>
      </div>
    );
  }
}

class SearchPath extends React.Component {
  render() {
    return(
      <div>
        <h2>Search for a path</h2>
        <p>
          <i>Paths are chains of two or more nodes in the graph database along with the relationships that link them.</i>
        </p>
      </div>
    );
  }
}

class FetchBatch extends React.Component {
  render() {
    return(
      <div>
        <h2>Bulk data fetch</h2>
        <p>
          This tool is used to retrieve node and/or relationship properties for many nodes or relationships simultaneously.
        </p>
      </div>
    );
  }
}

function App() {
  return (
    <div className="App">
      <body>
        <h1>ComptoxAI interactive data portal</h1>
        <SearchNode />
        <SearchRelationship />
        <SearchPath />
        <FetchBatch />
      </body>
    </div>
  );
}

export default App;
