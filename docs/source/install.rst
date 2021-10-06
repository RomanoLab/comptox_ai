.. _install:

#######################
Installing and Building
#######################

ComptoxAI is a complete data ecosystem for AI research in computational
toxicology, meaning it consists of a number of different tools that work
together to accomplish various goals. This installation guide is meant to teach
you how to get each of those tools/components up and running from scratch.

We've also prepared a brief guide on what to install based on the task you're 
trying to accomplish:

*****************************************
What parts of ComptoxAI should I install?
*****************************************

"I just want to explore the data and/or the graph database"
===========================================================

Good news - you don't need to install anything! Most likely, this website has 
everything you need already on it. For examples of ways to browse the database,
please refer to `Browse Data <browse.html>`_.

"I need to run some Cypher queries on the graph database"
=========================================================

Like above, you probably don't need to install anything. The `Neo4j database
browser <https://neo4j.comptox.ai>`_ lets you explore a full copy of the graph
database and run Cypher queries right from your web browser.

"I want to perform machine learning using data from ComptoxAI"
==============================================================

In this case, it depends. If you want to export one (or a few) subgraphs from
the graph database and train some traditional- or graph-ML models, you may have
an easier time just using the `bulk dataset generator <data.html>`_. However,
if you need to run many dataset queries it might be better to do it using a
local copy of the graph database and the Python package for actually extracting
the datasets. In this case you should install **the Python package** and the
full **Neo4j graph database**.

.. important::

   The examples on this page are roughly compatible with most modern UNIX (or UNIX-like) command line applications. If you are installing ComptoxAI on Windows (or something else), you should modify the examples accordingly.

********************************************
Installing the ``comptox_ai`` Python package
********************************************

The most reliable method for installing the ComptoxAI python package currently
is using a combination of ``conda`` and setuptools.

If you don't already have Anaconda or Miniconda installed, you can do so by
selecting the appropriate installer file `here <https://docs.conda.io/en/latest/miniconda.html>`_. We recommend a 64-bit version of Miniconda 3.

Then, you can create a new ``conda`` environment that will be used for 
ComptoxAI::

   $ conda create -n comptox_ai python=3.7.5

Now, we can install PyTorch and PyTorch Geometric using ``conda``::

   $ conda activate comptox_ai
   $ conda install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch
   $ conda install pytorch-geometric -c rusty1s -c conda-forge

Next, clone the GitHub repository for ComptoxAI, and install the remaining
dependencies via ``setuptools``::

   $ git clone https://github.com/JDRomano2/comptox_ai.git
   $ cd comptox_ai
   $ pip install .

***********************************************************
Installing Neo4j and importing the ComptoxAI graph database
***********************************************************

Install Neo4j
=============

For most users, `Neo4j Desktop <https://neo4j.com/download/>`_ is the
preferred method of installation. Neo4j Desktop does an excellent job managing
one or more graph databases concurrently, and makes installing plugins almost
trivially easy. It also comes with a built-in developer license for Neo4j
Enterprise, which includes the excellent `Neo4j Bloom 
<https://neo4j.com/product/bloom/>`_ visualization tool. If you prefer to
install Neo4j Server (e.g., if you want to host the complete graph database on
a web server, or if you just like having full control over your data
ecosystem), it is totally possible to do so, but you may need to troubleshoot a
bit.

Any modern version of Neo4j Desktop should work fine, but we have tested it
mainly on Version 1.4.7. Download the application and install it following the
prompts; the default setting should be sufficient for most users.

Create an empty graph database
==============================

You're now ready to create an empty graph database that will hold ComptoxAI.
Make a new Project, and change the name to ComptoxAI (or whatever else you
prefer), by hovering over the "Project" label in the main window and clicking
the edit icon immediately to its right. On the right side of this window, 
click the "Add" dropdown button, and select "Local DBMS". In this form, set
Name to anything you'd like (we use "ComptoxAI DBMS"), and set the password to
something you will remember. After you install the Python package, this
password will need to go into your ``CONFIG.yaml`` file. Next, choose version
4.2.8 from the Version dropdown menu - this is the newest version of the DBMS
that is compatible with the plugins we will be using. Finally, click "Create"
to finish the process.

Install plugins and configure the database
==========================================

Click the name of the DBMS ("ComptoxAI DBMS", if you are following our lead),
but don't start the database just yet. A new panel should appear to the right.
In this panel, click the "Plugins" tab. Install the following 3 plugins by
expanding their name and clicking "Install":

- APOC
- Graph Data Science Library
- Neosemantics (n10s)

Next, open the DBMS' configuration file (hover over the DBMS name, click the
ellipses icon on the right side, and select "Settings..."), and set the
following configuration options by changing the corresponding line to match:

- ``dbms.memory.heap.initial_size=2G``
- ``dbms.memory.heap.max_size=8G``
- ``dbms.memory.pagecache.size=2G``
- ``dbms.security.procedures.unrestricted=jwt.security.*,n10s.*,apoc.*,gds.*``

Then, add a new line at the end of the file with a configuration option that 
specifies the directory to which graphs will be exported when you want to 
analyze them in 3rd party software (such as PyTorch Geometric, for example). 
This should be changed to a local directory that makes sense on your computer, 
and where you have read/write permissions:

- ``gds.export.location=/home/username/data/comptox_ai/subgraphs``

.. important::

   This is one step where Windows users need to be careful. You need to escape
   each backslash in the export path with another backslash. It might look
   something like this::
   
   gds.export.location=C:\\data\\comptox_ai\\subgraphs

Download the ontology RDF file
==============================

The full RDF representation of the graph database / ontology is very large -
currently almost 600 MB. Visit the `data browsing page
<https://comptox.ai/browse.html>`_ and click the "Download fully-populated
ontology" button to be redirected to a page where you can download the file.
Save it to a location that you'll remember in the next step.

Import the RDF data into the DBMS
=================================

We now use ``n10s`` to import the RDF file into the (currently empty) graph
database.

In Neo4j Desktop, hover over your DBMS name, and click "Start" to start the
database. When the icon next to the DBMS name turns green and reads "Active",
click the "Graph Apps" tab on the far left side of Neo4j Desktop, then select
"Neosemantics". A new window will open with the ``n10s``/Neosemantics logo.
In the "Project" dropdown, select the project you created for ComptoxAI, and
then in "Graph" select the name of the DBMS, and click "Connect". You'll be
asked if you want to run a command to create a new constraint on the graph,
which you should do.

We now set a few configuration settings in ``n10s``. Click the "Config" tab on
the left, and set the following options:

- ``handleVocabUris``: ``IGNORE``
- ``handleMultival``: ``OVERWRITE``
- ``handleRDFTypes``: ``LABELS``
- ``applyNeo4jNaming``: Click the slider to activate

Click "Create Config" to save the config options.

Now, click on the "Import" tab, and set the following options:

- RDF Source: Fetch from URL (this should be selected already)
- Input Format: ``RDF/XML``
- URL: Location of the RDF file you downloaded in the previous step - see the note below for details

.. important::

   Specifying the RDF file's location is a bit finicky. Basically, you need to
   prepend the local path with ``file:///``. So, on a Unix system, it may look
   like ``file:///home/username/data/comptox_populated.rdf``. On Windows, you
   need to escape backslashes, so it may look like ``file:///C:\\data\\comptox_populated.rdf``.

   Also, note that you currently can't just use the "Upload" option for RDF
   Source, at least not on all operating systems. In our tests, trying to
   import the RDF data this way results in the app crashing.

Finally, click "Import Data". It should take a little while to complete the
import, but a success message will eventually show up indicating the number of
nodes and relationships imported into the database.

Finish tidying up
=================

The process we use for building the database - which involves populating an
OWL2 ontology and then importing that ontology as RDF data into Neo4j - leaves
behind some extra junk that we don't need in the database. The code repository
includes a Python script that automates the process of clearing these out.

.. important::

   If you didn't increase the memory limits in your DBMS as outlined above,
   this script will probably crash. We need to remove many unnecessary node
   labels from the database, and this is a very memory-intensive operation.

Assuming you followed the instructions above for installing the ComptoxAI
Python package, navigate to the cloned source code repository's root directory,
and then run the script, e.g.::

   $ cd comptox_ai/build/
   $ python post_install.py

Since this cleaning is an irreversible process, you need to confirm that you
want to proceed.

After the script finishes running, you should be all set up and good to go!



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