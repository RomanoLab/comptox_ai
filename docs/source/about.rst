.. _about:

About ComptoxAI
===============

ComptoxAI is a toolkit designed to enable AI and data science research in
computational toxicology. Like many areas in biomedicine, environmental
toxicology is facing a deluge of valuable data being generated in a wide array
of modalities and levels of biological organization. However, the tools for
interacting with these data are - at best - inconsistent, outdated, and fail to
leverage state-of-the-art computational methods.

We're creating ComptoxAI in order to change this.

Authors
-------

ComptoxAI is developed and maintained by `Joseph D. Romano <https://jdr.bio>`_, who is a
postdoctoral researcher at the University of Pennsylvania in the Computational
Genetics Lab.

Other important contributors include:

- `Jason Moore <https://www.med.upenn.edu/apps/faculty/index.php/g275/p8803452>`_ (Penn)
- `Trevor Penning <https://www.med.upenn.edu/apps/faculty/index.php/g275/p12620>`_ (Penn)
- Yun Hao (Penn)
- Holly Mortensen (US EPA)
- Jonathan Senn (US EPA)
- Mei Liang (US EPA)

Citing ComptoxAI
----------------

ComptoxAI is still under development, but we will update this page with a
preprint citation when we have one written. In the meantime, please contact us
if you would like to use ComptoxAI for research purposes (you don't need our
permission, we'd just like to make sure you're aware of which work is evaluated
and which isn't at this point)!

Source databases
----------------

ComptoxAI consists of data integrated from a wide range of third-party, open
access databases (many of which are relational databases rather than graph
databases). These include:

- AOP-DB
- AOP-Wiki
- Drugbank
- DSSTox
- Hetionet
- NCBI Gene
- NCBI OMIM
- PubChem
- Tox21

See :ref:`guide_databases` for complete details on each of these.

Contact Us
----------

This wesite is maintained by Joseph D. Romano, PhD. He can be reached via email
at **joseph.romano [at] pennmedicine.upenn.edu**.

If you believe you've found a bug, would like to request a new feature, or are
interested in contributing to the continued development of ComptoxAI, please
see `CONTRIBUTING.md
<https://github.com/jdromano2/comptox_ai/blob/master/CONTRIBUTING.md>`_ on
GitHub.

Similar projects can be found at `his personal website
<http://jdr.bio>`_, or at the University of Pennsylvania's `Computational
Genetics Lab home page <http://epistasis.org>`_.

Funding and Acknowledgements
----------------------------

ComptoxAI is supported by grant funding from the US National Institutes of
Health, including ``K99-LM013646`` (PI: Romano), ``R01-LM010098`` (PI: Moore), 
``R01-LM012601`` (PI: Moore), and ``T32-ES019851`` (PI: Penning).

ComptoxAI would also not be possible without essential contributions from
researchers at the US Environmental Protection Agency (EPA), including Dr.
Holly Mortensen, Jonathan Senn, and Mei Liang, who have contributed essential data from the `AOP-DB project <https://www.nature.com/articles/s41597-021-00962-3>`_.
We also would like to acknowledge Daniel Himmelstein's
`hetionet <https://het.io>`_ resource, which is used to derive many of the
graph relationships between different classes of biological entities.
