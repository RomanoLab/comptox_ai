const CACHE_TTL_MS = 5 * 60 * 1000;
let cache = null;
let cacheExpiresAt = 0;

const toInt = (v) =>
  v && typeof v === 'object' && typeof v.toNumber === 'function' ? v.toNumber() : v;

const getStats = function getStats(session) {
  const now = Date.now();
  if (cache && now < cacheExpiresAt) {
    return Promise.resolve(cache);
  }

  const nodeQuery =
    'MATCH (n) UNWIND labels(n) AS label RETURN label, count(*) AS count ORDER BY count DESC;';
  const edgeQuery =
    'MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count ORDER BY count DESC;';

  return Promise.all([
    session.executeRead((txc) => txc.run(nodeQuery)),
    session.executeRead((txc) => txc.run(edgeQuery)),
  ]).then(([nodeResult, edgeResult]) => {
    const stats = {
      nodes: nodeResult.records.reduce((acc, r) => {
        acc[r.get('label')] = toInt(r.get('count'));
        return acc;
      }, {}),
      edges: edgeResult.records.reduce((acc, r) => {
        acc[r.get('type')] = toInt(r.get('count'));
        return acc;
      }, {}),
      generatedAt: new Date(now).toISOString(),
      cacheTtlSeconds: CACHE_TTL_MS / 1000,
    };
    cache = stats;
    cacheExpiresAt = now + CACHE_TTL_MS;
    return stats;
  });
};

module.exports = {
  getStats,
};
