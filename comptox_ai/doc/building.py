"""
Overview of the build process
*****************************

ComptoxAI consists of several main components:

#. The Python ``comptox_ai`` package, which includes:

   #. A connection to the graph database 
   #. A library of graph machine learning models 
   #. This documentation

#. ComptoxAI's graph database (implemented in Neo4j) 
#. The ComptoxAI OWL ontology (developed in Protégé and populated using ``owlready2``)
#. The ComptoxAI website

When you install the Python package, the other components are
(currently) not automatically built and installed simultaneously,
although complete automation of the build is intended for a future
release.

Installing prerequisites
************************

Python package prerequisites
----------------------------

All prerequisites for the Python package are included in
``requirements.txt`` and ``requirements-conda.txt``. After downloading
the source distribution, you can install all packages via PIP by
running::

  $ pip install -r requirements.txt

If you use Conda to manage your Python distribution, you can install
many of the packages from their Conda sources by first running::

  $ conda install -r requirements-conda.txt

Since Conda doesn't index several of the prerequisite packages, you
should follow this command by running the ``pip`` installation shown
above.

Ontology prerequisites
----------------------

*tl,dr; Most users don't need to install anything new.*

=============  ==============  ==========
Prerequisite   Version         Notes
=============  ==============  ==========
Protégé        5.5.0           *optional*
=============  ==============  ==========

The base ontology (i.e., not populated with individuals) is included
as part of the Python package's source distribution, and named
``comptox.rdf``. This file was created manually using the Protégé
ontology editor (v5.5.0). The OWL/RDF file can be opened and modified
in any modern OWL ontology editor, although we prefer Protégé, but
doing so may cause errors later in the build process.

During the build process, we use ``owlready2`` to handle all Python
interactions with the base ontology. ``owlready2`` is included as a
prerequisite in the ``requirements.txt`` file, so it should be
installed for all users who have followed the standard installation
instructions.

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
Neo4j          at least 3.5.6
Neo4j desktop                  *optional*
=============  ==============  ==========

ComptoxAI's graph database is implemented using the Neo4j graph
database management system, which is currently the leading graph
database software for both academic and commercial applications.
Depending on your local operating system, hardware, and level of skill
administrating client/server applications you may opt to use different
Neo4j implementations, but most users should install Neo4j Desktop due
to its ease of use and self-contained nature.

.. seealso::
   
   :ref:`guide_databases`
   
   :ref:`graph`

Running the build script
************************

The script used to populate the ontology and build the graph database
is currently found at ``comptox_ai/scripts/build/build_all.py``. It
can be run like any typical Python script::

  $ python3.7 ./build_all.py

Windows users may encounter issues running the build script, since no
standard implementation of `curses` exists for Python on Windows. A
good workaround has been to install the wheel file from the following
link corresponding to your version of Python and whether you are
running 32- or 64-bit Windows: https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses

Testing the build
*****************

The unit tests included in the ``tests/`` directory (relative to the
source code's root) cover not only the Python package, but also the
graph database and ontology. These tests are run using ``pytest``,
which is included in the Python package's prerequisites (and therefore
is likely already installed).

To perform the tests, simply navigate to the package root and run::

  $ pytest tests/

Running ComptoxAI locally vs. on a server
*****************************************

"""