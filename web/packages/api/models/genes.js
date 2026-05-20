const _ = require('lodash');
const Node = require('./neo4j/node');

function parseNodes(neo4jResult) {
  return neo4jResult.records.map((r) => new Node(r.toObject()['n']));
}

const fetchBySymbol = function fetchBySymbol(session, symbol) {
  if (!symbol || typeof symbol !== 'string') {
    return Promise.reject({ message: 'symbol must be a non-empty string', status: 400 });
  }
  const upper = symbol.toUpperCase();
  const query = 'MATCH (n:Gene) WHERE toUpper(n.geneSymbol) = $symbol RETURN n;';
  return session
    .executeRead((txc) => txc.run(query, { symbol: upper }))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        throw { message: `No gene found for symbol ${symbol}`, query, status: 404 };
      }
      return parseNodes(result);
    });
};

module.exports = {
  fetchBySymbol,
};
