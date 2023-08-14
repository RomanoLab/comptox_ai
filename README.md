# `ComptoxAI`

[![DOI](https://zenodo.org/badge/202416245.svg)](https://zenodo.org/badge/latestdoi/202416245)

![comptox_ai](https://github.com/jdromano2/comptox_ai/actions/workflows/python-package.yml/badge.svg) ![web app](https://github.com/jdromano2/comptox_ai/actions/workflows/react-build.yml/badge.svg) ![docs](https://github.com/jdromano2/comptox_ai/actions/workflows/doc-build.yml/badge.svg)

[Website](https://comptox.ai/)

A modern data infrastructure for AI research in computational toxicology.

---

ComptoxAI is a collection of resources made to enable a diverse range of artificial intelligence applications for computational toxicology data. This repository contains all of the code that comprises the overall ComptoxAI project, including code related to the database, website, REST API, graph machine learning toolkit, and other miscellaneous utilities.

ComptoxAI is maintained by [the Romano Lab](http://romanolab.org) at the [University of Pennsylvania](https://upenn.edu) in the [Institute for Biomedical Informatics](https://ibi.med.upenn.edu/) and the [Center of Excellence in Environmental Toxicology](http://ceet.upenn.edu/).

### Installing

How you install ComptoxAI depends on whether you want to _analyze the knowledge graph_ or if you want to _build the knowledge graph from scratch_:

**I want to analyze ComptoxAI's knowledge graph**:

This should be relatively simple. You might need to install a different version of Python (we currently perform testing on v3.8), but otherwise the following should suffice:

```bash
$ git clone https://github.com/RomanoLab/comptox_ai
$ cd comptox_ai
$ pip install .
```

**I want to build a copy of the knowledge graph myself**:

This is a bit more complex. The short version of what to do goes as follows:

1. Install `conda` or `mamba`
2. Clone this repository and install the `conda` environment specified in `environment.yml`, e.g.:

```bash
$ git clone https://github.com/RomanoLab/comptox_ai
$ cd comptox_ai
$ mamba env create -n comptox_ai --file environment.yml -c conda-forge
$ mamba activate comptox_ai
```

3. Download all of the necessary data/knowledge sources
4. Run `ista` to build the knowledge graph from the sources
5. Install the knowledge graph into Neo4j
6. Check to make sure everything works as intended

We'll create more detailed instructions at some point in the near future. In the meantime, you can file an Issue or contact us by email with any questions or bugs.

### Funding

-   `K99-LM013646` (PI: Joseph D. Romano)
-   `P30-ES013508` (PI: Trevor M. Penning)
-   `R01-AG066833` (PIs: Jason H. Moore, Marylyn D. Ritchie, Li Shen)

### Contributions

We welcome collaborations and contributions from third-party developers. Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for further information.

### License

ComptoxAI is offered under a dual-license model, including an open-source option via the GNU GPLv3. See [LICENSE](LICENSE) for details.
