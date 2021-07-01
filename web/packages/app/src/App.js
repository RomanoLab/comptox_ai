import React from 'react';
import Container from '@material-ui/core/Container';

import NodeSearch from './components/NodeSearch';
import RelationshipSearch from './components/RelationshipSearch';
import PathSearch from './components/PathSearch';

import './App.css';

import * as config from './data.json';
import { createMuiTheme, ThemeProvider } from '@material-ui/core';

const theme = createMuiTheme({
  spacing: 2
});

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
      <div className="App" style={{marginTop:'24px'}}>
        <ThemeProvider theme={theme}>
          <Container>
            <h1>ComptoxAI interactive data portal</h1>
            <p>
              From this page, you can search for individual entities (nodes) in ComptoxAI's graph database. When you select a query result, adjacent nodes (related data elements) are loaded and displayed below.
            </p>
            <p>
              For detailed usage instructions, please see <a href="https://comptox.ai/browse.html">this page</a>.
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
        </ThemeProvider>
      </div>
    );
  }
}

export default App;
