const _ = require('lodash');

const Relationships = require('../models/relationships');
const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;
const writeError = require('../helpers/response').writeError;

exports.listRelationshipTypes = function (req, res, next) {
    Relationships.listRelationshipTypes(dbUtils.getSession(req))
        .then(response => writeResponse(res, response))
        .catch(next);
};
