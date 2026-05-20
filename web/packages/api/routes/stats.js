const Stats = require('../models/stats');
const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;

/**
 * @openapi
 * components:
 *   schemas:
 *     GraphStats:
 *       type: object
 *       properties:
 *         nodes:
 *           type: object
 *           description: |
 *             Number of nodes in the graph keyed by label. A node carrying
 *             multiple labels contributes to each of its labels' counts.
 *           additionalProperties:
 *             type: integer
 *             example: 880210
 *         edges:
 *           type: object
 *           description: Number of edges in the graph keyed by relationship type.
 *           additionalProperties:
 *             type: integer
 *             example: 200959
 *         generatedAt:
 *           type: string
 *           format: date-time
 *           description: Server time at which this snapshot was computed.
 *         cacheTtlSeconds:
 *           type: integer
 *           description: |
 *             How long this response will be served from the in-process cache
 *             before being recomputed. Clients can use this to decide how
 *             often to poll.
 *           example: 604800
 */

/**
 * @openapi
 * /stats:
 *   get:
 *     tags:
 *     - stats
 *     summary: Graph-wide node and edge counts
 *     description: |
 *       Returns the number of nodes per label and edges per relationship type
 *       across the entire ComptoxAI graph database. Useful for landing-page
 *       summaries, monitoring (sudden drops typically indicate ingest
 *       problems), and pagination planning. The response is cached
 *       in-process for 7 days — the underlying queries scan the whole graph,
 *       and the data changes infrequently enough that weekly recomputation
 *       is plenty. `cacheTtlSeconds` in the response reports the cache
 *       window length; `generatedAt` tells you when the current snapshot
 *       was computed.
 *     produces:
 *       - application/json
 *     responses:
 *       200:
 *         description: Successful query
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/GraphStats'
 *       503:
 *         description: Database unreachable
 */
exports.getStats = function getStats(req, res, next) {
  Stats.getStats(dbUtils.getSession(req))
    .then((response) => writeResponse(res, response))
    .catch(next);
};
