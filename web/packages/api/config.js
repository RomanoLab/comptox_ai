require('dotenv').config();

const nconf = require('nconf');

nconf.env(['PORT', 'NODE_ENV']).argv({
  e: {
    alias: 'NODE_ENV',
    describe: 'Specify development or production mode for running app.',
    demand: false,
    default: 'development',
  },
  p: {
    alias: 'PORT',
    describe: 'Port used to serve API application.',
    demand: false,
    default: 3000,
  },
  n: {
    alias: 'neo4j',
    describe: 'Specify whether to use remote or local Neo4j instance.',
    demand: false,
    default: 'local',
  },
}).defaults({
  USERNAME: process.env.COMPTOX_AI_DATABASE_USERNAME,
  PASSWORD: process.env.COMPTOX_AI_DATABASE_PASSWORD,
  neo4j: 'local',
  'neo4j-local': process.env.COMPTOX_AI_DATABASE_URL || 'bolt://54.147.33.120:7687',
  base_url: 'http://0.0.0.0:3000',
  api_path: '/api',
});

module.exports = nconf;
