# YUSEN Interactive Demos (Vite + GitHub Pages)

## Included demos
1. ERS Calculator — AI-assisted Decision Risk & Stability System
2. Multi-agent Collaboration Calibration System (5 agents)
3. Multi-step Workflow Orchestration Framework (Cooking Mode)

## Run locally
```bash
npm install
npm run dev
```

## Build
```bash
npm run build
npm run preview
```

## Deploy (GitHub Pages)
1. Push to GitHub repo
2. Settings → Pages → Source: GitHub Actions
3. Push to `main` triggers deployment

Notes:
- `base: './'` in `vite.config.js` makes assets load correctly under `/repo/` on GitHub Pages.
- `scripts/postbuild.js` generates `dist/404.html` for fallback.

<!-- trigger redeploy -->
