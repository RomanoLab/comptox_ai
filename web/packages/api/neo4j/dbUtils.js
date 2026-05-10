'use strict';

const neo4j = require('neo4j-driver');
const conf = require('../config');

const url = conf.get('COMPTOX_AI_DATABASE_URL') || 'bolt://localhost:7687';
const user = conf.get('COMPTOX_AI_DATABASE_USER') || '';
const password = conf.get('COMPTOX_AI_DATABASE_PASSWORD') || '';

// Memgraph Community has no auth by default; the driver still requires an
// auth token, so we pass empty credentials, which Memgraph accepts.
const driver = neo4j.driver(url, neo4j.auth.basic(user, password));

exports.driver = driver;

exports.getSession = function getSession(context) {
  if (context.neo4jSession) {
    return context.neo4jSession;
  }
  context.neo4jSession = driver.session({
    defaultAccessMode: neo4j.session.READ,
  });
  return context.neo4jSession;
};

exports.closeDriver = async function closeDriver() {
  await driver.close();
};

exports.verifyConnectivity = async function verifyConnectivity() {
  await driver.verifyConnectivity();
};
