.. _about:

About ComptoxAI
===============

ComptoxAI is a toolkit designed to enable AI and data science research in
computational toxicology.

Like many areas in biomedicine, environmental toxicology is facing a deluge of
valuable data being generated in a wide array of modalities and levels of
biological organization. However, the tools for interacting with these data are
- at best - inconsistent, outdated, and fail to use state-of-the-art
computational methods.

See also:

- :ref:`User Guide <user_guide>` - An introduction to ComptoxAI and its features
- :ref:`API Documentation <docs>` - Developer reference for ComptoxAI's Python library

.. _authors:

Authors
-------

ComptoxAI is developed and maintained by `Joseph D. Romano <https://jdr.bio>`_,
who is a postdoctoral researcher at the University of Pennsylvania. Yun Hao, a
PhD student at the University of Pennsylvania, provides assistance with data
preprocessing/curation and analysis.

Other important contributors include:

- `Jason Moore
  <http://epistasis.org/jason-h-moore-phd/>`_ (Cedars-Sinai)
- `Trevor Penning
  <https://www.med.upenn.edu/apps/faculty/index.php/g275/p12620>`_ (Penn)
- Holly Mortensen (US EPA)
- Jonathan Senn (formerly US EPA)
- Mei Liang (US EPA)

.. _citing:

Citing ComptoxAI
----------------

We are preparing two papers for publication which, together, will comprehensively
describe ComptoxAI and its current features. Until those are released, please
cite us using the following:

| Romano *et al*. (2022) ComptoxAI: A toolkit for AI research in computational toxicology. `<https://comptox.ai>`_.

BibTeX entry::

  @misc{comptoxai,
    title = "ComptoxAI: A toolkit for AI research in computational toxicology",
    author = "Joseph~D.~Romano",
    howpublished = "\url{https://comptox.ai}",
    year = 2021
  }

Other Publications
^^^^^^^^^^^^^^^^^^

* Romano JD, Hao Y, & Moore JH. (2022) Improving QSAR Modeling for Predictive Toxicology using Publicly Aggregated Semantic Graph Data and Graph Neural Networks. *Pacific Symposium on Biocomputing 27*: 187-198.

::

  @inproceedings{romano2021improving,
    title={Improving QSAR Modeling for Predictive Toxicology using Publicly Aggregated Semantic Graph Data and Graph Neural Networks},
    author={Romano, Joseph D and Hao, Yun and Moore, Jason H},
    booktitle={PACIFIC SYMPOSIUM ON BIOCOMPUTING 2022},
    pages={187--198},
    year={2021},
    organization={World Scientific}
  }

.. _source_dbs:

Source databases
----------------

ComptoxAI consists of data integrated from a wide range of third-party, open
access databases (many of which are relational databases rather than graph
databases). These include:

- `AOP-DB <https://aopdb.epa.gov/home>`_
- AOP-Wiki
- Drugbank
- DSSTox
- Hetionet
- NCBI Gene
- NCBI OMIM
- PubChem
- Reactome
- Tox21

See :ref:`guide_databases` for complete details on each of these.

.. _contact_us:

Contact Us
----------

This wesite is maintained by Joseph D. Romano, PhD. He can be reached via email
at:: 

   joseph.romano [at] pennmedicine.upenn.edu

Similar projects can be found at `his personal website
<http://jdr.bio>`_, or at the `Artificial Intelligence Innovation Lab's home
page <http://epistasis.org>`_.

.. _contributing:

Contributing
------------

If you believe you've found a bug, would like to request a new feature, or are
interested in contributing to the continued development of ComptoxAI, please
see `CONTRIBUTING.md
<https://github.com/jdromano2/comptox_ai/blob/master/CONTRIBUTING.md>`_ on
GitHub.

.. _funding:

Funding and Acknowledgements
----------------------------

ComptoxAI is supported by grant funding from the US National Institutes of
Health, including: 

- `K99-LM013646 <https://reporter.nih.gov/project-details/10371656>`_ (PI: Romano)
- `R01-LM010098 <https://reporter.nih.gov/project-details/10126058>`_ (PI: Moore)
- `R01-LM012601 <https://reporter.nih.gov/project-details/9999032>`_ (PI: Moore)
- `P30-ES013508 <https://reporter.nih.gov/project-details/10437460>`_ (PI: Penning)
- `T32-ES019851 <https://reporter.nih.gov/project-details/10176487>`_ (PI: Penning)

ComptoxAI would also not be possible without essential contributions from
researchers at the US Environmental Protection Agency (EPA), including Dr.
Holly Mortensen, Jonathan Senn, and Mei Liang, who have contributed essential
data from the `AOP-DB project
<https://www.nature.com/articles/s41597-021-00962-3>`_. We also would like to
acknowledge Daniel Himmelstein's `hetionet <https://het.io>`_ resource, which is
used to derive many of the graph relationships between different classes of
biological entities.
