import React from 'react';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';

class HowToUse extends React.Component {
  render() {
    return(
      <div>
        <h2>How to Use</h2>
        <Accordion>
          <AccordionSummary>
            <h3>About graph databases</h3>
          </AccordionSummary>
          <AccordionDetails>
            <p>
              ComptoxAI stores its data in a <b>graph database</b>. Each entity in the database (e.g., a chemical, disease, symptom, adverse outcome pathway, etc.) is represented as a <b>node</b>. Entities can be linked to other entities, and these links are stored in the database as <b>relationships</b>. Each relationship connects exactly two nodes, and each relationship has a direction. For example, the following relationship might exist in ComptoxAI:
            </p>
            <span>(Warfarin)-[INHIBITS]->(F2)</span>
            <p>
              In this case, the drug "Warfarin" and the gene "<i>F2</i>" are both nodes, and they are linked by the relationship "INHIBITS". In other words, the drug Warfarin inhibits the F2 protein.
            </p>
            <p>
              ComptoxAI's graph database is very large. It contains many types of nodes and many types of relationships. Furthermore, each node and relationship may contain a number of <b>properties</b> that further describe it. For example, the node representing warfarin may have the property "molar mass = 308.333 g/mol".
            </p>
          </AccordionDetails>
        </Accordion>
        <Accordion>
          <AccordionSummary>
            <h3>Types of search queries</h3>
          </AccordionSummary>
          <AccordionDetails>
            <h4>Node search</h4>
            <p>
              Search for a single node based on a node property. You can filter by node type (gene, disease, chemical, etc.), which accordingly will restrict the types of node properties you can apply the search to.
            </p>
            <h4>Relationship search</h4>
            <p>
              Search for a single relationship based on a specified relationship type. You can filter on start node and end node properties.
            </p>
            <h4>Path search</h4>
            <p>
              Find two nodes, and search for the shortest paths that link those two nodes. In this case, a <b>path</b> is a sequence of two or more nodes that are linked in sequence by a series of relationships. A path of length 2 is equal to a relationship directly linking the two nodes.
            </p>
            <h4>Batch query</h4>
            <p>
              Batch query is a more advanced feature that allows users to specify a list of node identifiers and retrieve properties for all of the nodes that those identifiers match to.
            </p>
          </AccordionDetails>
        </Accordion>
      </div>
    );
  }
}

export default HowToUse;
