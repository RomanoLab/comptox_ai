const _ = require('lodash');

const Path = require('./neo4j/path');

const parsePath = (neo4jResult) => {
  console.log(neo4jResult);
  
  const path = neo4jResult.records.map(r => new Path(r.toObject()['p']));

  return path[0];
};

const findPathByIds = function(session, fromId, toId) {
  const query = [
    `MATCH p=shortestPath((n)-[*1..10]-(m))`,
    `WHERE id(n)=${fromId} AND id(m)=${toId} AND length(p)>1`,
    `RETURN p;`
  ].join(' ');

  return session.readTransaction(txc =>
    txc.run(query)
  ).then(result => {
    if (!_.isEmpty(result.records)) {
      return parsePath(result);
    } else {
      throw {message: `Couldn't find a path of length <= 10 between node IDs ${fromId} and ${toId}`, query: query, result: result, status: 404}
    }
  });
};

module.exports = {
  findPathByIds: findPathByIds
}

// The following object can be used as an example:
// {
//   "start": {
//     "identity": 847357,
//     "labels": [
//       "KeyEvent",
//       "MolecularInitiatingEvent"
//     ],
//     "properties": {
//       "commonName": "N/A, Unknown; N/A, Unknown ",
//       "uri": "http://jdr.bio/ontologies/comptox.owl#keyevent_294",
//       "xrefAOPWikiKEID": 294
//     }
//   },
//   "end": {
//     "identity": 847131,
//     "labels": [
//       "AdverseOutcome",
//       "KeyEvent"
//     ],
//     "properties": {
//       "commonName": "Promotion, Hepatocelluar carcinoma ",
//       "uri": "http://jdr.bio/ontologies/comptox.owl#keyevent_334",
//       "xrefAOPWikiKEID": 334
//     }
//   },
//   "segments": [
//     {
//       "start": {
//         "identity": 847357,
//         "labels": [
//           "KeyEvent",
//           "MolecularInitiatingEvent"
//         ],
//         "properties": {
//           "commonName": "N/A, Unknown; N/A, Unknown ",
//           "uri": "http://jdr.bio/ontologies/comptox.owl#keyevent_294",
//           "xrefAOPWikiKEID": 294
//         }
//       },
//       "relationship": {
//         "identity": 1301503,
//         "start": 847357,
//         "end": 844862,
//         "type": "KEINCLUDEDINAOP",
//         "properties": {}
//       },
//       "end": {
//         "identity": 844862,
//         "labels": [
//           "AOP"
//         ],
//         "properties": {
//           "commonName": "Uncharacterized liver damage leading to hepatocellular carcinoma ",
//           "uri": "http://jdr.bio/ontologies/comptox.owl#aop_1",
//           "xrefAOPWikiAOPID": 1
//         }
//       }
//     },
//     {
//       "start": {
//         "identity": 844862,
//         "labels": [
//           "AOP"
//         ],
//         "properties": {
//           "commonName": "Uncharacterized liver damage leading to hepatocellular carcinoma ",
//           "uri": "http://jdr.bio/ontologies/comptox.owl#aop_1",
//           "xrefAOPWikiAOPID":
//         }
//       },
//       "relationship": {
//         "identity": 1303209,
//         "start": 847131,
//         "end": 844862,
//         "type": "KEINCLUDEDINAOP",
//         "properties": {}
//       },
//       "end": {
//         "identity": 847131,
//         "labels": [
//           "KeyEvent",
//           "AdverseOutcome"
//         ],
//         "properties": {
//           "commonName": "Promotion, Hepatocelluar carcinoma ",
//           "uri": "http://jdr.bio/ontologies/comptox.owl#keyevent_334",
//           "xrefAOPWikiKEID": 334
//         }
//       }
//     }
//   ],
//   "length": 2.0
// }