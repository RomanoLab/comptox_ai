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

.. _authors:

Authors
-------

ComptoxAI is developed and maintained by `Joseph D. Romano <https://jdr.bio>`_,
who is a postdoctoral researcher at the University of Pennsylvania.

Other important contributors include:

- `Jason Moore
  <https://www.med.upenn.edu/apps/faculty/index.php/g275/p8803452>`_ (Penn)
- `Trevor Penning
  <https://www.med.upenn.edu/apps/faculty/index.php/g275/p12620>`_ (Penn)
- Yun Hao (Penn)
- Holly Mortensen (US EPA)
- Jonathan Senn (US EPA)
- Mei Liang (US EPA)

.. _citing:

Citing ComptoxAI
----------------

ComptoxAI is still under development, but we would still appreciate citations
of the following form until we have our first preprints/papers published:

| ComptoxAI: A toolkit for AI research in computational toxicology, Romano *et al*, `<https://comptox.ai>`_, 2021

BibTeX entry::

  @misc{comptoxai,
    title = "ComptoxAI: A toolkit for AI research in computational toxicology",
    author = "Joseph~D.~Romano",
    howpublished = "\url{https://comptox.ai}",
    year = 2021
  }

.. _source_dbs:

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
<http://jdr.bio>`_, or at the University of Pennsylvania's `Computational
Genetics Lab home page <http://epistasis.org>`_.

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
- `T32-ES019851 <https://reporter.nih.gov/project-details/10176487>`_ (PI: Penning)

ComptoxAI would also not be possible without essential contributions from
researchers at the US Environmental Protection Agency (EPA), including Dr.
Holly Mortensen, Jonathan Senn, and Mei Liang, who have contributed essential
data from the `AOP-DB project
<https://www.nature.com/articles/s41597-021-00962-3>`_. We also would like to
acknowledge Daniel Himmelstein's `hetionet <https://het.io>`_ resource, which is
used to derive many of the graph relationships between different classes of
biological entities.
