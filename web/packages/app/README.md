# @comptoxai/comptox-app

Interactive React data browser for ComptoxAI. Built with **Vite** + React 17 +
Redux Toolkit + MUI. Lives at the root of `localhost:3002` in dev, and is
served from `/browse/` inside the Sphinx-built static site in production
(see `vite.config.js`'s conditional `base`).

## Scripts

Run from this directory, or from the repo root via the workspace shorthand
(see `CONTRIBUTING.md`).

| Command | What it does |
| --- | --- |
| `npm start` | Vite dev server on `http://localhost:3002` (HMR, opens nothing). |
| `npm run build` | Production bundle to `build/`, with all asset URLs prefixed `/browse/` and a single `static/js/main.js` + `static/css/main.css`. |
| `npm run preview` | Serve the built `build/` dir on `:3002` for a local prod-like check. |

## Production deploy

`npm run build` produces a self-contained `build/` directory whose layout
matches what `infra/deploy-site.sh` and `.github/workflows/deploy-site.yml`
expect. They:

1. Build the Sphinx site → `docs/build/html/`
2. Copy `web/packages/app/build/*` into `docs/build/html/browse/`
3. Sync the merged tree to S3 + invalidate CloudFront

The `base: '/browse/'` in `vite.config.js` ensures asset URLs in the built
`index.html` resolve correctly from the `/browse/` subpath.
