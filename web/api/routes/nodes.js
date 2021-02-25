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
 */

/**
 * @openapi
 * /listNodeTypes:
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
 * /listNodeTypeProperties/{type}:
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
 * /node/{type}/search:
 *   get:
 *     tags:
 *     - nodes
 *     description: Find a node by querying node properties
 *     summary: 
 *     produces:
 *       - application/json
 *     responses:
 *       200:
 *         description:
 *         schema:
 *           type: array
 *           items:
 *             $ref: '#/components/schema/Node'
 */
exports.findNode = function (req, res, next) {
    Nodes.findNodeByQuery(dbUtils.getSession(req), req.params.type, req.query.field, req.query.value)
        .then(response => writeResponse(res, response))
        .catch(next);
};