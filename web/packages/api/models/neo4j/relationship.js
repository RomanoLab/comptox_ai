const Node = require('./node');

const Relationship = module.exports = function(_relationship, relData) {
    const rel = _relationship['r'];

    this.fromNode = new Node(_relationship['n']);
    this.toNode = new Node(_relationship['m']);

    this.fromId = rel.start.toNumber();
    this.toId = rel.end.toNumber();

    this.relId = rel.identity.toNumber();
    this.relType = _relationship['r'].type;
};