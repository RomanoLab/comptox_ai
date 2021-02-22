const _ = require('lodash');

const Nodes = require('../models/nodes');
const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;
const writeError = require('../helpers/response').writeError;

/**
 * @openapi
 * /api/v0/listNodeTypes:
 *   get:
 *     tags:
 *     - nodes
 *     description: Get a list of all node types in ComptoxAI
 *     summary: Get a list of all node types in ComptoxAI
 *     produces:
 *       - application/json
 *     responses:
 *       200:
 *         description: A list of node types (node labels)
 *         schema:
 *           type: array
 */
exports.listNodeTypes = function (req, res, next) {
    Nodes.listNodeTypes(dbUtils.getSession(req))
        .then(response => writeResponse(res, response))
        .catch(next);
};

exports.listNodeTypeProperties = function (req, res, next) {
    Nodes.listNodeTypeProperties(dbUtils.getSession(req), req.params.type)
        .then(response => writeResponse(res, response))
        .catch(next);
};