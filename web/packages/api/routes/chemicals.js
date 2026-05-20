const Chemicals = require('../models/chemicals');
const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;

/**
 * @openapi
 * /chemicals/structureSearch:
 *   post:
 *     tags:
 *     - chemicals
 *     description: Search for structures similar to a query structure
 *     summary: Search for structures similar to a query structure
 *     produces:
 *       - application/json
 *     requestBody:
 *       description: MOL file as string
 *       content:
 *         'text/plain'
 *     responses:
 *       200:
 *         description: Successful query
 *         schema:
 *           type: array
 */
exports.structureSearch = function structureSearch(req, res, next) {
  Chemicals.runStructureSearch(req)
    .then((response) => writeResponse(res, response))
    .catch(next);
};

/**
 * @openapi
 * /chemicals/fetchByCas/{cas}:
 *   get:
 *     tags:
 *     - chemicals
 *     summary: Fetch a Chemical node by CAS Registry Number
 *     description: |
 *       Look up a single Chemical node by its CAS Registry Number (CASRN).
 *       This is typically more convenient than `/nodes/fetchChemicalByDtsxid`
 *       for users coming from the toxicology / cheminformatics literature,
 *       where CAS numbers are the canonical identifier. The match is exact
 *       on `xrefCasRN`.
 *     produces:
 *       - application/json
 *     parameters:
 *       - name: cas
 *         in: path
 *         required: true
 *         description: |
 *           CAS Registry Number, formatted as `nnnnnn-nn-n` (the dashes are
 *           required). Example: `80-05-7` (Bisphenol A).
 *         schema:
 *           type: string
 *           example: 80-05-7
 *     responses:
 *       200:
 *         description: The matching Chemical node
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Node'
 *       400:
 *         description: Invalid or empty CAS Registry Number
 *       404:
 *         description: No chemical found for the given CAS Registry Number
 */
exports.fetchByCas = function fetchByCas(req, res, next) {
  Chemicals.fetchByCas(dbUtils.getSession(req), req.params.cas)
    .then((response) => writeResponse(res, response))
    .catch(next);
};

/**
 * @openapi
 * /chemicals/{dtsxid}/genes:
 *   get:
 *     tags:
 *     - chemicals
 *     summary: List genes whose expression is modulated by a chemical
 *     description: |
 *       Returns the Gene nodes connected to the given Chemical via
 *       `chemicalIncreasesExpression` and/or `chemicalDecreasesExpression`
 *       edges. Each returned node carries an extra `relationshipTypes`
 *       array listing which of those two edge types was observed (a gene
 *       can appear via both, e.g. dose-dependent reversal).
 *
 *       Some chemicals touch thousands of genes (Bisphenol A has ~8000
 *       linked Gene nodes), so results are always paginated. Use the
 *       `limit` and `offset` query parameters to walk the result set.
 *     produces:
 *       - application/json
 *     parameters:
 *       - name: dtsxid
 *         in: path
 *         required: true
 *         description: |
 *           DSSTOX substance identifier of the chemical (e.g.,
 *           `DTXSID7020182` for Bisphenol A). Must match the literal pattern
 *           `DTXSID` followed by digits.
 *         schema:
 *           type: string
 *           example: DTXSID7020182
 *       - name: limit
 *         in: query
 *         required: false
 *         description: Maximum genes to return. Defaults to 100, capped at 1000.
 *         schema:
 *           type: integer
 *           minimum: 1
 *           maximum: 1000
 *           default: 100
 *       - name: offset
 *         in: query
 *         required: false
 *         description: Number of genes to skip before returning results. Use with `limit` to page.
 *         schema:
 *           type: integer
 *           minimum: 0
 *           default: 0
 *       - name: direction
 *         in: query
 *         required: false
 *         description: |
 *           Filter by direction of regulation:
 *           - `increases` — only `chemicalIncreasesExpression` edges
 *           - `decreases` — only `chemicalDecreasesExpression` edges
 *           - `both` (default) — either edge type
 *         schema:
 *           type: string
 *           enum: [increases, decreases, both]
 *           default: both
 *     responses:
 *       200:
 *         description: Page of Gene nodes connected to the chemical
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 allOf:
 *                   - $ref: '#/components/schemas/Node'
 *                   - type: object
 *                     properties:
 *                       relationshipTypes:
 *                         type: array
 *                         description: Which of the two regulation edge types connect this gene to the chemical.
 *                         items:
 *                           type: string
 *                           enum: [chemicalIncreasesExpression, chemicalDecreasesExpression]
 *       400:
 *         description: Invalid dtsxid or direction
 */
exports.findGenes = function findGenes(req, res, next) {
  const opts = {
    limit: req.query.limit,
    offset: req.query.offset,
    direction: req.query.direction,
  };
  Chemicals.findGenesForChemical(dbUtils.getSession(req), req.params.dtsxid, opts)
    .then((response) => writeResponse(res, response))
    .catch(next);
};

/**
 * @openapi
 * /chemicals/{dtsxid}/aops:
 *   get:
 *     tags:
 *     - chemicals
 *     summary: List Adverse Outcome Pathways implicated by a chemical
 *     description: |
 *       Returns the AOP nodes reachable from the given Chemical via a
 *       Key Event intermediary, i.e. via the path:
 *
 *           (Chemical) -[:keyEventTriggeredBy]- (KeyEvent)
 *                       -[:aopIncludesKE|keIncludedInAOP]- (AOP)
 *
 *       This is the canonical "what AOPs does this chemical implicate?"
 *       query. Only ~600 chemicals currently have direct linkage to Key
 *       Events in ComptoxAI, so most chemicals will return an empty array.
 *       Good test substances: `DTXSID2021315` (TCDD), `DTXSID5020732`
 *       (Ibuprofen), `DTXSID7022592` (Amiodarone).
 *     produces:
 *       - application/json
 *     parameters:
 *       - name: dtsxid
 *         in: path
 *         required: true
 *         description: DSSTOX substance identifier of the chemical.
 *         schema:
 *           type: string
 *           example: DTXSID2021315
 *       - name: limit
 *         in: query
 *         required: false
 *         description: Maximum AOPs to return. Defaults to 100, capped at 1000.
 *         schema:
 *           type: integer
 *           minimum: 1
 *           maximum: 1000
 *           default: 100
 *       - name: offset
 *         in: query
 *         required: false
 *         description: Number of AOPs to skip before returning results.
 *         schema:
 *           type: integer
 *           minimum: 0
 *           default: 0
 *     responses:
 *       200:
 *         description: Page of AOP nodes reachable from the chemical
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Node'
 *       400:
 *         description: Invalid dtsxid
 */
exports.findAops = function findAops(req, res, next) {
  const opts = {
    limit: req.query.limit,
    offset: req.query.offset,
  };
  Chemicals.findAopsForChemical(dbUtils.getSession(req), req.params.dtsxid, opts)
    .then((response) => writeResponse(res, response))
    .catch(next);
};
