const Schema = require('../models/schema');
const writeResponse = require('../helpers/response').writeResponse;

/**
 * @openapi
 * /schema/edges:
 *   get:
 *     tags:
 *     - schema
 *     description: Get the edge schema — valid (source, relationship, target) triples with human-readable labels
 *     summary: Get edge schema for query builder
 *     responses:
 *       200:
 *         description: Edge schema
 */
exports.getEdgeSchema = function (req, res, next) {
  try {
    writeResponse(res, Schema.getEdgeSchema());
  } catch (err) {
    next(err);
  }
};
