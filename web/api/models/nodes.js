const _ = require('lodash');
const NodeType = require('./neo4j/nodetype');

function parseNodeLabels(neo4jResult, namespace_filter = 'ns0') {
    const all_records = neo4jResult.records.map(r => new NodeType(r.toObject()));
    return all_records.filter(ar => ar['namespace'] === namespace_filter).map(r => r['label']);
}

// Get a list of node types in ComptoxAI
const listNodeTypes = function (session) {
    return session.readTransaction(txc => (
        txc.run('call db.labels()')
    )).then(
        r => parseNodeLabels(r)
    );
};

function _makePropertiesList(labelSchemaData) {
    //console.log(labelSchemaData);
    //console.log(labelSchemaData[0].toObject());
    const labelSchemaDataObjects = labelSchemaData.map(r => r.toObject());
    const propsList = labelSchemaDataObjects.map(r => ({
        property: r['property'],
        type: r['type']
    }));
    return propsList;
};

const listNodeTypeProperties = function (session, nodeTypeLabel) {
    const query = [
        'CALL apoc.meta.schema() YIELD value as schemaMap',
        'UNWIND keys(schemaMap) as label',
        'WITH label, schemaMap[label] as data',
        'WHERE data.type = "node" AND label = $nodeTypeLabel',
        'UNWIND keys(data.properties) as property',
        'WITH label, property, data.properties[property] as propData',
        'RETURN label, property,',
        'propData.type as type,',
        'propData.indexed as isIndexed,',
        'propData.existence as existenceConstraint'
    ].join('\n');
    
    return session.readTransaction(txc =>
        txc.run(query, {nodeTypeLabel: nodeTypeLabel})
    ).then(result => {
        if (!_.isEmpty(result.records)) {
            return _makePropertiesList(result.records);
        } else {
            throw {message: 'Node label not found in database', status: 404}
        }
    });
};

module.exports = {
    listNodeTypes: listNodeTypes,
    listNodeTypeProperties: listNodeTypeProperties,
};