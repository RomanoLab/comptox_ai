.. _web_api:

************
REST Web API
************

We provide access to ComptoxAI's data via a REST web API. Some supported
operations include node/relationship search and accession, description of the
database's overall structure, shortest path generation, bulk data download, and
others.

Unless specified otherwise, all responses to API queries are in JSON format.

API Routes
**********

The base URL for all API queries is::
   
   https://comptox.ai/api/

A complete list of API routes and endpoints is provided in our Swagger API
documentation.

Web API Implementation
**********************

The Web API is implemented as a NodeJS application using ExpressJS to process
and respond to HTTP requests. The API follows the OpenAPI specification
(formerly known as Swagger), and can be accessed using most modern programming
languages.

Contributions and Suggestions
*****************************

We welcome new contributions (in the form of GitHub pull requests) and
suggestions for ways to improve the Web API (by `submitting a new issue 
<https://github.com/JDRomano2/comptox_ai/issues/new>`_ with the "enhancement" 
tag).

For more details, please refer to :ref:`contributing`.