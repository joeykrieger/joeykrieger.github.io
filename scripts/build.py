#!/usr/bin/env python3
"""Build an accessible static portfolio from one content file."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
from html import escape
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
ORIGINALS = ROOT / "assets" / "originals"
IMAGE_CACHE: dict[str, dict] = {}


def text(value):
    return escape(str(value), quote=True)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_url(value):
    parsed = urlsplit(value)
    require(parsed.scheme == "https" and parsed.netloc and not parsed.username,
            f"Use a complete HTTPS URL: {value}")
    return value


def source_image(image):
    require(isinstance(image, dict), "Images must contain file and alt fields.")
    require(isinstance(image.get("alt"), str) and image["alt"].strip(),
            "Every artwork image needs descriptive alt text.")
    file = image.get("file", "")
    require(isinstance(file, str) and file, "Every image needs a file name.")
    path = (ORIGINALS / file).resolve()
    require(path.is_relative_to(ORIGINALS.resolve()) and path.is_file(),
            f"Image not found inside assets/originals: {file}")
    require(path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"},
            f"Export {file} as PNG, JPEG, WebP, or TIFF first.")
    require(image.get("span", "full") in {"full", "half", "third"}, "Image span must be full, half, or third.")
    return path


def validate(data, publish):
    site = data["site"]
    for field in ("name", "role", "intro"):
        require(isinstance(site.get(field), str) and site[field].strip(), f"site.{field} is required.")
    if "share_title" in site:
        require(isinstance(site["share_title"], str) and site["share_title"].strip(),
                "site.share_title must contain text.")
    if "contact_heading" in site:
        require(isinstance(site["contact_heading"], str) and site["contact_heading"].strip(),
                "site.contact_heading must contain text.")
    bio = site.get("bio")
    require(isinstance(bio, list) and bio, "site.bio needs at least one text segment.")
    for segment in bio:
        require(isinstance(segment, dict) and isinstance(segment.get("text"), str) and segment["text"].strip(),
                "Every bio segment needs text.")
        if segment.get("url"):
            safe_url(segment["url"])
        if segment.get("preview"):
            require(segment.get("url"), "A bio preview needs a link destination.")
            source_image(segment["preview"])
    require(isinstance(site.get("draft"), bool), "site.draft must be true or false.")
    email = site.get("email", "")
    require(isinstance(email, str), "site.email must be text.")
    if email:
        require(re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", email),
                "Check the contact email address.")
    for link in site.get("links", []):
        require(isinstance(link.get("label"), str) and link["label"].strip(), "Social links need labels.")
        safe_url(link["url"])
    if site.get("url"):
        safe_url(site["url"])
    projects = data["projects"]
    require(isinstance(projects, list) and projects, "Add at least one project.")
    seen = set()
    for project in projects:
        slug = project.get("slug", "")
        require(isinstance(slug, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug),
                f"Use lowercase words separated by hyphens for the project slug: {slug}")
        require(slug not in seen, f"Duplicate project slug: {slug}")
        seen.add(slug)
        for field in ("title", "overview", "description", "client", "year"):
            require(isinstance(project.get(field), str) and project[field].strip(), f"{slug}.{field} is required.")
        roles = project.get("roles")
        require(isinstance(roles, list) and roles and all(isinstance(role, str) and role.strip() for role in roles),
                f"{slug}.roles needs at least one role.")
        require(isinstance(project.get("draft"), bool), f"{slug}.draft must be true or false.")
        require(project.get("cover"), f"{slug} needs a cover image.")
        if project.get("client_url"):
            safe_url(project["client_url"])
        if project.get("motion"):
            safe_url(project["motion"]["url"])
        for image in ([project["cover"]] if project.get("cover") else []) + project.get("images", []):
            source_image(image)
        if publish:
            require(not project["draft"] and project.get("cover"), f"{slug} still needs real artwork and final content.")
    if publish:
        require(not site["draft"], "Set site.draft to false after reviewing the real content.")
        require(email or site.get("links"), "Add a real contact email or social link before publishing.")


def optimize(image, width_limits=(640, 1280, 1920)):
    path = source_image(image)
    key = (str(path), tuple(width_limits))
    if key in IMAGE_CACHE:
        return IMAGE_CACHE[key]
    from PIL import Image, ImageCms, ImageOps
    import io

    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    dest = OUT / "images"
    dest.mkdir(exist_ok=True)
    cache = ROOT / ".cache" / "images"
    cache.mkdir(parents=True, exist_ok=True)
    with Image.open(path) as original:
        require(not getattr(original, "is_animated", False), f"Use a still image for {path.name}.")
        artwork = ImageOps.exif_transpose(original)
        if artwork.info.get("icc_profile"):
            source_profile = ImageCms.ImageCmsProfile(io.BytesIO(artwork.info["icc_profile"]))
            artwork = ImageCms.profileToProfile(artwork, source_profile, ImageCms.createProfile("sRGB"),
                                               outputMode="RGBA" if "A" in artwork.getbands() else "RGB")
        else:
            artwork = artwork.convert("RGBA" if "A" in artwork.getbands() else "RGB")
        width, height = artwork.size
        widths = sorted({min(width, limit) for limit in width_limits})
        variants = []
        for target_width in widths:
            target_height = max(1, round(height * target_width / width))
            resized = artwork.resize((target_width, target_height), Image.Resampling.LANCZOS)
            name = f"{digest}-{target_width}.webp"
            cached = cache / name
            if not cached.exists():
                for quality in (90, 82, 74):
                    resized.save(cached, "WEBP", quality=quality, method=6)
                    if cached.stat().st_size < 2_000_000:
                        break
            require(cached.stat().st_size < 2_000_000,
                    f"{path.relative_to(ORIGINALS)} exceeds the 2 MB image budget at {target_width}px.")
            shutil.copyfile(cached, dest / name)
            variants.append((name, target_width))
    info = {"width": width, "height": height, "variants": variants}
    IMAGE_CACHE[key] = info
    return info


def image_html(image, eager=False, sizes="(max-width: 760px) 90vw, 44vw", prefix="./"):
    info = optimize(image)
    srcset = ", ".join(f"{prefix}images/{name} {width}w" for name, width in info["variants"])
    name = info["variants"][-1][0]
    return (f'<img src="{prefix}images/{name}" srcset="{srcset}" sizes="{text(sizes)}" '
            f'width="{info["width"]}" height="{info["height"]}" alt="{text(image["alt"])}" '
            f'loading="{"eager" if eager else "lazy"}" decoding="async"'
            f'{" fetchpriority=\"high\"" if eager else ""}>')


def bio_html(segments):
    parts = []
    for segment in segments:
        label = text(segment["text"])
        if not segment.get("url"):
            parts.append(label)
            continue
        preview = segment.get("preview")
        attributes = ""
        if preview:
            sidebar_preview = preview.get("placement") == "sidebar"
            name = optimize(preview, width_limits=(480,) if sidebar_preview else (200,))["variants"][0][0]
            attribute = "data-name-preview-src" if sidebar_preview else "data-preview-src"
            attributes = f' {attribute}="./images/{name}"'
        parts.append(f'<a href="{text(segment["url"])}" target="_blank" rel="noopener noreferrer"'
                     f'{attributes}>{label}</a>')
    return "".join(parts)



GALLERY_SIZES = "(max-width: 720px) 90vw, (max-width: 1100px) 68vw, (max-width: 1800px) 55vw, 960px"


def slides_for(project):
    slides, seen = [], set()
    for image in [project["cover"], *project.get("images", [])]:
        if image["file"] in seen:
            continue
        seen.add(image["file"])
        info = optimize(image)
        slides.append({
            "src": "./images/" + info["variants"][-1][0],
            "srcset": ", ".join(f"./images/{name} {width}w" for name, width in info["variants"]),
            "width": info["width"], "height": info["height"],
            "alt": image["alt"], "caption": image.get("caption", ""),
        })
    return slides


def project_html(project, eager=False):
    slug, title = text(project["slug"]), text(project["title"])
    slides = slides_for(project)
    payload = json.dumps(slides, ensure_ascii=False).replace("<", "\\u003c")
    image = image_html(project["cover"], eager=eager, sizes=GALLERY_SIZES).replace("<img ", '<img class="gallery-image" ')
    client = text(project["client"])
    if project.get("client_url"):
        client = f'<a href="{text(project["client_url"])}" target="_blank" rel="noopener noreferrer">{client}</a>'
    motion = project.get("motion")
    motion_link = (f'<p class="motion-link"><a href="{text(motion["url"])}" target="_blank" rel="noopener noreferrer">'
                   f'{text(motion["label"])}</a></p>') if motion else ""
    controls = (f'<button class="gallery-hit gallery-prev" type="button" aria-label="Previous image — {title}" aria-controls="stage-{slug}"><span aria-hidden="true"></span></button>'
                f'<button class="gallery-hit gallery-next" type="button" aria-label="Next image — {title}" aria-controls="stage-{slug}"><span aria-hidden="true"></span></button>') if len(slides) > 1 else ""
    fallback = "".join(image_html(image, sizes=GALLERY_SIZES) for image in project.get("images", []))
    return f'''
      <article class="project-row" id="{slug}" aria-labelledby="title-{slug}">
        <div class="project-notes">
          <h2 class="project-title" id="title-{slug}">{title}</h2>
          <p class="project-overview">{text(project["overview"])}</p>
          <p class="project-roles">{text(" · ".join(project["roles"]))}</p>
          <details class="project-details">
            <summary><span class="more-label">Read more</span><span class="less-label">Read less</span><span class="disclosure-symbol" aria-hidden="true"></span></summary>
            <div class="project-story"><p>{text(project["description"])}</p><p class="project-client">Client: {client}</p>{motion_link}</div>
          </details>
        </div>
        <section class="gallery" aria-label="{title} image gallery" aria-roledescription="carousel">
          <div class="gallery-heading"><span>{text(project["year"])}</span></div>
          <figure>
            <div class="gallery-stage" id="stage-{slug}">{image}{controls}</div>
            <figcaption class="gallery-caption" hidden></figcaption>
          </figure>
          <p class="gallery-status sr-only" role="status"></p>
          <script class="gallery-data" type="application/json">{payload}</script>
          <noscript><details class="gallery-fallback"><summary>View all images</summary>{fallback}</details></noscript>
        </section>
      </article>
'''


def social_metadata(site, image_name):
    base = site.get("url", "").rstrip("/") + "/"
    if base == "/":
        return ""
    properties = {
        "og:title": site.get("share_title", site["role"]), "og:site_name": site["name"],
        "og:type": "website", "og:url": base, "og:description": site["intro"],
        "og:image": urljoin(base, image_name), "og:image:type": "image/png",
        "og:image:width": "1200", "og:image:height": "630",
        "og:image:alt": "IF A BAGEL CAN HAVE EVERYTHING, SO CAN YOU. — centered orange lettering on white",
    }
    properties.update({"twitter:card": "summary_large_image", "twitter:title": properties["og:title"],
                       "twitter:description": site["intro"], "twitter:image": properties["og:image"]})
    return "\n  ".join(f'<meta {"name" if key.startswith("twitter:") else "property"}="{key}" content="{text(value)}">' for key, value in properties.items())


def build(publish=False):
    data = json.loads((ROOT / "content/portfolio.json").read_text())
    validate(data, publish)
    IMAGE_CACHE.clear()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    site = data["site"]
    share_name = "share-preview-" + hashlib.sha256((ROOT / "assets/share-preview.png").read_bytes()).hexdigest()[:12] + ".png"
    values = {
        "TITLE": text(f'{site["name"]} — {site["role"]}'),
        "DESCRIPTION": text(site["intro"]), "BIO": bio_html(site["bio"]),
        "CANONICAL": f'<link rel="canonical" href="{text(site["url"].rstrip("/") + "/")}">' if site.get("url") else "",
        "EMAIL": text(site["email"]), "NAME": text(site["name"]), "YEAR": str(date.today().year),
        "CONTACT_HEADING": text(site.get("contact_heading", "Get in touch")),
        "SOCIAL_LINKS": "".join(f'<a href="{text(link["url"])}" target="_blank" rel="noopener noreferrer" aria-label="{text(link.get("aria_label", link["label"]))}">{text(link["label"])}</a>' for link in site.get("links", [])),
        "STYLE_VERSION": hashlib.sha256((ROOT / "assets/styles.css").read_bytes()).hexdigest()[:12],
        "SITE_VERSION": hashlib.sha256((ROOT / "assets/site.js").read_bytes()).hexdigest()[:12],
        "GALLERY_VERSION": hashlib.sha256((ROOT / "assets/galleries.js").read_bytes()).hexdigest()[:12],
        "CV_VERSION": hashlib.sha256((ROOT / "assets/Joey_Krieger_GraphicDesigner.pdf").read_bytes()).hexdigest()[:12],
        "ICON_VERSION": hashlib.sha256((ROOT / "assets/favicon.svg").read_bytes()).hexdigest()[:12],
        "SOCIAL_META": social_metadata(site, share_name),
        "PROJECTS": "".join(project_html(project, eager=index == 0) for index, project in enumerate(data["projects"])),
    }
    template = (ROOT / "templates/index.html").read_text()
    page = re.sub(r"@@([A-Z_]+)@@", lambda match: values[match[1]], template)
    (OUT / "index.html").write_text(page)
    # Preserve previously published project addresses after moving to one page.
    for project in data["projects"]:
        destination = "../../#" + project["slug"]
        route = OUT / "projects" / project["slug"]
        route.mkdir(parents=True)
        canonical = f'<link rel="canonical" href="{text(site["url"].rstrip("/") + "/")}">' if site.get("url") else ""
        (route / "index.html").write_text(
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta http-equiv="refresh" content="0; url={text(destination)}">'
            f'{canonical}<title>{text(project["title"])} — {text(site["name"])}</title>'
            f'</head><body><p><a href="{text(destination)}">View {text(project["title"])}</a></p></body></html>'
        )
    for asset in ("styles.css", "site.js", "galleries.js", "favicon.svg", "favicon.png", "apple-touch-icon.png", "Joey_Krieger_GraphicDesigner.pdf"):
        shutil.copyfile(ROOT / "assets" / asset, OUT / asset)
    shutil.copyfile(ROOT / "assets/share-preview.png", OUT / share_name)
    (OUT / ".nojekyll").touch()
    shell_bytes = sum((OUT / asset).stat().st_size for asset in ("index.html", "styles.css", "site.js", "galleries.js"))
    require(shell_bytes < 100_000, "HTML, CSS, and JavaScript exceed the 100 KB budget.")
    print(f'Built single-page portfolio: {OUT}')
    print(f'{len(data["projects"])} projects; HTML + CSS + JavaScript: {shell_bytes:,} bytes.')
    print("Original artwork is preserved outside dist. This build does not publish.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true", help="Validate finished content; does not deploy.")
    args = parser.parse_args()
    try:
        build(args.publish)
    except (ValueError, KeyError, OSError, ImportError) as error:
        print(f"Build stopped: {error}", file=sys.stderr)
        sys.exit(1)
