# Portfolio maintenance

The owner wants a minimal portfolio that stays easy to update through Codex. Preserve that scope as the site evolves.

- Read `README.md` and the current content before editing. The source of truth is `content/portfolio.json`; do not edit generated `dist/` files.
- Update project content and image lists without changing layout code when possible.
- Keep the site static. Add dependencies or a framework only when a requested feature needs them.
- Preserve image originals; use the build pipeline for responsive website assets. Never link the deployed site to Readymag's image CDN.
- Show complete artwork by default. Choose cropping only when the owner requests it or it is clearly appropriate for that asset.
- Preserve semantic HTML, keyboard operation, mobile layouts, readable text, reduced-motion support, and lazy image loading.
- Run `python scripts/build.py --publish` before delivery or deployment. Verify desktop and mobile appearance, the changed content, project routes, gallery proportions, and navigation when relevant. The homepage uses natural image sizes in two staggered columns; project pages are static HTML with a small Read More modal enhancement. Check modal opening, dismissal, keyboard focus, and mobile scrolling when changing it.
- Report whether a change was only previewed locally or actually deployed. Do not claim a live deployment until GitHub Pages reports success.
