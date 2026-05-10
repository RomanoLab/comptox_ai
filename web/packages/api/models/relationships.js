const _ = require('lodash');
const Relationship = require('./neo4j/relationship');

const listRelationshipTypes = function listRelationshipTypes(session) {
  // Portable across Memgraph and Neo4j. See note in models/nodes.js.
  const query = 'MATCH ()-[r]->() RETURN DISTINCT type(r) AS relationshipType ORDER BY relationshipType;';
  return session
    .executeRead((txc) => txc.run(query))
    .then((r) => r.records.map((rec) => rec.get('relationshipType')));
};

function parseRelationships(neo4jResult) {
  return neo4jResult.records.map((r) => new Relationship(r.toObject()));
}

const findRelationshipsByNode = function findRelationshipsByNode(session, nodeId) {
  const numericId = Number.parseInt(nodeId, 10);
  if (!Number.isFinite(numericId) || numericId < 0) {
    return Promise.reject({ message: 'nodeId must be a non-negative integer', status: 400 });
  }

  const query = 'MATCH (n)-[r]-(m) WHERE id(n) = $id RETURN n, r, m';

  return session
    .executeRead((txc) => txc.run(query, { id: numericId }))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        throw { message: 'No results found for user query', query, status: 404 };
      }
      return parseRelationships(result);
    });
};

module.exports = {
  listRelationshipTypes,
  findRelationshipsByNode,
};
