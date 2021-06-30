const neo4j = require('neo4j-driver');

const _ = require('lodash');

const Path = module.exports = function(_path, pathData) {
  let nodes = [{
    id: _path.start.identity.toNumber(),
    labels: _path.start.labels,
    name: _path.start.properties.commonName
  }];
  nodes.push(_path.segments.map(seg => {
    return {
      id: seg.end.identity.toNumber(),
      labels: seg.end.labels,
      name: seg.end.commonName
    }
  }));

  const relationships = _path.segments.map(seg => {
    return {
      source: seg.relationship.start.toNumber(),
      target: seg.relationship.end.toNumber(),
      relType: seg.relationship.type,
    }
  });

  this.nodes = nodes;
  this.relationships = relationships;
};