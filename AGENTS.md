# Portfolio maintenance

Joey reviewed and authorized publishing the single-page redesign on October 5, 2026.

- Edit content/portfolio.json and source files; never edit generated dist/ directly.
- Preserve bold readable type, orange accents, the pinned desktop bio, single-page projects, and newest-year-first ordering.
- Keep all artwork complete and uncropped in stable gallery frames. Preserve image originals and local optimized assets.
- Preserve independent galleries, inline Read more, left/right image-half clicks, keyboard controls, and touch gestures. On desktop show each arrow only over its own half or on keyboard focus; keep touch arrows visible.
- Joey's portrait appears at the bottom of the desktop bio on name hover or keyboard focus, loads on demand, and stays clear of the text. Preserve the name's LinkedIn link.
- Preserve existing project addresses under projects/ as redirects to homepage anchors.
- Keep the site static and dependency-light. Warn Joey before adding anything with a meaningful performance cost.
- Run python3 scripts/build.py --publish before delivery or pushing. This validates locally; it does not deploy.
- Verify relevant layout and interactions locally, show a reviewable preview, and obtain approval for each publishing batch. Earlier approvals are not permission for future updates.
- After an approved push succeeds, report the push and let GitHub Pages deploy in the background. Do not wait for deployment or recheck the live site unless Joey requests it or reports a problem.
