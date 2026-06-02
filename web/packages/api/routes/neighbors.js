const Neighbors = require('../models/neighbors');
const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;

/**
 * @openapi
 * /nodes/{id}/neighborCounts:
 *   get:
 *     tags:
 *     - neighbors
 *     description: Get counts of neighbors grouped by relationship type
 *     summary: Neighbor relationship type counts for a node
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Array of {relType, targetType, count}
 */
exports.getNeighborCounts = function (req, res, next) {
  Neighbors.getNeighborCounts(dbUtils.getSession(req), req.params.id)
    .then((response) => writeResponse(res, response))
    .catch(next);
};

/**
 * @openapi
 * /nodes/{id}/neighbors:
 *   get:
 *     tags:
 *     - neighbors
 *     description: Get neighbor nodes, optionally filtered by relationship type
 *     summary: Expand a node's neighbors
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         schema:
 *           type: integer
 *       - name: relType
 *         in: query
 *         schema:
 *           type: string
 *       - name: limit
 *         in: query
 *         schema:
 *           type: integer
 *           default: 50
 *     responses:
 *       200:
 *         description: Object with nodes and edges arrays
 */
exports.getNeighbors = function (req, res, next) {
  Neighbors.getNeighbors(dbUtils.getSession(req), req.params.id, req.query.relType, req.query.limit)
    .then((response) => writeResponse(res, response))
    .catch(next);
};
