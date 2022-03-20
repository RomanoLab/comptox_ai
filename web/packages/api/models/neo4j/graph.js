const Node = require('./node');
const Relationship = require('./relationship');

const Graph = module.exports = function(_graph) {
    this.nodes = _graph['nodes'].map(n => new Node(n));

    this.relationships = _graph['relationships'];
}