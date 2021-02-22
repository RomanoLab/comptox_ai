const _ = require('lodash');

const NodeType = module.exports = function(_node, label) {
    _.extend(this, _node.properties);

    const raw_label = _node['label'];

    this.label = _.last(raw_label.split("__"));
    if (raw_label.split("__").length > 1){
        this.namespace = _.first(raw_label.split("__"));
    } else {
        this.namespace = null;
    }
};
