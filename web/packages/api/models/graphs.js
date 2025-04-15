const _ = require('lodash');

const Graph = require('./neo4j/graph');

// Return `true` if start, end, and relationship type are all identical
const pathSegmentsAreEqual = function(seg1, seg2) {
    const sameStart = (seg1['relationship']['start'].equals(seg2['relationship']['start']));
    const sameEnd = (seg1['relationship']['end'].equals(seg2['relationship']['end']));

    const sameRelType = seg1['relationship']['type'] === seq2['relationship']['type'];

    return [sameStart, sameRelType, sameEnd].every(x => x === true);

}

const parsePathsToGraph = function (neo4jResult) {
    
    // Extract all PathSegments
    const paths = neo4jResult['records'];
    const allSegments = paths.map(p => p['_fields'][0]['segments']).flat();

    // Collapse duplicate PathSegments
    const uniqSegments = _.uniqBy(allSegments, 'relationship.identity')

    // Get all distinct nodes, based on unique URI
    const startNodes = uniqSegments.map(s => s['start']);
    const endNodes = uniqSegments.map(s => s['end']);
    const uniqNodes = _.uniqBy(startNodes.concat(endNodes), 'properties.uri');
    
    const graph = {
        nodes: uniqNodes,
        relationships: uniqSegments.map(ss => ss['relationship'])
    }

    return new Graph(graph);
}

// Run an arbitrary Cypher query and return a Graph
const getGraphFromPaths = function (session, cypherQuery) {
    return session.readTransaction(txc =>
        txc.run(cypherQuery)
    ).then(result => {
        if  (!_.isEmpty(result.records)) {
            return parsePathsToGraph(result);
        } else {
            throw {message: 'No results found for user query', query: query, result: result, status: 404}
        }
    });
};

module.exports = {
    getGraphFromPaths: getGraphFromPaths
};
