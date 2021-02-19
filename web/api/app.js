const express = require('express');

const conf = require('./config');
const routes = require('./routes');
const neo4jSessionCleanup = require("./middleware/neo4jSessionCleanup");

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
    swaggerDefinition: {
        info: {
            title: "ComptoxAI REST API",
            version: "1.0.0-alpha",
            description: "REST API serving ComptoxAI data to support cheminformatics applications",
        },
        host: "localhost:3000",
        basePath: "/",
    },
    apis: ["./routes/*.js"],
};

var swaggerSpec = swaggerJSDoc(swaggerOpts);

app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
app.set("port", conf.get("PORT"));

api.use(bodyParser.json());
api.use(methodOverride());

// CORS: Important for Open API and other things
api.use(function (req, res, next) {
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
    next();
});

api.use(neo4jSessionCleanup);

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
api.post("/listNodeTypes", routes.nodes.listNodeTypes);
api.post("/listRelationshipTypes", routes.relationships.listRelationshipTypes);

// handle errors
api.use(function (err, req, res, next) {
    if (err && err.status) {
        WritableStreamDefaultController(res, err);
    } else next(err);
});

app.listen(app.get("port"), () => {
    console.log(`ComptoxAI API listening at http://localhost:${port}`);
});
