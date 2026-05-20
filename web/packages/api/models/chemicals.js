const { execSync } = require("node:child_process");
const { appendFileSync } = require('fs');
const tmp = require('tmp');
const { parseString } = require('xml2js');

const _ = require('lodash');
const Node = require('./neo4j/node');

function parseNodes(neo4jResult) {
  return neo4jResult.records.map((r) => new Node(r.toObject()['n']));
}

const DTSXID_PATTERN = /^DTXSID[0-9]+$/;

const PAGINATION_MAX = 1000;

function normalizePagination({ limit, offset }) {
  const parsedLimit = parseInt(limit, 10);
  const parsedOffset = parseInt(offset, 10);
  const safeLimit = Math.min(
    Math.max(Number.isFinite(parsedLimit) ? parsedLimit : 100, 1),
    PAGINATION_MAX
  );
  const safeOffset = Math.max(Number.isFinite(parsedOffset) ? parsedOffset : 0, 0);
  return { safeLimit, safeOffset };
}

let parseCmlData = function (cmlData) {
    const molecules = cmlData.cml.molecule.map(m => {
        const mol_props = m.propertyList[0].property.reduce((propObj, item) => {
            let propTitle = item['$'].title;
            let propValue = item.scalar[0];
            return {...propObj, [propTitle]: propValue};
        }, {});
        return mol_props;
    })
    return molecules;
}

const runStructureSearch = function (req) {
    return new Promise(function(resolve, reject) {
        // Save mol file payload as temporary file
        const tmpobj = tmp.fileSync({ postfix: '.mol' });
        appendFileSync(tmpobj.fd, req.body);

        // Call jcsearch using the temp file
        const cml_data_raw = execSync(
            `jcsearch -q ${tmpobj.name} -f cml -t:i DB:public.chemicals`,
            {
                maxBuffer: (1024*1024*24)
            }
        ).toString();

        var cml_obj;
        parseString(cml_data_raw, function (err, result) {
            cml_obj = result;
        });

        const mols = parseCmlData(cml_obj);
        resolve(mols);
    });
}

const fetchByCas = function fetchByCas(session, cas) {
  if (!cas || typeof cas !== 'string') {
    return Promise.reject({ message: 'cas must be a non-empty string', status: 400 });
  }
  const query = 'MATCH (n:Chemical {xrefCasRN: $cas}) RETURN n;';
  return session
    .executeRead((txc) => txc.run(query, { cas }))
    .then((result) => {
      if (_.isEmpty(result.records)) {
        throw {
          message: `No chemical found for CAS Registry Number ${cas}`,
          query,
          status: 404,
        };
      }
      return parseNodes(result);
    });
};

const findGenesForChemical = function findGenesForChemical(session, dtsxid, options = {}) {
  if (!DTSXID_PATTERN.test(dtsxid || '')) {
    return Promise.reject({
      message: 'dtsxid must look like "DTXSID" followed by digits',
      status: 400,
    });
  }
  const { safeLimit, safeOffset } = normalizePagination(options);

  let relPattern;
  switch (String(options.direction || 'both').toLowerCase()) {
    case 'increases':
      relPattern = ':chemicalIncreasesExpression';
      break;
    case 'decreases':
      relPattern = ':chemicalDecreasesExpression';
      break;
    case 'both':
    case '':
    case undefined:
      relPattern = ':chemicalIncreasesExpression|chemicalDecreasesExpression';
      break;
    default:
      return Promise.reject({
        message: 'direction must be one of: increases, decreases, both',
        status: 400,
      });
  }

  // SKIP/LIMIT are interpolated as numeric literals (safe after normalisation
  // above) because Memgraph's planner rejects bound parameters in those slots
  // in some 2.x point releases.
  const query = `
    MATCH (c:Chemical {xrefDTXSID: $dtsxid})-[r${relPattern}]-(n:Gene)
    WITH n, collect(DISTINCT type(r)) AS relTypes
    ORDER BY n.geneSymbol
    SKIP ${safeOffset} LIMIT ${safeLimit}
    RETURN n, relTypes;
  `;

  return session
    .executeRead((txc) => txc.run(query, { dtsxid }))
    .then((result) =>
      result.records.map((rec) => {
        const node = new Node(rec.toObject()['n']);
        node.relationshipTypes = rec.get('relTypes');
        return node;
      })
    );
};

const findAopsForChemical = function findAopsForChemical(session, dtsxid, options = {}) {
  if (!DTSXID_PATTERN.test(dtsxid || '')) {
    return Promise.reject({
      message: 'dtsxid must look like "DTXSID" followed by digits',
      status: 400,
    });
  }
  const { safeLimit, safeOffset } = normalizePagination(options);

  const query = `
    MATCH (c:Chemical {xrefDTXSID: $dtsxid})-[:keyEventTriggeredBy]-(ke:KeyEvent)
          -[:aopIncludesKE|keIncludedInAOP]-(n:AOP)
    WITH DISTINCT n
    ORDER BY n.commonName
    SKIP ${safeOffset} LIMIT ${safeLimit}
    RETURN n;
  `;

  return session
    .executeRead((txc) => txc.run(query, { dtsxid }))
    .then((result) => parseNodes(result));
};

module.exports = {
  runStructureSearch,
  fetchByCas,
  findGenesForChemical,
  findAopsForChemical,
};
