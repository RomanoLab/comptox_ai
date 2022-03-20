const Graphs = require('../models/graphs');

const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;

/**
 * @openapi
 * components:
 *   schemas:
 *     Graph:
 *       type: object
 *       properties:
 *         nodes:
 *           type: array
 *           items:
 *             $ref: '#/components/schemas/Node'
 *         relationships:
 *           type: array
 *           items:
 *             $ref: '#/components/schemas/Relationship'
 */

exports.testGraphs = function (req, res, next) {
    const cypherQuery = "MATCH p=(n)-[r:CHEMICALBINDSGENE]->(m) RETURN p LIMIT 25;";
    
    Graphs.getGraphFromPaths(dbUtils.getSession(req), cypherQuery)
        .then(response => writeResponse(res, response))
        .catch(next);
};
