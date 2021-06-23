const _ = require('lodash');
const Node = require('./neo4j/node')


function parseNodes(neo4jResult) {
    const nodes = neo4jResult.records.map(r => new Node(r.toObject()['n']));

    return nodes;
}

const listNodeTypes = function (session) {
    return session.readTransaction(txc => (
        txc.run('call db.labels();')
    )).then(
        r => r.records.map(rec => rec.toObject()["label"])
    );
};

function _makePropertiesList(labelSchemaData) {
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

const findNodeByQuery = function (session, type, field, value) {
    const query = [
        `MATCH (n:${type} {${field}: $value})`,
        `RETURN n, id(n);`
    ].join(' ');

    // Convert the value to an int if it looks like an int
    const intValue = parseInt(value);
    const safeCastValue = (isNaN(intValue)) ? value : intValue;
    
    return session.readTransaction(txc =>
        txc.run(query, {value: safeCastValue})
    ) .then(result => {
        if (!_.isEmpty(result.records)) {
            return parseNodes(result);
        } else {
            throw {message: 'No results found for user query', query: query, result: result, status: 404}
        }
    });
};

module.exports = {
    listNodeTypes: listNodeTypes,
    listNodeTypeProperties: listNodeTypeProperties,
    findNodeByQuery: findNodeByQuery,
};