require('dotenv').config();

const nconf = require('nconf');

nconf
  .env([
    'PORT',
    'NODE_ENV',
    'COMPTOX_AI_DATABASE_URL',
    'COMPTOX_AI_DATABASE_USER',
    'COMPTOX_AI_DATABASE_PASSWORD',
    'API_PUBLIC_URL',
  ])
  .argv({
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
      default: 3001,
    },
  })
  .defaults({
    COMPTOX_AI_DATABASE_URL: 'bolt://localhost:7687',
    COMPTOX_AI_DATABASE_USER: '',
    COMPTOX_AI_DATABASE_PASSWORD: '',
    base_url: 'http://0.0.0.0:3001',
    api_path: '/api',
  });

module.exports = nconf;
