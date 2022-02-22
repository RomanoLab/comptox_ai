import React from 'react';
import Container from '@mui/material/Container';

import NodeSearch from './components/NodeSearch';
import RelationshipSearch from './components/RelationshipSearch';
import PathSearch from './components/PathSearch';
import DatasetBuilder from './components/DatasetBuilder';
import ShortestPath from './components/ShortestPath';
import ExpandNetwork from './components/ExpandNetwork';

import './App.css';

import * as config from './data/data.json';
import * as chemLists from './data/chemical_list_data.json'
import { createTheme, ThemeProvider, StyledEngineProvider, adaptV4Theme } from '@mui/material';

const theme = createTheme(adaptV4Theme({
  spacing: 2
}));

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
        <StyledEngineProvider injectFirst>
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
              <NodeSearch 
                config={config.default}
              />
              <RelationshipSearch
                relationshipResults={this.state.relationshipResults}
              />
              <PathSearch
                pathResults={this.state.pathResults}
              />
              {/* <BatchQuery /> */}
              <DatasetBuilder
                config={config.default}
                chemLists={chemLists.default}
              />
              <ShortestPath
              />
              <ExpandNetwork
              />
              <div style={{marginTop:'300px'}}>
              </div>
            </Container>
          </ThemeProvider>
        </StyledEngineProvider>
      </div>
    );
  }
}

export default App;
