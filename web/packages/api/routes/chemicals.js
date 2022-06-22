const Chemicals = require('../models/chemicals');
const writeResponse = require('../helpers/response').writeResponse;

/**
 * @openapi
 * /chemicals/structureSearch:
 *   get:
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
exports.structureSearch = function (req, res, next) {
    Chemicals.runStructureSearch(req)
        .then(response => writeResponse(res, response))
        .catch(next);
}