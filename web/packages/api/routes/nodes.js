const _ = require('lodash');

const Nodes = require('../models/nodes');
const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;
const writeError = require('../helpers/response').writeError;

/**
 * @openapi
 * components:
 *   schemas:
 *     Node:
 *       type: object
 *       properties:
 *         nodeId:
 *           type: integer
 *         nodeType:
 *           type: string
 *         commonName:
 *           type: string
 *         nodeFeatures:
 *           type: array
 *           items:
 *             type: object
 *             properties:
 *               featType:
 *                 type: string
 *               featValue:
 *                 oneOf:
 *                   - type: string
 *                   - type: integer
 *         identifiers:
 *           type: array
 *           items:
 *             type: object
 *             properties:
 *               idType:
 *                 type: string
 *               idValue:
 *                 oneOf:
 *                   - type: string
 *                   - type: integer
 *         ontologyIRI:
 *           type: string
 */

/**
 * @openapi
 * /nodes/listNodeTypes:
 *   get:
 *     tags:
 *     - nodes
 *     description: Get a list of all node types in ComptoxAI
 *     summary: Get a list of all node types in ComptoxAI
 *     produces:
 *       - application/json
 *     responses:
 *       200:
 *         description: Successful query
 *         schema:
 *           type: array
 *           items:
 *             type: string
 */
exports.listNodeTypes = function (req, res, next) {
    Nodes.listNodeTypes(dbUtils.getSession(req))
        .then(response => writeResponse(res, response))
        .catch(next);
};

/**
 * @openapi
 * /nodes/listNodeTypeProperties/{type}:
 *   get:
 *     tags:
 *     - nodes
 *     description: List properties defined for a particular node type
 *     summary: Get a list of properties defined for a particular node type
 *     produces:
 *       - application/json
 *     parameters:
 *       - name: type
 *         in: path
 *         description: Node type label (as, e.g., returned by `/listNodeTypes`)
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Successful response
 *         schema:
 *           type: array
 *           items: 
 *             type: string
 *       400:
 *         description: Invalid node type was passed
 */
exports.listNodeTypeProperties = function (req, res, next) {
    Nodes.listNodeTypeProperties(dbUtils.getSession(req), req.params.type)
        .then(response => writeResponse(res, response))
        .catch(next);
};

/**
 * @openapi
 * /nodes/{type}/search:
 *   get:
 *     tags:
 *     - nodes
 *     description: Find a node by querying node properties
 *     summary: Search for a node using string matching on a specific field
 *     produces:
 *       - application/json
 *     parameters:
 *       - name: type
 *         in: path
 *         description: Node type to be queried
 *         required: true
 *         schema:
 *           type: string
 *       - name: field
 *         in: query
 *         description: Name of a node property against which to run the query
 *         required: true
 *         schema:
 *           type: string
 *       - name: value
 *         in: query
 *         description: Value to match
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description:
 *         schema:
 *           type: array
 *           items:
 *             $ref: '#/components/schemas/Node'
 */
 exports.findNode = function (req, res, next) {
    Nodes.findNodeCaseInsensitive(dbUtils.getSession(req), req.params.type, req.query.field, req.query.value)
        .then(response => writeResponse(res, response))
        .catch(next);
};
// exports.findNode = function (req, res, next) {
//     Nodes.findNodeByQuery(dbUtils.getSession(req), req.params.type, req.query.field, req.query.value)
//         .then(response => writeResponse(res, response))
//         .catch(next);
// };

/**
 * @openapi
 * /nodes/{type}/searchContains:
 *   get:
 *     tags:
 *     - nodes
 *     description: Find a node by querying node properties, where the search string doesn't need to be an exact match
 *     summary: Search for a node where a certain field contains a query string
 *     produces:
 *       - application/json
 *     parameters:
 *       - name: type
 *         in: path
 *         description: Name of a node property against which to run the query
 *         required: true
 *         schema:
 *           type: string
 *       - name: field
 *         in: query
 *         description: Name of a node property against which to run the query
 *         required: true
 *         schema:
 *           type: string
 *       - name: value
 *         in: query
 *         description: Value to match
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description:
 *         schema:
 *           type: array
 *           items:
 *             $ref: '#/components/schemas/Node'
  */
exports.findNodeContains = function (req, res, next) {
    Nodes.findNodeByQueryContains(dbUtils.getSession(req), req.params.type, req.query.field, req.query.value)
        .then(response => writeResponse(res, response))
        .catch(next);
};

/**
 * @openapi
 * /nodes/fetchById/{id}:
 *   get:
 *     tags:
 *     - nodes
 *     description: Find a single node by its Neo4j ID
 *     summary: Fetch a single node using its Neo4j ID
 *     produces:
 *       - application/json
 *     parameters:
 *       - name: id
 *         in: path
 *         description: Neo4j node ID to fetch from the graph database
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description:
 *         schema:
 *           type: object
 *           properties:
 *             $ref: '#/components/schemas/Node'
 */
exports.fetchById = function (req, res, next) {
    Nodes.fetchById(dbUtils.getSession(req), req.params.id)
        .then(response => writeResponse(res, response))
        .catch(next);
};

exports.fetchChemicalByDtsxid = function (req, res, next) {
    Nodes.fetchChemicalByDtsxid(dbUtils.getSession(req), req.params.id)
        .then(response => writeResponse(res, response))
        .catch(next);
};