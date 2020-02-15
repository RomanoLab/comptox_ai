"""
Overview of the installation and build processes
************************************************

ComptoxAI consists of several main components:

#. The Python ``comptox_ai`` package, which includes:

   #. A connection to the graph database
   #. A library of graph machine learning models
   #. This documentation

#. ComptoxAI's graph database (implemented in Neo4j) 
#. The ComptoxAI OWL ontology (developed in Protégé and populated using ``owlready2``) #. The ComptoxAI website

When you install the Python package, the other components are (currently) not
automatically built and installed simultaneously, although complete automation
of the build is intended for a future release.

Installing prerequisites
************************

Python prerequisites
--------------------

ComptoxAI is only compatible with Python 3. If you'd still like to use Python 2
for other applications, there are several good solutions for maintaining
multiple Python installations on a single system. We recommend using either
`Anaconda <https://anaconda.org/>`_ or `pyenv <https://github.com/pyenv/pyenv>`_ if
this applies to you.

=============  ==============  ==========
Prerequisite   Version         Notes
=============  ==============  ==========
Python         >= 3.7.0        Currently untested on Python 3 versions < 3.7
=============  ==============  ==========

All Python package dependencies should be automatically installed when you run
the ``pip install`` command. If - for some reason - this fails to happen, you
can manually the dependencies using the ``requirements.txt`` file in the base
directory of the code repository::

  $ pip install -r requirements.txt    

Ontology prerequisites
----------------------

*tl,dr; Most users don't need to install anything new.*

=============  ==============  ==========
Prerequisite   Version         Notes
=============  ==============  ==========
Protégé        5.5.0           *optional*
=============  ==============  ==========

The base ontology (i.e., not populated with individuals) is included as part of
the Python package's source distribution, and named ``comptox.rdf``. This file
was created manually using the Protégé ontology editor (v5.5.0). The OWL/RDF
file can be opened and modified in any modern OWL ontology editor, although we
prefer Protégé, but doing so may cause errors later in the build process.

During the build process, we use ``owlready2`` to handle all Python interactions
with the base ontology. ``owlready2`` is included as a prerequisite in the
``requirements.txt`` file, so it should be installed for all users who have
followed the standard installation instructions.

Graph database prerequisites
----------------------------

.. note::

    In the near future, we will be making a public (read-only) instance of
    the graph database available online for remote use; until that time,
    users will need to install the database locally in order to use most
    of the components of ComptoxAI.

=============  ==============  ==========
Prerequisite   Version         Notes
=============  ==============  ==========
Neo4j          at least 3.5.6  *version >= 4.0.0 not yet tested*
=============  ==============  ==========

ComptoxAI's graph database is implemented using the Neo4j graph database
management system, which is currently the leading graph database software for
both academic and commercial applications. 

.. note::

    Depending on your local operating system, hardware, and level of skill
    administrating client/server applications you may opt to use different Neo4j
    implementations, but **most users should install Neo4j Desktop** due to its ease
    of use and self-contained nature.

.. seealso::

   :class:`comptox_ai.graph.Graph`

Installing the ComptoxAI Python package
***************************************

Clone the git repository to a location on your local machine and install using
``pip``::

  $ git clone https://github.com/JDRomano2/comptox_ai.git $ cd comptox_ai $ pip
  install .

Downloading source database files
*********************************

You'll need a local copy of a number of source files in order to build the graph
database from scratch. You will need to group the required files for each
database into a directory named for that database, and then group all of these
database-specific directories underneath a single parent data directory. 

For the currently supported source database versions, the directory setup should
look like this:

::

    data
    ├── comptox_ai
    │   └── comptox.rdf
    ├── ctd
    │   ├── CTD_chemicals.csv
    │   ├── CTD_chemicals_diseases.csv
    │   ├── CTD_diseases.csv
    │   └── CTD_genes.csv
    ├── drugbank
    │   └── drug_links.csv
    ├── epa
    │   ├── DSSTox_Mapping_20160701
    │   │   └── dsstox_20160701.tsv
    │   ├── Dsstox_CAS_number_name.xlsx
    │   └── PubChem_DTXSID_mapping_file.txt
    └── hetionet
        ├── hetionet-v1.0-edges.sif
        └── hetionet-v1.0-nodes.tsv

.. seealso::

   :ref:`guide_databases`


Running the build script
************************

The script used to populate the ontology and build the graph database is
currently found at ``comptox_ai/scripts/build/build_all.py``. It can be run like
any typical Python script::

  $ python ./build_all.py

Testing the build
*****************

The unit tests included in the ``tests/`` directory (relative to the source
code's root) cover not only the Python package, but also the graph database and
ontology. These tests are run using ``pytest``, which is included in the Python
package's prerequisites (and therefore is likely already installed).

To perform the tests, simply navigate to the package root and run::

  $ pytest tests/

The tests will fail if you don't have a currently-running instance of the Neo4j
graph database and/or a properly specified ``config.cfg`` file.

"""