const writeResponse = require('../helpers/response').writeResponse;
const writeError = require('../helpers/response').writeError;

const Datasets = require('../models/datasets');

/**
 * @openapi
 * /datasets/makeQsarDataset:
 *   get:
 *     tags:
 *     - datasets
 *     description: Dynamically build a QSAR dataset
 *     summary: Dynamically build a QSAR dataset for a given EPA chemical list and Tox21 assay endpoint
 *     produces:
 *       - application/json
 *     parameters:
 *       - name: assay
 *         in: query
 *         description: Tox21 assay abbreviation (see first column of https://tripod.nih.gov/tox21/assays/)
 *         required: true
 *         schema:
 *           type: string
 *       - name: chemList
 *         in: query
 *         description: EPA Chemical List acronym (see first column of https://comptox.epa.gov/dashboard/chemical-lists)
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description:
 *         schema:
 *           type: object
 */
exports.makeQsarDataset = function (req, res, next) {
    Datasets.makeQsarDataset(req.query.assay, req.query.chemList)
        .then(response => writeResponse(res, response))
        .catch(next);
}