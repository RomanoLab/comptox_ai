const _ = require('lodash');
const RelationshipType = require('./neo4j/relationshiptype');

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

module.exports = {
    listRelationshipTypes: listRelationshipTypes,
};
