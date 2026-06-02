const _ = require('lodash');
const Node = require('./neo4j/node');

const SAFE_ID = /^[A-Za-z_][A-Za-z0-9_]*$/;

const getNeighborCounts = function getNeighborCounts(session, nodeId) {
  const numericId = Number.parseInt(nodeId, 10);
  if (!Number.isFinite(numericId) || numericId < 0) {
    return Promise.reject({ message: 'nodeId must be a non-negative integer', status: 400 });
  }

  const query = `
    MATCH (n)-[r]-(m)
    WHERE id(n) = $id
    RETURN type(r) AS relType, labels(m)[0] AS targetType, count(*) AS cnt
    ORDER BY cnt DESC
  `;

  return session
    .executeRead((txc) => txc.run(query, { id: numericId }))
    .then((result) =>
      result.records.map((rec) => ({
        relType: rec.get('relType'),
        targetType: rec.get('targetType'),
        count: rec.get('cnt').toNumber ? rec.get('cnt').toNumber() : rec.get('cnt'),
      }))
    );
};

const getNeighbors = function getNeighbors(session, nodeId, relType, limit) {
  const numericId = Number.parseInt(nodeId, 10);
  if (!Number.isFinite(numericId) || numericId < 0) {
    return Promise.reject({ message: 'nodeId must be a non-negative integer', status: 400 });
  }

  const maxResults = Math.min(Number.parseInt(limit, 10) || 50, 200);

  let query;
  const params = { id: numericId };

  if (relType && SAFE_ID.test(relType)) {
    query = `
      MATCH (n)-[r:${relType}]-(m)
      WHERE id(n) = $id
      RETURN n, r, m
      LIMIT ${maxResults}
    `;
  } else {
    query = `
      MATCH (n)-[r]-(m)
      WHERE id(n) = $id
      RETURN n, r, m
      LIMIT ${maxResults}
    `;
  }

  return session
    .executeRead((txc) => txc.run(query, params))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        return { nodes: [], edges: [] };
      }

      const nodesMap = new Map();
      const edges = [];

      result.records.forEach((rec) => {
        const sourceRaw = rec.get('n');
        const targetRaw = rec.get('m');
        const relRaw = rec.get('r');

        const sourceId = sourceRaw.identity.toNumber();
        const targetId = targetRaw.identity.toNumber();

        if (!nodesMap.has(sourceId)) {
          nodesMap.set(sourceId, new Node(sourceRaw));
        }
        if (!nodesMap.has(targetId)) {
          nodesMap.set(targetId, new Node(targetRaw));
        }

        edges.push({
          source: sourceId,
          target: targetId,
          relType: relRaw.type,
          relId: relRaw.identity.toNumber(),
        });
      });

      return {
        nodes: Array.from(nodesMap.values()),
        edges,
      };
    });
};

module.exports = { getNeighborCounts, getNeighbors };
