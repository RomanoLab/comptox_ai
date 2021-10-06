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

In this case, it depends.

If you want to export one (or a few) subgraphs from
the graph database and train some traditional- or graph-ML models, you may have
an easier time just using the `bulk dataset generator <data.html>`_.

However,
if you need to run many dataset queries it might be better to do it using a
local copy of the graph database and the Python package for actually extracting
the datasets. In this case you should install **the Python package** and the
full **Neo4j graph database**.

"I want to run a few Python analyses using some of ComptoxAI's data"
====================================================================

Depending on the size of your analyses, you can probably just install **the
Python package**, and connect to the public graph database rather than hosting
an entire copy locally. If you find that analyses are slow, if bandwidth is a
concern, or you want to modify the contents of the graph database for any reason,
it is probably best to install the full **Neo4j graph database**.

"I want to create a similar data infrastructure, but for a different purpose"
=============================================================================

In this case, you should probably `fork the repository
<https://github.com/jdromano2/comptox_ai/fork>`_ and edit each of the parts to 
fit your particular needs and environment. Make sure you read `the license
<https://github.com/JDRomano2/comptox_ai/blob/master/LICENSE>`_ to know your
rights and restrictions (we use the MIT License).

.. important::

   The examples on this page are roughly compatible with most modern UNIX (or 
   UNIX-like) command line applications. If you are installing ComptoxAI on
   Windows (or something else), you should modify the examples accordingly.

********************************************
Installing the ``comptox_ai`` Python package
********************************************

We don't have ComptoxAI on the Python Package Index yet, but you can install it
directly from the source repository. We recommend using Anaconda/``conda``, but
it should also work with ``pip`` alone (you might need to tell it to install a
few dependencies).

First, clone the repository::

   $ git clone https://github.com/JDRomano2/comptox_ai
   $ cd comptox_ai

Installing prerequisites into a new ``conda`` environment::

   $ conda install -f environment.yml

Installing ``comptox_ai`` using ``pip``::

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
ecosystem), it is totally possible to do so, but we don't provide up-to-date
instructions.

Any modern version of Neo4j Desktop should work fine, but we have tested it
mainly on Version 1.4.7. Download the application and install it following the
prompts; the default settings should be sufficient for most users.

Create an empty graph database
==============================

You're now ready to create an empty graph database that will hold ComptoxAI.
Make a new Project, and change the name to ComptoxAI by hovering over the
"Project" label in the main window and clicking the edit icon immediately to its
right. On the right side of this window, click the "Add" dropdown button, and
select "Local DBMS". In this form, set Name to anything you'd like (we use
"ComptoxAI DBMS"), and set the password to something you will remember. After
you install the Python package, this password will need to go into your
``CONFIG.yaml`` file. Next, choose version 4.2.8 from the Version dropdown menu
- this is the newest version of the DBMS that is compatible with the plugins we
will be using. Finally, click "Create" to finish the process.

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
   
   gds.export.location=C:\\\\data\\\\comptox_ai\\\\subgraphs

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
- URL: Location of the RDF file you downloaded in the previous step - see the
  note below for details

.. important::

   Specifying the RDF file's location is a bit finicky. Basically, you need to
   prepend the local path with ``file:///``. So, on a Unix system, it may look
   like ``file:///home/username/data/comptox_populated.rdf``. On Windows, you
   need to escape backslashes, so it may look like
   ``file:///C:\\\\data\\\\comptox_populated.rdf``.

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

**********************************
Building and accessing the website
**********************************

Most users probably don't need/want to do this, but we'll include the
instructions anyways.