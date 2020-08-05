.. _install:

=======================
Installing and Building
=======================

This guide is meant to get new users up and running with a complete
installation of ComptoxAI, including the Python package and the graph database
populated from the original data sources.

Users also have the option to install a "slimmed down" version of ComptoxAI
without the graph database. It's important to keep in mind, however, that many
features won't be available without the database installed and running. A
future release will include the option to connect to a remote version of the
database; we will update this guide accordingly when this is implemented.

.. important::

   The examples on this page are roughly compatible with most modern UNIX (or UNIX-like) command line applications. If you are installing ComptoxAI on Windows (or something else), you should modify the examples accordingly.

Installing the ``comptox_ai`` Python package
--------------------------------------------

For now, the easiest way to install the ``comptox_ai`` package is by cloning
the repository from GitHub and running the ``setup.py`` script from the
repository's root directory::

   $ git clone https://github.com/JDRomano2/comptox_ai
   $ cd comptox_ai
   $ python setup.py

Rather than running the ``setup.py`` script directly, you can also install
using ``pip``::

   $ git clone https://github.com/JDRomano2/comptox_ai
   $ cd comptox_ai
   $ pip install .

If you run into errors with package dependencies, you can force ``pip`` to install the prerequisites by navigating to the repository's root and running::

   $ pip install -r requirements.txt

Downloading the source data files
---------------------------------

All of the data in ComptoxAI's graph database come from publicly-available
sources - usually domain-specific public databases released and maintained by
academic research groups or the US federal government. In order to build the
graph database locally, you will need to download the data files from their
original locations and put them in a folder where ComptoxAI's build utilities
known to look for them.

Preparing the root data directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, create a folder on your computer that will contain all of the source
data. For example, on a Unix system::

   $ cd ~
   $ mkdir -p data/comptox_ai
   $ cd data/comptox_ai

Make sure that you have read and write access to this directory!

Preparing database-specific subdirectories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a subdirectory within the new root data directory for each of the source
databases. For example::

   $ mkdir epa
   $ mkdir hetionet
   ...

ComptoxAI's build scripts will look for the source databases in directories
with the following names:

  =================================== ===================================
  Database                            Directory name (case-sensitive)
  =================================== ===================================
  Hetionet                            ``hetionet/``
  Comparative Toxicogenomics Database ``ctd/``
  EPA CompTox dashboard               ``epa/``
  DrugBank                            ``drugbank/``
  =================================== ===================================

Source Data Files
^^^^^^^^^^^^^^^^^

Place the following files into their corresponding directories. We will try to
keep the page where the files can be found up-to-date, but the source database
maintainers may change these at any time. If you notice an error, please let us
know by `filing an Issue on GitHub
<https://github.com/JDRomano2/comptox_ai/issues>`_.

+----------+----------------------------------------------------------+--------------------------------+-------+
| Database |                      Download Page                       |            Filename            | Notes |
+==========+==========================================================+================================+=======+
| Hetionet | https://github.com/hetio/hetionet/tree/master/hetnet/tsv | ``hetionet-v1.0-edges.sif.gz`` | Unzip |
|          |                                                          | ``hetionet-v1.0-nodes.tsv``    |       |
+----------+----------------------------------------------------------+--------------------------------+-------+

Setting up and preparing Neo4j
------------------------------

Install Neo4j
^^^^^^^^^^^^^

We recommend `Neo4j Desktop <https://neo4j.com/download/>`_ for most users, as
it runs with minimal headaches and is self-contained. More advanced users can
opt to download `Neo4j Community
<https://neo4j.com/download-center/#community>`_ if they like the extra control
it provides over your server setup. We don't officially support any particular
version of Neo4j, but for reference, the database is developed and tested on
Neo4j versions 3.5.6 and greater.

When you have downloaded and installed Neo4j Desktop, create a new Project and
name it "ComptoxAI". Inside this project, choose "Add Graph", then "Create a
Local Graph". Name the graph ``ComptoxAI``, and set a password that you will
remember. We recommend that you avoid using the password ``neo4j``, because
some of the database browser applications bundled with Neo4j Desktop have a
tendancy to complain when you do so (the application tries to enforce some
degree of security). Choose "Create", and then click the "Start" button once
the graph has finished being created. After a few moments, you will see the
status indicator for the graph turn from yellow to green, and it will say
"Active". You now have an empty graph database to use!

Install Neo4j plugins
^^^^^^^^^^^^^^^^^^^^^

You need the following 3 plugins:

- APOC
- Graph Algorithms
- neosemantics (n10s)

APOC and Graph Algorithms are easily installed from Neo4j Desktop by going to
its main screen, clicking on the ComptoxAI project, and then clicking "Add Plugin". Both plugins should be listed and available to install.

Neosemantics needs to be installed manually. You can find instructions for how to do so at `<https://neo4j.com/docs/labs/nsmntx/current/install/>`_, but note
that they don't provide detailed steps for users with Neo4j Desktop. To get it
working on our desktop, we did roughly the following:

#. Download the most recent ``.jar`` file from the `Github Releases page
   <https://github.com/neo4j-labs/neosemantics/releases>`_. Make sure that the
   version you download is compatible with the version of Neo4j you chose when
   you created the ComptoxAI graph.
#. In Neo4j Desktop, click "Manage" in the graph status panel. Next to
   "Open Folder", click the down arrow, and then "Plugins".
#. Move the neosemantics ``.jar`` file to the plugins folder.
#. Back in Neo4j Desktop, click the "Settings" tab, and add a line to the bottom containing the following::
   ``dbms.unmanaged_extension_classes=semantics.extension=/rdf``
#. Go back to the Project page and restart the server.
#. Create an index/constraint on ``Resource`` nodes by, e.g., running:
   ``CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE``

Building the database and populating Neo4j
------------------------------------------

Build the graph database and store as RDF
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the root directory of ComptoxAI, navigate to ``comptox_ai/build/`` and
run ``python build_all.py``. From the application's main menu, choose the
option to ``Build ontology``. This will take a long time to complete!

Once that has finished, select the option to ``Save ontology to disk``. After
this has completed, you can press ``q`` or ``Q`` to quit the application.

Import the RDF file into Neo4j using neosemantics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. important::
   
   While importing the data, you may encounter errors related to null values
   (represented as the string ``None`` in the RDF file). The best way to handle
   these are by simply filtering out all lines in the file that contain the
   string ``None``, e.g., by running ``sed``:
   ``sed '/None/d' COMPTOX_FULL.rdf > COMPTOX_FULL_TRIMMED.rdf``

Since neosemantics is under active development, the correct syntax for 
importing the RDF file into Neo4j changes fairly frequently. Refer to its
documentation for up-to-date info for the version of neosemantics you 
installed. At the time of writing this, the instructions are given at
`<https://github.com/neo4j-labs/neosemantics#2--importing-rdf-data>`_.

.. note::

   Make sure to use the correct function calls for importing RDF data (NOT
   ontology data, as this will only import the class hierarchy).

.. note::

   Neosemantics has somewhat fragmented documentation, particularly for Windows
   users. To specify a local RDF file on Windows within a neosemantics import
   command, the path should look something like:
   ``'file:///D:\\Data\\comptox_ai\\comptox_full.rdf'``

Testing ComptoxAI
-----------------

ComptoxAI's complete test suite is still under development. Prior to releasing
v1.0 we will write a full suite of tests, and this guide will be updated
accordingly.