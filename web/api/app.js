const express = require('express');

const nconf = require('./config');
const routes = require('./routes');
const neo4jSessionCleanup = require("./middleware/neo4jSessionCleanup");
const writeError = require("./helpers/response").writeError;

const app = express();
const swaggerJSDoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');
const bodyParser = require('body-parser');
const methodOverride = require('method-override');

const port = 3000

// Planned routes:
// /info
// /about
// /stats
// /listTables
// 

var swaggerOpts = {
    definition: {
        openapi: '3.0.3',
        info: {
            title: "ComptoxAI REST API",
            version: "1.0.0-alpha",
            description: "REST API serving ComptoxAI data to support cheminformatics applications",
        },
        servers: [
            {
                url: "http://localhost:3000",
                description: "Default URL when run as a local development environment"
            },
            {
                url: "http://comptox.ai/api",
                description: "Eventual public-facing instance of ComptoxAI's API"
            }
        ],
        host: "localhost:3000",
    },
    apis: ["api/routes/*.js", "api/*.js"],
};

// Make swagger/openapi documentation
var swaggerSpec = swaggerJSDoc(swaggerOpts);
app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
app.set("port", nconf.get("PORT"));

app.use(bodyParser.json());
app.use(methodOverride());

// CORS: Important for Open API and other things
app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Credentials", "true");
    res.header(
        "Access-Control-Allow-Methods",
        "GET,HEAD,OPTIONS,POST,PUT,DELETE"
    );
    res.header(
        "Access-Control-Allow-Headers",
        "Origin, X-Requested-With, Content-Type, Accept, Authorization"
    );
    // Make everything be returned as JSON
    res.header("Content-Type", 'application/json');
    next();
});

app.use(neo4jSessionCleanup);

/**
 * @openapi
 * /:
 *   get:
 *     description: Welcome to ComptoxAI's REST API
 *     responses:
 *       200:
 *         description: Returns the string 'Hello, World!'
 */
app.get('/', (req, res) => {
    res.send('Hello, World!')
})

// main API routes
app.get("/listNodeTypes", routes.nodes.listNodeTypes);
app.get("/listNodeTypeProperties/:type", routes.nodes.listNodeTypeProperties);
//app.get("/node/:type/:id", routes.nodes.findNodeById); // TODO: What qualifies as an ID?
app.get("/node/:type/search?", routes.nodes.findNode);
app.get("/listRelationshipTypes", routes.relationships.listRelationshipTypes);
//app.get("/listRelationshipTypeProperties/:type", routes.relationships.listRelationshipTypeProperties);

// handle errors
app.use(function (err, req, res, next) {
    if (err && err.status) {
        writeError(res, err);
    } else next(err);
});

app.listen(app.get("port"), () => {
    console.log(`ComptoxAI API listening at http://localhost:${port}`);
});
