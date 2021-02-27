const _ = require('lodash');

const Node = module.exports = function(_node, nodeData) {
    _.extend(this, _node.properties);

    console.log(_node['n'].properties);
};