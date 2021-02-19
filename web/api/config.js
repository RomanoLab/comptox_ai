'use strict';

require('dotenv').config();

var nconf = require('nconf');

nconf.env(['PORT', 'NODE_ENV']).argv({
    'e': {
        alias: 'NODE_ENV',
        describe: 'Specify development or production mode for running app.',
        demand: false,
        default: 'development',
    },
    'p': {
        alias: 'PORT',
        describe: 'Port used to serve API application.',
        demand: false,
        default: 3000,
    },
    'n': {
        alias: 'neo4j',
        describe: 'Specify whether to use remote or local Neo4j instance.',
        demand: false,
        default: 'local'
    }
}).defaults({
    'USERNAME': process.env.COMPTOX_AI_DATABASE_USERNAME,
    'PASSWORD': process.env.COMPTOX_AI_DATABASE_PASSWORD,
    'neo4j': 'local',
    'neo4j-local': process.env.COMPTOX_AI_DATABASE_URL || 'bolt://localhost:7867',
    'base_url': 'http://localhost:3000',
    'api_path': '/api/v0',
});

module.exports = nconf;
