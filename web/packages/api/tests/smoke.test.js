'use strict';

// Smoke tests for the ComptoxAI API.
// Requires a Memgraph instance reachable at COMPTOX_AI_DATABASE_URL
// (default bolt://localhost:7687). The DB does not need data — these tests
// only assert that the API process boots and the read paths return 2xx.

const test = require('node:test');
const assert = require('node:assert');
const request = require('supertest');

const app = require('../app');
const dbUtils = require('../neo4j/dbUtils');

test.after(async () => {
  await dbUtils.closeDriver();
});

test('GET / returns the welcome string', async () => {
  const res = await request(app).get('/');
  assert.strictEqual(res.status, 200);
  assert.match(res.text, /ComptoxAI/);
});

test('GET /health returns 200 with db: up', async () => {
  const res = await request(app).get('/health');
  assert.strictEqual(res.status, 200);
  assert.strictEqual(res.body.status, 'ok');
  assert.strictEqual(res.body.db, 'up');
});

test('GET /nodes/listNodeTypes returns an array', async () => {
  const res = await request(app).get('/nodes/listNodeTypes');
  assert.strictEqual(res.status, 200);
  assert.ok(Array.isArray(res.body));
});

test('GET /nodes/fetchById/abc returns 400 for non-numeric id', async () => {
  const res = await request(app).get('/nodes/fetchById/not-a-number');
  assert.strictEqual(res.status, 400);
});
