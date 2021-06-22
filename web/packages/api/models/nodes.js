const _ = require('lodash');
const Node = require('./neo4j/node')

// Example node:
// const testNode = {
//     nodeType: 'Chemical',
//     commonName: "3-Fluoro-4-(1-methyl-5,6-dihydro-1,2,4-triazin-4(1H)-yl)aniline",
//     ontologyIRI: 'http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid9085',
//     identifiers: [
//         {
//             idType: "PubchemSID",
//             idValue: "316386667",
//         },
//         {
//             idType: "DTXSID",
//             idValue: "DTXSID90857126"
//         },
//         {
//             idType: "PubchemCID",
//             idValue: "71741499"
//         },
//         {
//             idType: "CasRN",
//             idValue: "1334167-69-9"
//         }
//     ],
// };

function parseNodes(neo4jResult, namespace_filter = 'ns0') {
    const all_records = neo4jResult.records.map(r => new Node(r.toObject()));
    
    const nodes = all_records.map(record => {
        console.log(Object.keys(record.node_features));
        const identifiers = Object.keys(record.node_features).reduce(function(xrefs, nf) {
            if (nf.startsWith("xref")) {
                xrefs.push({
                    idType: nf.replace(/^(xref\.)/, ""),
                    idValue: record.node_features[nf]
                });
            }
            return xrefs;
        }, []);

        return {
            nodeType: record.node_labels[0],
            commonName: record.node_features.commonName,
            identifiers: identifiers,
            ontologyIRI: record.node_features.uri,
        }
    });

    return nodes;
}

// Get a list of node types in ComptoxAI
const listNodeTypes = function (session) {
    return session.readTransaction(txc => (
        txc.run('call db.labels();')
    )).then(
        // r => parseNodeLabels(r)
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
        `RETURN n;`
    ].join(' ');

    console.log(query);

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