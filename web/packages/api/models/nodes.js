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

const findNodeCaseInsensitive = function (session, type, field, value) {
    // Convert the value to an int if it looks like an int
    const intValue = parseInt(value);
    const safeCastValue = (isNaN(intValue)) ? value : intValue;

    // Case insensitive matching using Cypher's regex syntax:
    let query;
    if (isNaN(intValue)) {
        query = [
            `MATCH (n:${type})`,
            `WHERE n.${field} =~ '(?i)${value}'`,
            `RETURN n, id(n);`
        ].join(' ');
    } else {
        query = [
            `MATCH (n:${type})`,
            `WHERE n.${field} = ${value}`,
            `RETURN n, id(n);`
        ].join(' ');
    }
    
    return session.readTransaction(txc =>
        txc.run(query)
    ).then(result => {
        if (!_.isEmpty(result.records)) {
            return parseNodes(result);
        } else {
            throw {message: 'No results found for user query', query: query, result: result, status: 404}
        }
    });
};

const findNodeByQuery = function (session, type, field, value) {
    // Convert the value to an int if it looks like an int
    const intValue = parseInt(value);
    const safeCastValue = (isNaN(intValue)) ? value : intValue;
    
    const query = [
        `MATCH (n:${type} {${field}: $value})`,
        `RETURN n, id(n);`
    ].join(' ');
    
    return session.readTransaction(txc =>
        txc.run(query, {value: safeCastValue})
    ).then(result => {
        if (!_.isEmpty(result.records)) {
            return parseNodes(result);
        } else {
            throw {message: 'No results found for user query', query: query, result: result, status: 404}
        }
    });
};

const findNodeByQueryContains = function (session, type, field, value) {
    // Convert the value to an int if it looks like an int
    const intValue = parseInt(value);
    const safeCastValue = (isNaN(intValue)) ? value : intValue;

    let query;
    if (isNaN(intValue)) {
        query = [
            `MATCH (n:${type})`,
            `WHERE n.${field} =~ '(?i).*${value}.*'`,
            `RETURN n, id(n);`
        ].join(' ');
    } else {
        query = [
            `MATCH (n:${type})`,
            `WHERE n.${field} = ${value}`,
            `RETURN n, id(n);`
        ].join(' ');
    }

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

const fetchById = function (session, id) {
    const query = `MATCH (n) WHERE id(n) = ${id} RETURN n;`

    return session.readTransaction(txc =>
        txc.run(query)
    ).then(result => {
        if (!_.isEmpty(result.records)) {
            return parseNodes(result);
        } else {
            throw {message: `No nodes found for id ${id}`, query: query, result: result, status: 404}
        }
    });
};

module.exports = {
    listNodeTypes: listNodeTypes,
    listNodeTypeProperties: listNodeTypeProperties,
    findNodeCaseInsensitive: findNodeCaseInsensitive,
    findNodeByQuery: findNodeByQuery,
    findNodeByQueryContains: findNodeByQueryContains,
    fetchById: fetchById,
};