## Contributing to ComptoxAI

ComptoxAI is open source, and we encourage contributions from developers,
computational toxicologists, informatics researchers, and anyone else who feels
they have something to contribute!

## Local development

Prerequisites:
- Node.js 20+
- A local Memgraph instance reachable at `bolt://localhost:7687` with the
  ComptoxAI knowledge graph loaded. The fastest way is `docker run -p 7687:7687
  memgraph/memgraph:2.18.1` and then importing your dump.

Default local port layout:
- **3000** — Memgraph Lab (web UI, when running via Compose)
- **3001** — REST API
- **3002** — React app
- **7687** — Memgraph (Bolt)
- 8000 — Sphinx docs (when `dev:docs` is running)
- 7688 — bolt-proxy (Compose only)

One-time setup (from the repository root):

```
npm run install:all
```

This installs dependencies for the root tooling and the npm workspace under
`web/` that holds the REST API (`web/packages/api`) and the React app
(`web/packages/app`). Both packages share `web/package-lock.json`; npm hoists
shared deps into `web/node_modules`.

Then, to run both servers with hot reload:

```
npm run dev
```

You'll get:
- API on http://localhost:3001 (nodemon — restarts on file changes)
- Swagger UI on http://localhost:3001/help
- React app on http://localhost:3002 (Vite — sub-second HMR)

The React app's API base URL flips based on `import.meta.env.PROD`: in dev
it points at `http://localhost:3001`, in production at `https://comptox.ai/api`.
No extra config required.

To run only one piece:

```
npm run dev:api      # just the REST API
npm run dev:app      # just the React app
npm run dev:docs     # just sphinx-autobuild on docs/ (port 8000)
```

If you also want live-reloading docs alongside the API and app:

```
pip install -r docs/requirements.txt   # one-time
npm run dev:full                       # api + app + docs concurrently
```

The React app runs at the root of `:3001` in dev. In production it's
served from `/browse/` inside the merged Sphinx output (see `vite.config.js`'s
conditional `base`), so refreshing inner SPA routes works locally without
any extra setup.

Configuration overrides go in `web/packages/api/.env` (copy from
`.env.example`). The default DB URL `bolt://localhost:7687` works for a
Memgraph running directly on your host; change it if you're running
Memgraph in Docker on a different port or host.

For full-stack local testing (Memgraph + bolt-proxy + API + Lab + Caddy in
containers), use `docker compose up -d` from the repo root — see
`infra/README.md`.



We ask that all contributions are submitted in the form of pull requests.
GitHub's documentation pages contain a good introduction to forking and
submitting pull requests:

[https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork]

## Bugs

Create a bug report by filing an issue with the ``bug`` tag:

https://github.com/jdromano2/comptox_ai/issues

## Questions

Feel free to ask questions via the issue tracker, by filing a new issue with
the ``question`` tag.

We're also more than happy to discuss potential scientific collaborations. If
you have an exciting idea in mind, please contact us by email, using the
[address listed on our website](http://comptox.ai/contact.html).