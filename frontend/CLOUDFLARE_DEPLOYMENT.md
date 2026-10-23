# Cloudflare deployment

Worker: `marketplace-web`

Cloudflare Workers Builds configuration:

- Root directory: `frontend`
- Build command: `npm ci && npm run build`
- Deploy command: `npx wrangler deploy`
- Initial production branch: `fix/cloudflare-spa-routing`

`wrangler.jsonc` publishes `dist` with SPA fallback enabled. Vite reads the public API URL from `.env.production`.

After deployment, verify `/`, `/products`, `/login`, `/cart`, and `/checkout` with direct navigation and refresh. Confirm that HTML references built `/assets/` files, not `/src/main.jsx`.

Previous Worker versions remain available in Cloudflare Deployments for rollback. Do not delete the Worker or modify backend data to roll back the frontend.
