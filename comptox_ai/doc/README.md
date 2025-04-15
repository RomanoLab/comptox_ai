These files contain narrative-style documentation for important concepts that
make up ComptoxAI's codebase. They will be read (via `docutils` and `autodoc`)
by Sphinx and compiled into Sphinx's output.

There are two reasons why this setup is beneficial:

- The documentation is accessible as docstrings (e.g., via `help()`) within the Python interpreter.
- Extended restructured text capabilities are added that aren't easily accessible from within Sphinx alone. For some reason, Sphinx doesn't like commonly-used table formats defined for rST.