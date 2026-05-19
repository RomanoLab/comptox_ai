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

Like above, you probably don't need to install anything. The `Memgraph Lab
browser <https://lab.comptox.ai>`_ lets you explore a full copy of the graph
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
the datasets. In this case you should install **the Python package** and run a
local copy of the **Memgraph graph database** (see the local-deploy section
below).

"I want to run a few Python analyses using some of ComptoxAI's data"
====================================================================

Depending on the size of your analyses, you can probably just install **the
Python package**, and connect to the public graph database rather than hosting
an entire copy locally. If you find that analyses are slow, if bandwidth is a
concern, or you want to modify the contents of the graph database for any reason,
it is probably best to run a local copy of the **Memgraph graph database**.

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

**************************************************
Running the ComptoxAI graph database locally
**************************************************

.. note::

   ComptoxAI has migrated from Neo4j to **Memgraph**. The legacy Neo4j-
   Desktop-based setup previously documented on this page is no longer
   supported. Most users do not need to run the database locally — the
   public read-only endpoint is available at:

   - **Web browser:** https://lab.comptox.ai (Memgraph Lab UI)
   - **Bolt driver:** ``neo4j+s://bolt.comptox.ai``  (the official Neo4j
     Python driver speaks Bolt to Memgraph)

   For local development, the simplest path is the project's
   ``docker-compose.yml``, which runs Memgraph alongside the API, the
   bolt-proxy, and Memgraph Lab:

   .. code-block:: bash

      docker compose up -d
      # Memgraph         :7687   (Bolt)
      # Memgraph Lab     :3000
      # REST API         :3001
      # bolt-proxy       :7688   (write-filtering proxy used in prod)

   Detailed instructions for a non-Docker local Memgraph install, including
   loading the latest ComptoxAI snapshot, are being written and will be
   linked here when ready.

Since this cleaning is an irreversible process, you need to confirm that you
want to proceed.

After the script finishes running, you should be all set up and good to go!

**********************************
Building and accessing the website
**********************************

Most users probably don't need/want to do this, but we'll include the
instructions anyways.