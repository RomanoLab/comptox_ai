const neo4j = require('neo4j-driver');

const _ = require('lodash');

const Node = module.exports = function(_node, nodeData) {
    const node_features = _node.properties;
    const node_labels = _node['labels'];

    // Map identifiers
    const identifiers = Object.keys(node_features).reduce(function(xrefs, nf) {
        if (nf.startsWith("xref")) {
            if (typeof node_features[nf] === "object") {
                xrefs.push({
                    idType: nf.replace(/^(xref\.)/, ""),
                    idValue: node_features[nf].toNumber()
                });
            } else {
                xrefs.push({
                    idType: nf.replace(/^(xref\.)/, ""),
                    idValue: node_features[nf]
                });
            }
        }
        return xrefs;
    }, []);

    // Map non-identifier node features
    const features = Object.keys(node_features).reduce(function(feats, nf) {
        if (!nf.startsWith("xref") && !['commonName','uri'].includes(nf)) {
            const this_feat = node_features[nf];
            switch (typeof this_feat) {
                case "object":
                    var fv;

                    if (Array.isArray(this_feat)) {
                        // Convert each element of the list to a number
                        fv = this_feat.map(x => x.toNumber()).join('');
                    } else {
                        fv = this_feat.toNumber();
                    }

                    feats.push({
                        featType: nf,
                        featValue: fv
                    }); 
                    
                    break;
                default:
                    feats.push({
                        featType: nf,
                        featValue: node_features[nf]
                    });

                    break;
            }

        }
        return feats;
    }, []);

    this.nodeId = _node.identity.toNumber();
    this.nodeType = node_labels[0];
    this.commonName = node_features.commonName;
    this.nodeFeatures = features;
    this.identifiers = identifiers;
    this.ontologyIRI = node_features.uri;
};