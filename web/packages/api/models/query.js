const _ = require('lodash');
const Node = require('./neo4j/node');
const schema = require('./schema');

const SAFE_ID = /^[A-Za-z_][A-Za-z0-9_]*$/;
const MAX_HOPS = 5;
const MAX_RESULTS = 200;

function validatePattern(pattern) {
  if (!Array.isArray(pattern) || pattern.length < 1) {
    throw { message: 'Pattern must be a non-empty array', status: 400 };
  }

  const nodeSteps = pattern.filter((_, i) => i % 2 === 0);
  const relSteps = pattern.filter((_, i) => i % 2 === 1);

  if (nodeSteps.length < 1 || relSteps.length !== nodeSteps.length - 1) {
    throw { message: 'Pattern must alternate node/rel/node/rel/... with at least 1 node', status: 400 };
  }

  if (nodeSteps.length > MAX_HOPS + 1) {
    throw { message: `Pattern too long (max ${MAX_HOPS} hops)`, status: 400 };
  }

  for (const ns of nodeSteps) {
    if (!ns.nodeType || !schema.isValidNodeType(ns.nodeType)) {
      throw { message: `Invalid node type: ${ns.nodeType}`, status: 400 };
    }
    for (const f of ns.filters || []) {
      if (!SAFE_ID.test(f.field)) {
        throw { message: `Invalid field name: ${f.field}`, status: 400 };
      }
      if (!['eq', 'contains', 'startsWith'].includes(f.op)) {
        throw { message: `Invalid operator: ${f.op}`, status: 400 };
      }
    }
  }

  for (const rs of relSteps) {
    if (!rs.relType || !schema.isValidRelType(rs.relType)) {
      throw { message: `Invalid relationship type: ${rs.relType}`, status: 400 };
    }
  }
}

function buildCypher(pattern) {
  const nodeSteps = pattern.filter((_, i) => i % 2 === 0);
  const relSteps = pattern.filter((_, i) => i % 2 === 1);

  const matchParts = [];
  const whereClauses = [];
  const params = {};

  matchParts.push(`(n0:${nodeSteps[0].nodeType})`);

  for (let i = 0; i < relSteps.length; i++) {
    const rel = relSteps[i];
    const nextNode = nodeSteps[i + 1];
    matchParts.push(`-[:${rel.relType}]-(n${i + 1}:${nextNode.nodeType})`);
  }

  for (let i = 0; i < nodeSteps.length; i++) {
    for (let j = 0; j < (nodeSteps[i].filters || []).length; j++) {
      const f = nodeSteps[i].filters[j];
      const paramKey = `p${i}_${j}`;

      switch (f.op) {
        case 'eq':
          whereClauses.push(`toLower(toString(n${i}.${f.field})) = toLower($${paramKey})`);
          params[paramKey] = f.value;
          break;
        case 'contains':
          whereClauses.push(`toLower(toString(n${i}.${f.field})) CONTAINS toLower($${paramKey})`);
          params[paramKey] = f.value;
          break;
        case 'startsWith':
          whereClauses.push(`toLower(toString(n${i}.${f.field})) STARTS WITH toLower($${paramKey})`);
          params[paramKey] = f.value;
          break;
      }
    }
  }

  const returnVars = nodeSteps.map((_, i) => `n${i}`).join(', ');

  let cypher = `MATCH ${matchParts.join('')}`;
  if (whereClauses.length > 0) {
    cypher += `\nWHERE ${whereClauses.join(' AND ')}`;
  }
  cypher += `\nRETURN DISTINCT ${returnVars}\nLIMIT ${MAX_RESULTS}`;

  return { cypher, params };
}

function parsePatternResults(neo4jResult, nodeCount) {
  return neo4jResult.records.map((record) => {
    const row = [];
    for (let i = 0; i < nodeCount; i++) {
      row.push(new Node(record.get(`n${i}`)));
    }
    return row;
  });
}

const executePattern = function executePattern(session, pattern) {
  validatePattern(pattern);

  const nodeSteps = pattern.filter((_, i) => i % 2 === 0);
  const { cypher, params } = buildCypher(pattern);

  return session
    .executeRead((txc) => txc.run(cypher, params))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        throw { message: 'No results found for pattern query', status: 404 };
      }
      return {
        results: parsePatternResults(result, nodeSteps.length),
        count: result.records.length,
        cypher,
      };
    });
};

module.exports = { executePattern, buildCypher, validatePattern };
