const _ = require('lodash');

const RelationshipType = module.exports = function(_rel, label) {
    _.extend(this, _rel.properties);

    const raw_label = _rel['relationshipType'];

    this.label = _.last(raw_label.split("__"));
    if (raw_label.split("__").length > 1) {
        this.namespace = _.first(raw_label.split("__"));
    } else {
        this.namespace = null;
    }
};
