# Joey's portfolio

A minimal portfolio inspired by the spacing, navigation, and large artwork of Mouthwash Studio. The content comes from Joey's public Readymag portfolio. This folder contains the complete source and a generated website in `dist/`.

## GitHub, in plain language

GitHub stores your website files and keeps a history of changes. A **repository** is the folder containing the project. That history lets us restore an earlier version if you want to undo a change.

**GitHub Pages** publishes the website from those files. Its free option uses a public repository, so both the website and its source files are visible. A custom domain can be connected later.

You do not need to learn coding to maintain this portfolio. Tell Codex what to change, provide your new artwork, review the preview, and have Codex publish the update.

The one-time GitHub setup is complete. Your account username is `joeykrieger`; `JuicyJoeOG` is your display name. Your website files and change history are in [the portfolio repository](https://github.com/joeykrieger/joeykrieger.github.io). Approved updates pushed to its `main` branch automatically build and publish through GitHub Pages.

No password or access token needs to be pasted into this chat. Use GitHub's own sign-in screen.

## Updating through Codex

You can say things like:

- “Put Village Mice first in the project grid.”
- “Replace the Warren Lotas cover with this image.”
- “Add a new project called ___ with these pictures and this description.”
- “Change my bio to ___.”

Codex edits `content/portfolio.json`, adds images under `assets/originals/`, rebuilds the site, and checks the result. Content updates do not require changes to the page layout. The homepage uses two staggered columns with natural image proportions. Project order follows the content file, down the left column and then down the right; phones show one column. There is no featured carousel.

## Files that matter

| File | Purpose |
| --- | --- |
| `content/portfolio.json` | Name, bio, contact, project order, descriptions, and image lists |
| `assets/originals/` | Source artwork; never served to visitors |
| `assets/styles.css` | Layout and visual styling |
| `assets/site.js` | Small cursor-following thumbnail enhancement |
| `assets/project.js` | Small Read More modal enhancement |
| `templates/index.html` | Shared page structure |
| `templates/project.html` | Shared project page structure |
| `scripts/build.py` | Content validation, image resizing, and HTML generation |
| `content/source-assets.json` | Import provenance and source URLs |

An image entry looks like this:

```json
{
  "file": "my-project/cover.jpg",
  "alt": "A short description of the artwork",
  "span": "half"
}
```

`file` is relative to `assets/originals/`. Images keep their natural proportions and show the complete artwork. On project pages, `span` can be `full` (default), `half`, or `third` to arrange gallery images. All images stack on phones. The cover appears first, followed by the gallery images; duplicate file references are displayed once. Gallery entries also accept an optional `caption`. Use descriptive alt text, especially when an image contains important lettering.

Each project has an editable `title`, a short `overview`, the longer `description`, `client`, optional HTTPS `client_url`, `year`, and a `roles` list. Its `slug` becomes its page address under `projects/`. Keep slugs stable after publishing so existing links continue to work. Change the title independently when a display name needs updating.

Every project page includes a large title and short overview, a centered Read More + control, Client / Year / Role, artwork, and previous/next project links. Read More opens a rounded modal containing the project cover and the longer `description`; the description is no longer repeated below the gallery. The close button, Escape, or clicking the backdrop dismisses the modal and restores focus. Without JavaScript, the same control expands the description inline below the header. Client links open in another tab. Adding a project to the content file creates its card and page automatically; no route configuration is needed.

The landing bio is the `site.bio` list. Each segment has `text`; linked segments also have a complete HTTPS `url`. A linked segment can include a `preview` image entry for a thumbnail on hover or keyboard focus. Plain text is escaped during the build, so editing the bio does not require HTML. Keep spaces and punctuation at the ends of the surrounding text segments.

## Typography and links

The site uses your accent color `#FF5F15` for bio, contact, and video links, with `#E6530D` on hover or keyboard focus. The main navigation stays black.

The bio uses responsive type (about 42px at a 1280px desktop width, 26px on a phone), `-0.03em` letter spacing (−30 tracking), and 95% line height. Inspiration previews are image-only, 100px wide, and follow the mouse while it is over a video link. Their position is updated once per animation frame and kept inside the viewport. Keyboard focus anchors the image beside the link; Escape dismisses it.

Helvetica Neue is first in the font stack, followed by Helvetica, Arial, and the browser's sans-serif fallback. Visitors with Helvetica Neue installed see it without downloading a font. The macOS system file is not copied into the project. To make the same font available on every device, provide properly licensed webfont files; a Font Book installation alone does not establish web redistribution rights.

## Preview locally

With Python 3.12 or newer:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build.py
python -m http.server 8765 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8765. Rebuild and refresh after making changes. Use the local server to test project routes and navigation.

## Publishing to GitHub Pages

Joey's GitHub account username is `joeykrieger`; `JuicyJoeOG` is the display name. The portfolio repository is named `joeykrieger.github.io`, with the initial Pages address `https://joeykrieger.github.io`.

1. Add this folder's source to the chosen GitHub repository on its `main` branch.
2. In the repository, open **Settings → Pages** and choose **GitHub Actions** as the source.
3. Run the **Publish portfolio** workflow, or push a change to `main`.

The included workflow validates and builds the site, then publishes only `dist/`. It works at both `username.github.io` and `username.github.io/repository-name/` because all local asset URLs are relative. Add the final public URL to `site.url` for the canonical link. A custom domain can be configured in GitHub Pages settings.

Publishing through this chat still needs access to the GitHub account and the destination repository. A successful local build does not mean the site has been deployed.

## Connecting joeykrieger.me

The portfolio's domain is `joeykrieger.me`, registered through Squarespace. The domain ownership verification and website DNS records below were configured on October 4, 2026. Keep the domain registered through Squarespace and continue renewing it there; GitHub Pages hosts the website. The following steps document the connection for future maintenance:

1. In your GitHub **account Settings → Pages → Add a domain**, enter `joeykrieger.me`. GitHub gives you a TXT verification record. Add that exact record at your domain provider, return to GitHub, and click Verify. Keep the TXT record afterward. [GitHub domain verification instructions](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages).
2. In the portfolio **repository Settings → Pages → Custom domain**, enter `joeykrieger.me` and Save. Do this before pointing the domain's website records to GitHub.
3. In [Squarespace Domains](https://account.squarespace.com/domains), open `joeykrieger.me`, then **DNS → DNS Settings → Custom Records → Add record**. Add the following website records. The CNAME target has no `https://` or repository name.

| Type | Host / Name | Value |
| --- | --- | --- |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | joeykrieger.github.io |

`@` means the bare domain, `joeykrieger.me`. Review existing records before changing them: replace conflicting website records for `@` or `www`, and preserve email records such as MX, SPF, and DKIM. Use Squarespace's default TTL. A records use the **IP Address** field; CNAME records use **Alias Data**. Squarespace may request your password or 2FA again before saving. [Squarespace DNS instructions](https://support.squarespace.com/hc/en-us/articles/31119879125645-DNS-records-for-web-hosting).

4. Wait for the DNS check in GitHub Pages to pass, then turn on **Enforce HTTPS** when it becomes available. GitHub documents up to 24 hours for DNS propagation and certificate availability. `www.joeykrieger.me` will redirect to the bare domain with these records. [GitHub custom domain instructions](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).
5. Open `https://joeykrieger.me` and check a project page, Read More, and the client links. Once the domain is live, set `site.url` in the content file to `https://joeykrieger.me` and publish again for canonical links.

This project deploys using GitHub Actions, so a `CNAME` file in the source or generated website is not required. Future edits are published by updating the repository's `main` branch.

## Performance and maintenance

- Visitors get static HTML and one small stylesheet, with no framework or remote fonts.
- Cards, project pages, galleries, descriptions, and all navigation work without JavaScript. Project pages load only the small modal enhancement; the browser's native dialog handles keyboard focus and Escape.
- Source images become responsive WebP files at up to 640, 1280, and 1920 pixels wide. Originals are preserved, color profiles are converted to sRGB when provided, and photos are oriented before resizing.
- Only the first homepage cover and the first gallery image on each project page have high loading priority. Other images load lazily and have explicit dimensions to avoid layout jumps. The modal cover uses the same optimized asset as the gallery and loads lazily when opened.
- Generated images are cached locally to speed up repeat builds.
- Publishing fails for missing images, missing alt text, missing project metadata, draft projects, absent contact details, image files over 2 MB, or a page's HTML/CSS/JS over 100 KB.
- Pages share optimized image assets and one stylesheet. Smooth scrolling respects reduced motion.
- Inspiration thumbnails are optimized locally and load only on hover or keyboard focus. Touch users can open the video directly; no YouTube player is embedded.

## Import notes

Six projects were imported from the Readymag site: The Brink Of, Warren Lotas Jewelry, Warren Lotas Sports (now WL Trophy Room), Western Pulps (now WL Western Pulp Drop), Emo Nite, and Village Mice TCG. Descriptions were shortened from the existing copy, and the contact email was preserved. Joey supplied the client credits and years: Jewelry 2024, The Brink Of / Respect Films 2022, WL Trophy Room 2023, WL Western Pulp Drop 2022, Emo Nite 2024, and Village Mice / Father Steve 2023. Roles use the labels from the imported project copy.

Fifty source images were saved. The six main projects use a selection of those images; additional homepage graphics remain in `assets/originals/home/` for later updates. The Brink Of cover now uses the larger original poster. Village Mice uses three representative card designs from its original carousel. The Brink Of title animation is linked to Vimeo instead of loading a video player on the page.

The landing bio was replaced with Joey's requested Nike ACG Kids / Haddad Brands role and personal inspirations. The three preview thumbnails come from the exact YouTube videos he selected; their provenance is in `content/inspiration-sources.json`. Mouthwash Studio's artwork and branding were not copied.

Source portfolio: https://readymag.website/u2408382941/4498950/
