import React from 'react';
import { adaptV4Theme,createTheme, StyledEngineProvider, ThemeProvider } from '@mui/material';
import Container from '@mui/material/Container';

import DatasetBuilder from './components/DatasetBuilder';
import QueryBuilder from './components/QueryBuilder';
import * as chemLists from './data/chemical_list_data.json';
import * as config from './data/data.json';

import './App.css';

const theme = createTheme(adaptV4Theme({
  spacing: 2
}));

class App extends React.Component {
  render() {
    return (
      <div className="App" style={{marginTop:'24px'}}>
        <StyledEngineProvider injectFirst>
          <ThemeProvider theme={theme}>
            <Container>
              <h1>ComptoxAI interactive data portal</h1>
              <p>
                Search for entities and explore relationships in ComptoxAI&apos;s knowledge graph.
                Build multi-hop patterns to discover connections between chemicals, genes, pathways, AOPs, and more.
              </p>
              <p>
                For detailed usage instructions, please see <a href="https://comptox.ai/browse.html">this page</a>.
                For direct access to the graph database, open <a href="https://lab.comptox.ai" target="_blank" rel="noopener noreferrer">Memgraph Lab</a>.
              </p>
              <QueryBuilder config={config.default} />
              <DatasetBuilder
                config={config.default}
                chemLists={chemLists.default}
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
