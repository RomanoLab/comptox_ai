const express = require('express');
const swaggerJSDoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');
const bodyParser = require('body-parser');
const methodOverride = require('method-override');
const cors = require('cors');

const nconf = require('./config');
const routes = require('./routes');
const dbUtils = require('./neo4j/dbUtils');
const neo4jSessionCleanup = require('./middleware/neo4jSessionCleanup');
const { writeError } = require('./helpers/response');
const dataConfigJson = require('./assets/data.json');

const app = express();
const port = nconf.get('PORT') || 3000;

const swaggerOpts = {
  definition: {
    openapi: '3.0.3',
    info: {
      title: 'ComptoxAI REST API',
      version: '1.1.0',
      description: 'A REST Web API providing programmatic access to ComptoxAI\'s graph database.',
    },
    servers: [
      {
        url: nconf.get('API_PUBLIC_URL') || 'https://api.comptox.ai',
        description: 'ComptoxAI\'s public REST API',
      },
      {
        url: `http://0.0.0.0:${port}`,
        description: 'Default local (dev) API server',
      },
    ],
  },
  apis: ['./routes/*.js', './*.js'],
};

const swaggerSpec = swaggerJSDoc(swaggerOpts);
app.use('/help', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
app.set('port', port);

app.use(bodyParser.json());
app.use(methodOverride());
app.use(cors());
app.options('*', cors());

app.use((req, res, next) => {
  res.header('Content-Type', 'application/json');
  next();
});

// Must come before routes so res.on('finish') fires after handlers complete.
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
 */
app.get('/', (req, res) => {
  res.send('Welcome to ComptoxAI\'s web API! Please read the documentation at http://comptox.ai/api/help/ for available operations.');
});

/**
 * @openapi
 * /health:
 *   get:
 *     description: Liveness/readiness probe — verifies the API process is up and the graph database responds.
 *     summary: Health check
 *     responses:
 *       200:
 *         description: API and database are reachable
 *       503:
 *         description: Database is unreachable
 */
app.get('/health', async (req, res) => {
  const session = dbUtils.driver.session({ defaultAccessMode: 'READ' });
  try {
    await session.run('RETURN 1 AS ok');
    res.status(200).json({ status: 'ok', db: 'up' });
  } catch (err) {
    res.status(503).json({ status: 'degraded', db: 'down', error: err.message });
  } finally {
    await session.close();
  }
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
 */
app.get('/config', (req, res) => {
  res.json(dataConfigJson);
});

app.post('/chemicals/structureSearch', bodyParser.text({ type: '*/*' }), routes.chemicals.structureSearch);
// More specific /chemicals/... routes must precede the :dtsxid catch-all
// patterns below so that e.g. /chemicals/fetchByCas/... isn't matched by
// /chemicals/:dtsxid/genes.
app.get('/chemicals/fetchByCas/:cas', routes.chemicals.fetchByCas);
app.get('/chemicals/:dtsxid/genes', routes.chemicals.findGenes);
app.get('/chemicals/:dtsxid/aops', routes.chemicals.findAops);

app.get('/genes/fetchBySymbol/:symbol', routes.genes.fetchBySymbol);

app.get('/nodes/listNodeTypes', routes.nodes.listNodeTypes);
app.get('/nodes/listNodeTypeProperties/:type', routes.nodes.listNodeTypeProperties);
app.get('/nodes/:type/search', routes.nodes.findNode);
app.get('/nodes/:type/searchContains', routes.nodes.findNodeContains);
app.get('/nodes/fetchById/:id', routes.nodes.fetchById);
app.get('/nodes/fetchChemicalByDtsxid/:id', routes.nodes.fetchChemicalByDtsxid);

app.get('/relationships/listRelationshipTypes', routes.relationships.listRelationshipTypes);
app.get('/relationships/fromStartNodeId/:id', routes.relationships.findRelationshipsByNode);

app.get('/paths/findByIds', routes.paths.findByIds);

app.get('/datasets/makeQsarDataset', routes.datasets.makeQsarDataset);

app.get('/graphs/test', routes.graphs.testGraphs);

app.get('/stats', routes.stats.getStats);

app.use((err, req, res, next) => {
  if (err && err.status) {
    writeError(res, err);
  } else {
    next(err);
  }
});

const server = app.listen(app.get('port'), () => {
  console.log(`ComptoxAI API listening at http://0.0.0.0:${app.get('port')}`);
});

// Graceful shutdown: only meaningful in containers (SIGTERM from
// docker/k8s). In dev under nodemon, intercepting SIGINT breaks nodemon's
// restart on Windows (where it has no SIGUSR2 and falls back to SIGINT),
// so we leave Node's default signal behavior in place.
if (process.env.NODE_ENV === 'production') {
  const shutdown = (signal) => {
    console.log(`Received ${signal}, shutting down...`);
    server.close(async () => {
      try {
        await dbUtils.closeDriver();
      } catch (err) {
        console.error('Error closing driver:', err);
      }
      process.exit(0);
    });
    if (typeof server.closeAllConnections === 'function') {
      // Node 18.2+: kick keep-alive connections so server.close() can finish.
      server.closeAllConnections();
    }
    setTimeout(() => process.exit(1), 10000).unref();
  };

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));
}

module.exports = app;
