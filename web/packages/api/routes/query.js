const Query = require('../models/query');
const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;

/**
 * @openapi
 * /query/pattern:
 *   post:
 *     tags:
 *     - query
 *     description: Execute a multi-hop pattern query against the knowledge graph
 *     summary: Run a visual query builder pattern
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               pattern:
 *                 type: array
 *                 description: Alternating node/rel steps — [node, rel, node, rel, node, ...]
 *     responses:
 *       200:
 *         description: Pattern query results
 *       400:
 *         description: Invalid pattern
 *       404:
 *         description: No results found
 */
exports.executePattern = function (req, res, next) {
  const { pattern } = req.body;
  Query.executePattern(dbUtils.getSession(req), pattern)
    .then((response) => writeResponse(res, response))
    .catch(next);
};
