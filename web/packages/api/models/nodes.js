const _ = require('lodash');
const Node = require('./neo4j/node');

// Memgraph node-type-properties uses an unquoted ":Label" string for nodeType,
// without the backticks Neo4j 4.x emits.
const NODE_TYPE_LABEL_REGEX = /^[A-Za-z_][A-Za-z0-9_]*$/;

function parseNodes(neo4jResult) {
  return neo4jResult.records.map((r) => new Node(r.toObject()['n']));
}

const listNodeTypes = function listNodeTypes(session) {
  // Portable across Memgraph and Neo4j. Memgraph has no built-in
  // mg.labels() proc; the canonical scan is acceptable here because this
  // endpoint is metadata-only and called infrequently.
  const query = 'MATCH (n) UNWIND labels(n) AS label RETURN DISTINCT label ORDER BY label;';
  return session
    .executeRead((txc) => txc.run(query))
    .then((r) => r.records.map((rec) => rec.get('label')));
};

function makePropertiesList(records) {
  return records.map((rec) => ({
    property: rec.get('property'),
    type: rec.get('type'),
  }));
}

const listNodeTypeProperties = function listNodeTypeProperties(session, nodeTypeLabel) {
  if (!NODE_TYPE_LABEL_REGEX.test(nodeTypeLabel || '')) {
    return Promise.reject({ message: 'Invalid node type label', status: 400 });
  }
  // schema.node_type_properties() in Memgraph returns nodeType as ":Label"
  // (or ":A:B" for multi-label nodes) and propertyTypes as a single STRING.
  // We strip backticks and split on ":" so we tolerate the various Neo4j /
  // Memgraph nodeType formats, and pass propertyTypes through as-is.
  const query = [
    'CALL schema.node_type_properties() YIELD nodeType, propertyName, propertyTypes',
    "WITH split(replace(nodeType, '`', ''), ':') AS parts, propertyName, propertyTypes",
    'WHERE $nodeTypeLabel IN parts',
    'RETURN $nodeTypeLabel AS label,',
    '       propertyName AS property,',
    '       propertyTypes AS type',
    'ORDER BY property',
  ].join('\n');

  return session
    .executeRead((txc) => txc.run(query, { nodeTypeLabel }))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        throw { message: 'Node label not found in database', status: 404 };
      }
      return makePropertiesList(result.records);
    });
};

function ensureSafeIdentifier(name) {
  if (!NODE_TYPE_LABEL_REGEX.test(name || '')) {
    throw { message: `Invalid identifier: ${name}`, status: 400 };
  }
}

const findNodeCaseInsensitive = function findNodeCaseInsensitive(session, type, field, value) {
  ensureSafeIdentifier(type);
  ensureSafeIdentifier(field);

  const intValue = parseInt(value, 10);
  const isInt = !Number.isNaN(intValue) && String(intValue) === String(value).trim();

  const query = isInt
    ? `MATCH (n:${type}) WHERE n.${field} = $value RETURN n, id(n);`
    : `MATCH (n:${type}) WHERE toLower(toString(n.${field})) = toLower($value) RETURN n, id(n);`;

  return session
    .executeRead((txc) => txc.run(query, { value: isInt ? intValue : value }))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        throw { message: 'No results found for user query', query, status: 404 };
      }
      return parseNodes(result);
    });
};

const findNodeByQuery = function findNodeByQuery(session, type, field, value) {
  ensureSafeIdentifier(type);
  ensureSafeIdentifier(field);

  const intValue = parseInt(value, 10);
  const safeCastValue = Number.isNaN(intValue) ? value : intValue;

  const query = `MATCH (n:${type}) WHERE n.${field} = $value RETURN n, id(n);`;

  return session
    .executeRead((txc) => txc.run(query, { value: safeCastValue }))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        throw { message: 'No results found for user query', query, status: 404 };
      }
      return parseNodes(result);
    });
};

const findNodeByQueryContains = function findNodeByQueryContains(session, type, field, value) {
  ensureSafeIdentifier(type);
  ensureSafeIdentifier(field);

  const intValue = parseInt(value, 10);
  const isInt = !Number.isNaN(intValue) && String(intValue) === String(value).trim();

  const query = isInt
    ? `MATCH (n:${type}) WHERE n.${field} = $value RETURN n, id(n);`
    : `MATCH (n:${type}) WHERE toLower(toString(n.${field})) CONTAINS toLower($value) RETURN n, id(n);`;

  return session
    .executeRead((txc) => txc.run(query, { value: isInt ? intValue : value }))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        throw { message: 'No results found for user query', query, status: 404 };
      }
      return parseNodes(result);
    });
};

const fetchById = function fetchById(session, id) {
  const numericId = Number.parseInt(id, 10);
  if (!Number.isFinite(numericId) || numericId < 0) {
    return Promise.reject({ message: 'id must be a non-negative integer', status: 400 });
  }

  const query = 'MATCH (n) WHERE id(n) = $id RETURN n;';

  return session
    .executeRead((txc) => txc.run(query, { id: numericId }))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        throw { message: `No nodes found for id ${id}`, query, status: 404 };
      }
      return parseNodes(result);
    });
};

const fetchChemicalByDtsxid = function fetchChemicalByDtsxid(session, id) {
  const query = 'MATCH (n:Chemical {xrefDTXSID: $id}) RETURN n;';

  return session
    .executeRead((txc) => txc.run(query, { id }))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        throw { message: `No nodes found for DSSTox ID ${id}`, query, status: 404 };
      }
      return parseNodes(result);
    });
};

module.exports = {
  listNodeTypes,
  listNodeTypeProperties,
  findNodeCaseInsensitive,
  findNodeByQuery,
  findNodeByQueryContains,
  fetchById,
  fetchChemicalByDtsxid,
};
