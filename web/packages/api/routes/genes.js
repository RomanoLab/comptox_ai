const Genes = require('../models/genes');
const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;

/**
 * @openapi
 * /genes/fetchBySymbol/{symbol}:
 *   get:
 *     tags:
 *     - genes
 *     summary: Fetch a Gene node by HGNC gene symbol
 *     description: |
 *       Look up a single Gene node by its HGNC gene symbol (e.g. `TP53`,
 *       `BRCA1`, `ESR1`). The match is case-insensitive. Returns an array
 *       because some symbols can appear in more than one Gene node (e.g.,
 *       pseudogenes or paralogs); for unambiguous symbols the array has a
 *       single element.
 *     produces:
 *       - application/json
 *     parameters:
 *       - name: symbol
 *         in: path
 *         required: true
 *         description: HGNC gene symbol. Case-insensitive.
 *         schema:
 *           type: string
 *           example: TP53
 *     responses:
 *       200:
 *         description: Matching Gene node(s)
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Node'
 *       400:
 *         description: Invalid or empty symbol
 *       404:
 *         description: No gene found for the given symbol
 */
exports.fetchBySymbol = function fetchBySymbol(req, res, next) {
  Genes.fetchBySymbol(dbUtils.getSession(req), req.params.symbol)
    .then((response) => writeResponse(res, response))
    .catch(next);
};
