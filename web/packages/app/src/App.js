import React from 'react';
import Container from '@material-ui/core/Container';

import NodeSearch from './components/NodeSearch';
import RelationshipSearch from './components/RelationshipSearch';
import PathSearch from './components/PathSearch';

import './App.css';

import * as config from './data.json';

class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      relationshipResults: [],
      pathResults: []
    }
  }

  render() {
    return (
      <div className="App">
        <Container>
          <h1>ComptoxAI interactive data portal</h1>
          <p>
            From this page, you can search for individual entities (nodes) in ComptoxAI's graph database. When you select a query result, adjacent nodes (related data elements) are loaded and displayed below.
          </p>
          <p>
            For detailed usage instructions, please see <b>here</b>.
          </p>
          {/* <HowToUse /> */}
          <NodeSearch config={config.default}/>
          <RelationshipSearch
            relationshipResults={this.state.relationshipResults}
          />
          <PathSearch
            pathResults={this.state.pathResults}
          />
          {/* <BatchQuery /> */}
        </Container>
      </div>
    );
  }
}

export default App;
