const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;
const writeError = require('../helpers/response').writeError;

const Paths = require('../models/paths');

/**
 * @openapi
 * components:
 *   schemas:
 *     Path:
 *       type: object
 *       properties:
 *         nodes:
 *           type: array
 *           items:
 *             type: object
 *             properties:
 *               id:
 *                 type: integer
 *               labels:
 *                 type: array
 *                 items:
 *                   type: string
 *               name:
 *                 type: string
 *         relationships:
 *           type: array
 *           items:
 *             type: object
 *             properties:
 *               source:
 *                 type: integer
 *               target:
 *                 type: integer
 *               relType:
 *                 type: string
 */

/** 
 * @openapi
 * /paths/findByIds:
 *   get:
 *     tags:
 *     - paths
 *     description: Use a start node ID and end node ID to retrieve a shortest path connecting those nodes
 *     summary: Use a start node ID and end node ID to retrieve a shortest path connecting those nodes
 *     produces:
 *       - application/json
 *     parameters:
 *       - name: fromId
 *         in: query
 *         required: true
 *         schema:
 *           type: integer
 *       - name: toId
 *         in: query
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Successful query
 *         schema:
 *           $ref: '#/components/schemas/Path'
 */
exports.findByIds = function(req, res, next) {
  Paths.findPathByIds(dbUtils.getSession(req), req.query.fromId, req.query.toId)
    .then(response => writeResponse(res, response))
    .catch(next);
};