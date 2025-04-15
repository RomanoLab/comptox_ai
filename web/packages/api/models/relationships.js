const _ = require('lodash');
const RelationshipType = require('./neo4j/relationshiptype');
const Relationship = require('./neo4j/relationship');

function parseRelationshipLabels(neo4jResult, namespace_filter = 'ns0') {
    const all_records = neo4jResult.records.map(r => new RelationshipType(r.toObject()));
    return all_records.filter(ar => ar['namespace'] === namespace_filter).map(r => r['label']);
}

const listRelationshipTypes = function (session) {
    return session.readTransaction(txc => (
        txc.run('call db.relationshipTypes()')
    )).then(
        r => parseRelationshipLabels(r)
    );
};

function parseRelationships(neo4jResult) {
    const relationships = neo4jResult.records.map(r => new Relationship(r.toObject()));

    return relationships;
};

const findRelationshipsByNode = function (session, nodeId) {
    const query = [
        `MATCH (n)-[r]-(m)`,
        `WHERE id(n) = ${nodeId}`,
        `RETURN n, r, m`
    ].join(' ');

    return session.readTransaction(txc =>
        txc.run(query)
    ).then(result => {
        if (!_.isEmpty(result.records)) {
            return parseRelationships(result);
        } else {
            throw {message: 'No results found for user query', query: query, result: result, status: 404}
        }
    });
};

module.exports = {
    listRelationshipTypes: listRelationshipTypes,
    findRelationshipsByNode: findRelationshipsByNode,
};
