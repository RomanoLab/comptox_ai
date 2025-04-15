We use [Sphinx](https://www.sphinx-doc.org/en/master/) to generate ComptoxAI's
documentation.

To generate the files locally, navigate to this directory and run `make html`.
Once finished the documentation will be deposited into `build/html`.

## `sphinx-autobuild`

It's easier to make larger modifications to the website if you don't need to
manually rebuild the entire site every time you make a tiny change.

If you're running it from this directory:

```{python}
sphinx-autobuild source build/html
```

Or if you're running it from the repository root:

```{python}
sphinx-autobuild docs/source docs/build/html
```

## Styles

The website uses the following colors:

#DDDDDD (light grey)
#226B07 (green)
#5D737E (dark grey)
#64B6AC (light green)