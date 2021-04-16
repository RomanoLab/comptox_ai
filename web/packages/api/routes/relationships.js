const _ = require('lodash');

const Relationships = require('../models/relationships');
const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;
const writeError = require('../helpers/response').writeError;

/**
 * @openapi
 * components:
 *   schemas:
 *     Relationship:
 *       type: object
 */

/**
 * @openapi
 * /relationships/listRelationshipTypes:
 *   get:
 *     tags:
 *     - relationships
 *     description: Get a list of all relationship types in ComptoxAI
 *     summary: Get a list of all relationship types in ComptoxAI
 *     produces:
 *       - application/json
 *     responses:
 *       200:
 *         description: Successful query
 *         schema:
 *           type: array
 *           items:
 *             type: string
 */
exports.listRelationshipTypes = function (req, res, next) {
    Relationships.listRelationshipTypes(dbUtils.getSession(req))
        .then(response => writeResponse(res, response))
        .catch(next);
};

/**
 * @openapi
 * /relationships/listRelationshipTypeProperties/{type}
 */
// exports.listRelationshipTypeProperties = function (req, res, next) {
//     Relationships.listRelationshipTypeProperties(dbUtils.getSession(req), req.params.type)
//         .then(response => writeResponse(res, response))
//         .catch(next);
// };