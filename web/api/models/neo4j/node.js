const _ = require('lodash');

const Node = module.exports = function(_node, nodeData) {
    _.extend(this, _node.properties);

    this.uri = _node['n'].properties.uri;
    this.node_features = _node['n'].properties;
    
    this.node_labels = _node['n']['labels'];

};