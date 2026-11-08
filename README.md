# Joey Krieger — single-page portfolio

Joey’s single-page portfolio, with a pinned bio, a project grid, inline project descriptions, image galleries, orange links, and inspiration previews.

Website: [https://www.joeykrieger.me](https://www.joeykrieger.me). Source: [joeykrieger/joeykrieger.github.io](https://github.com/joeykrieger/joeykrieger.github.io). Approved pushes to main automatically publish through GitHub Pages.

The sidebar links are Resume, Email, and IG (@virtual.cowboy), with orange hover and keyboard-focus states. All seven projects live on the homepage, with ACG Holiday 2026 first. The bio stays pinned on desktop. The overview uses a masonry grid of square-edged project covers: three columns on desktop, two on smaller screens, and one on phones. Clicking a cover opens that project’s notes and gallery in the same document. Back to projects or Escape restores the grid, selected tile, and scroll position. Browser Back/Forward and direct project hash links also work.

Each project has a compact description column with an inline Read more / Read less disclosure and a large image gallery. Click the left half of the gallery to go back, or the right half to advance. Galleries use small chevrons with no visible image counters. They wrap at each end and work independently. Keyboard users can focus either gallery button and use the left/right arrow keys. Touch users can tap either half or swipe horizontally.

Images retain their original proportions. The gallery frame stays steady as images change; desktop height is capped at 70% of the viewport and 640px. On smaller desktop/tablet screens, project descriptions move above their galleries. On mobile, the bio appears above the projects and the gallery gets its own responsive frame. Without JavaScript, covers link to projects lower on the page, descriptions still expand, and each project offers View all images.

## Content and source

- `content/portfolio.json`: bio segments, links, project order, short overview, long description, roles, client, year, and image lists.
- `assets/originals/`: untouched artwork originals.
- `assets/styles.css`: layout and responsive styles.
- `assets/site.js`: inspiration hover previews and the name portrait easter egg.
- `assets/galleries.js`: independent galleries, image loading, keyboard navigation, and touch gestures.
- `assets/project-index.js`: same-page project switching, browser history, focus and scroll restoration, and masonry sizing.
- `templates/index.html`: the single-page document.
- `scripts/build.py`: validates the content, creates responsive local WebP images, and generates `dist/`.

## Build and preview

Requires Python and Pillow, as listed in `requirements.txt`.

```sh
python3 scripts/build.py --publish
python3 -m http.server 8772 --bind 127.0.0.1 --directory dist
```

Then open http://127.0.0.1:8772/. The `--publish` flag validates finished content; it does not publish anything. The build sets the canonical address and social metadata from site.url. Styles and scripts have content-based versions so approved updates load correctly. Previously published projects/<slug>/ addresses redirect to the matching homepage section.

Review changes locally and obtain Joey’s approval for each publishing batch before pushing. After a successful push, let GitHub Pages finish deploying in the background; do not wait or recheck the live site unless Joey asks.

The workflow in .github/workflows/pages.yml validates and builds the source, then publishes only dist/. Image originals are stored in source and are never served to site visitors. The custom domain and HTTPS settings remain managed by GitHub Pages.

Joey approved the gallery homepage and revised ACG images for publishing on November 8, 2026. ACG Holiday 2026 uses `assets/originals/ACG Holiday 2026/ACG_HO26-01.png` as its cover, followed by images 02–08. The matching local upload folder is `../New Project Photos/ACG Holiday 2026/`; the previous image set is archived there and in the separate gallery comparison.

## Name portrait

Hover or keyboard-focus Joey’s name to reveal his portrait near the bottom of the desktop bio column. It hides on leaving the name, losing keyboard focus, Escape, or resizing. The portrait uses a transparent 480px WebP loaded only on reveal. On short screens it shrinks into the available space or stays hidden to avoid covering the bio and navigation. It stays hidden on the mobile layout. The original PNG is preserved under `assets/originals/profile/`. The name continues to link to LinkedIn.
