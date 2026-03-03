# ComptoxAI - A platform for knowledge-driven AI research in computational toxicology
ComptoxAI is a suite of tools for performing computational toxicology research that sits on top of a large multimodal knowledge graph (also called ComptoxAI) containing environmental toxicants, components of the human body, interactions, entities related to Adverse Outcome Pathways (AOPs) and others that describe the complex network of effects following human exposure to toxicants.

## Structure of ComptoxAI
ComptoxAI is a "monorepo" containing several different components that are capable of functioning on their own:
- 


## Coding conventions
- Avoid creation of new markdown documents or other non-code files unless they are explicitly part of ComptoxAI's documentation.
- Prefer Memgraph for graph databases, Python for data science and machine learning (PyG for graph neural networks), and Javascript/Node for all website components and the REST API.