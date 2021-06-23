const neo4j = require('neo4j-driver');
const _ = require('lodash');

const Node = require('./node');

const Relationship = module.exports = function(_relationship, relData) {
  console.log(_relationship.r);

  const rel = _relationship['r'];
  
  this.fromNode = new Node(_relationship['n']);
  this.toNode = new Node(_relationship['m']);
  
  this.fromId = rel.start.toNumber();
  this.toId = rel.end.toNumber();

  this.relId = rel.identity.toNumber();
  this.relType = _relationship['r'].type;
};