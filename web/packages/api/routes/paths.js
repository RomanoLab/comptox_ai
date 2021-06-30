const dbUtils = require('../neo4j/dbUtils');
const writeResponse = require('../helpers/response').writeResponse;
const writeError = require('../helpers/response').writeError;

const Paths = require('../models/paths');

exports.findByIds = function(req, res, next) {
  Paths.findPathByIds(dbUtils.getSession(req), req.query.fromId, req.query.toId)
    .then(response => writeResponse(res, response))
    .catch(next);
};