const express = require('express');

const nconf = require('./config');
const routes = require('./routes');
const neo4jSessionCleanup = require('./middleware/neo4jSessionCleanup');
const { writeError } = require('./helpers/response');

const dataConfigJson = require('./assets/data.json');

const app = express();
const swaggerJSDoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');
const bodyParser = require('body-parser');
const methodOverride = require('method-override');
const path = require('path');
const cors = require('cors');

const port = 3000;

const HOST = (process.env.NODE_ENV === 'production') ? 'https://comptox.ai/api' : 'http://localhost:3000';

const swaggerOpts = {
  definition: {
    openapi: '3.0.3',
    info: {
      title: 'ComptoxAI REST API',
      version: '1.0.0',
      description: 'A REST Web API providing programmatic access to ComptoxAI\'s graph database.',
    },
    servers: [
      {
        url: 'https://comptox.ai/api',
        description: 'ComptoxAI\'s public REST API',
      },
      {
        url: 'http://localhost:3000',
        description: 'Default local (dev) API server',
      },
    ],
    host: HOST,
  },
  apis: ['./routes/*.js', './*.js'],
};

// Make swagger/openapi documentation
const swaggerSpec = swaggerJSDoc(swaggerOpts);
app.use('/help', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
app.set('port', nconf.get('PORT'));

app.use(require('./neo4j'));

app.use(bodyParser.json());
app.use(methodOverride());

app.use(cors());

// CORS: Important for Open API and other things
app.use((req, res, next) => {
  // res.header("Access-Control-Allow-Origin", "*");
  // res.header("Access-Control-Allow-Credentials", "true");
  // // res.header("Access-Control-Allow-Credentials", "false");
  // res.header(
  //     "Access-Control-Allow-Methods",
  //     "GET,HEAD,OPTIONS,POST,PUT,DELETE"
  // );
  // res.header(
  //     "Access-Control-Allow-Headers",
  //     "Origin, X-Requested-With, Content-Type, Accept, Authorization, X-Auth-Token"
  // );
  // Make everything be returned as JSON
  res.header('Content-Type', 'application/json');
  next();
});

app.options('*', cors());

app.use(neo4jSessionCleanup);

/**
 * @openapi
 * /:
 *   get:
 *     description: Return a string
 *     summary: Display a welcome message
 *     responses:
 *       200:
 *         description: Returns a welcome message if the API is available
 *         content:
 *           application/json:
 *             schema:
 *               type: string
 */
app.get('/', (req, res) => {
  res.send('Welcome to ComptoxAI\'s web API! Please read the documentation at http://comptox.ai/api/help/ for available operations.');
});

/**
 * @openapi
 * /config:
 *   get:
 *     description: Return basic database configuration metadata
 *     summary: Fetch metadata describing the API's internal configuration
 *     responses:
 *       200:
 *         description: Returns config metadata
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 */
app.get('/config', (req, res) => {
  console.log(dataConfigJson);
  res.json(dataConfigJson);
});

// Note: We use bodyParser here to enable text data in the request body
app.post('/chemicals/structureSearch', bodyParser.text({ type: '*/*' }), routes.chemicals.structureSearch);

app.get('/nodes/listNodeTypes', routes.nodes.listNodeTypes);
app.get('/nodes/listNodeTypeProperties/:type', routes.nodes.listNodeTypeProperties);
// example: http://localhost:3000/nodes/Chemical/search?field=xrefDTXSID&value=DTXSID30857908
app.get('/nodes/:type/search?', routes.nodes.findNode);
app.get('/nodes/:type/searchContains?', routes.nodes.findNodeContains);
app.get('/nodes/fetchById/:id', routes.nodes.fetchById);
app.get('/nodes/fetchChemicalByDtsxid/:id', routes.nodes.fetchChemicalByDtsxid);

app.get('/relationships/fromStartNodeId/:id', routes.relationships.findRelationshipsByNode);

app.get('/paths/findByIds?', routes.paths.findByIds);

app.get('/datasets/makeQsarDataset?', routes.datasets.makeQsarDataset);

app.get('/graphs/test', routes.graphs.testGraphs);

// handle errors
app.use((err, req, res, next) => {
  if (err && err.status) {
    writeError(res, err);
  } else next(err);
});

app.listen(app.get('port'), () => {
  console.log(`ComptoxAI API listening at http://localhost:${port}`);
});
