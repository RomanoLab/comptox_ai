const _ = require('lodash');
const Path = require('./neo4j/path');

function parsePath(neo4jResult) {
  const path = neo4jResult.records.map((r) => new Path(r.toObject()['p']));
  return path[0];
}

const findPathByIds = function findPathByIds(session, fromId, toId) {
  const from = Number.parseInt(fromId, 10);
  const to = Number.parseInt(toId, 10);
  if (!Number.isFinite(from) || from < 0 || !Number.isFinite(to) || to < 0) {
    return Promise.reject({
      message: 'fromId and toId must be non-negative integers',
      status: 400,
    });
  }

  // Memgraph's BFS returns the single shortest path between the anchored
  // endpoints. The lower bound must be 1: a floor of 2 makes BFS return
  // nothing whenever the two nodes are directly connected (it finds the
  // 1-hop shortest path, sees it is below the floor, and gives up rather
  // than searching for a longer alternative).
  const query = [
    'MATCH p = (n)-[*BFS 1..10]-(m)',
    'WHERE id(n) = $from AND id(m) = $to',
    'RETURN p',
    'ORDER BY size(relationships(p)) ASC',
    'LIMIT 1;',
  ].join(' ');

  return session
    .executeRead((txc) => txc.run(query, { from, to }))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        throw {
          message: `Couldn't find a path of length <= 10 between node IDs ${from} and ${to}`,
          query,
          status: 404,
        };
      }
      return parsePath(result);
    });
};

module.exports = {
  findPathByIds,
};
