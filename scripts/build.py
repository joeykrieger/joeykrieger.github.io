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
            name = optimize(preview, width_limits=(200,))["variants"][0][0]
            attributes = f' data-preview-src="./images/{name}"'
        parts.append(f'<a href="{text(segment["url"])}" target="_blank" rel="noopener noreferrer"'
                     f'{attributes}>{label}</a>')
    return "".join(parts)


def project_card(project, eager=False):
    slug = text(project["slug"])
    return (f'<article class="project-card" id="project-{text(project["slug"])}">'
            f'<a class="project-link" href="./projects/{slug}/" aria-labelledby="title-{slug}">'
            f'{image_html(project["cover"], eager=eager)}'
            '<div class="project-card-caption">'
            f'<h3 class="project-title" id="title-{slug}">{text(project["title"])}</h3>'
            f'<p class="project-meta">{text(" · ".join(project["roles"]))} · {text(project["year"])}</p>'
            '</div></a></article>')


def gallery_html(project):
    gallery = []
    seen = set()
    for image in [project["cover"], *project.get("images", [])]:
        if image["file"] in seen:
            continue
        seen.add(image["file"])
        span = image.get("span", "full")
        sizes = "(max-width: 760px) 90vw, " + {"full": "90vw", "half": "44vw", "third": "29vw"}[span]
        caption = f'<figcaption>{text(image["caption"])}</figcaption>' if image.get("caption") else ""
        gallery.append(f'<figure data-span="{span}">{image_html(image, eager=len(gallery) == 0, sizes=sizes, prefix="../../")}{caption}</figure>')
    return "".join(gallery)


def project_page(project, previous, following, common):
    client = text(project["client"])
    if project.get("client_url"):
        client = (f'<a href="{text(project["client_url"])}" target="_blank" rel="noopener noreferrer">'
                  f'{client}</a>')
    motion = project.get("motion")
    motion_link = (f'<p class="motion-link"><a href="{text(motion["url"])}" target="_blank" rel="noopener noreferrer">'
                   f'{text(motion["label"])}</a></p>' if motion else "")
    navigation = (f'<a href="../{text(previous["slug"])}/"><span>Previous project</span>{text(previous["title"])}</a>'
                  f'<a href="../{text(following["slug"])}/"><span>Next project</span>{text(following["title"])}</a>')
    values = common | {
        "TITLE": text(f'{project["title"]} — {common["RAW_NAME"]}'),
        "DESCRIPTION": text(project["overview"]),
        "CANONICAL": canonical(common["SITE_URL"], f'projects/{project["slug"]}/'),
        "PROJECT_TITLE": text(project["title"]), "OVERVIEW": text(project["overview"]),
        "CLIENT": client, "PROJECT_YEAR": text(project["year"]),
        "ROLES": "".join(f'<li>{text(role)}</li>' for role in project["roles"]),
        "GALLERY": gallery_html(project), "STORY": text(project["description"]),
        "STORY_IMAGE": image_html(project["cover"], sizes="(max-width: 760px) 85vw, 800px", prefix="../../"),
        "MOTION": motion_link, "PROJECT_NAVIGATION": navigation,
        "SOCIAL_META": social_metadata(common["SITE_URL"], common["RAW_NAME"], project["title"],
                                       project["overview"], common["SHARE_IMAGE"], f'projects/{project["slug"]}/'),
    }
    values["ROBOTS"] = '<meta name="robots" content="noindex, nofollow">' if project["draft"] or common["SITE_DRAFT"] else ""
    return render("project.html", values)


def canonical(site_url, path=""):
    if not site_url:
        return ""
    return f'<link rel="canonical" href="{text(urljoin(site_url.rstrip("/") + "/", path))}">'


def social_metadata(site_url, site_name, title, description, image_name, path=""):
    if not site_url:
        return ""
    base = site_url.rstrip("/") + "/"
    image_url = urljoin(base, image_name)
    image_alt = "IF A BAGEL CAN HAVE EVERYTHING, SO CAN YOU. — centered orange lettering on white"
    properties = {
        "og:title": title, "og:site_name": site_name, "og:type": "website",
        "og:url": urljoin(base, path), "og:description": description,
        "og:image": image_url, "og:image:type": "image/png",
        "og:image:width": "1200", "og:image:height": "630", "og:image:alt": image_alt,
    }
    tags = [f'<meta property="{key}" content="{text(value)}">' for key, value in properties.items()]
    for key, value in {"twitter:card": "summary_large_image", "twitter:title": title,
                       "twitter:description": description, "twitter:image": image_url,
                       "twitter:image:alt": image_alt}.items():
        tags.append(f'<meta name="{key}" content="{text(value)}">')
    return "\n  ".join(tags)


def render(template_name, values):
    template = (ROOT / "templates" / template_name).read_text()
    return re.sub(r"@@([A-Z_]+)@@", lambda match: values[match[1]], template)


def build(publish=False):
    data = json.loads((ROOT / "content" / "portfolio.json").read_text())
    validate(data, publish)
    IMAGE_CACHE.clear()
    # Only the generated dist directory is replaced; originals and content are preserved.
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    site = data["site"]
    projects = data["projects"]
    share_image_name = "share-preview-" + hashlib.sha256((ROOT / "assets" / "share-preview.png").read_bytes()).hexdigest()[:12] + ".png"
    contacts = []
    if site.get("email"):
        contacts.append(f'<a class="email-link" href="mailto:{text(site["email"])}">{text(site["email"])}</a>')
    for link in site.get("links", []):
        contacts.append(f'<a href="{text(link["url"])}">{text(link["label"])}</a>')
    if not contacts:
        contacts.append('<p class="contact-pending">Contact details coming soon.</p>')
    contact_section = render("contact.html", {
        "CONTACT_HEADING": text(site.get("contact_heading", "Get in touch")),
        "CONTACT": "".join(contacts),
    })
    common = {
        "STYLE_VERSION": hashlib.sha256((ROOT / "assets" / "styles.css").read_bytes()).hexdigest()[:12],
        "CV_VERSION": hashlib.sha256((ROOT / "assets" / "Joey_Krieger_GraphicDesigner.pdf").read_bytes()).hexdigest()[:12],
        "ICON_VERSION": hashlib.sha256((ROOT / "assets" / "favicon.svg").read_bytes()).hexdigest()[:12],
        "SHARE_IMAGE": share_image_name,
        "RAW_NAME": site["name"], "SITE_URL": site.get("url", ""), "SITE_DRAFT": site["draft"],
        "NAME": text(site["name"]), "YEAR": str(date.today().year), "CONTACT_SECTION": contact_section,
        "ROBOTS": '<meta name="robots" content="noindex, nofollow">' if site["draft"] else "",
    }
    values = common | {
        "TITLE": text(f'{site["name"]} — {site["role"]}'),
        "DESCRIPTION": text(site["intro"]),
        "CANONICAL": canonical(site.get("url", "")), "BIO": bio_html(site["bio"]),
        "SOCIAL_META": social_metadata(site.get("url", ""), site["name"], site.get("share_title", site["role"]),
                                       site["intro"], share_image_name),
        "PROJECT_COUNT": f"{len(projects):02d}",
        "PROJECTS": "".join(project_card(p, eager=i == 0) for i, p in enumerate(projects)),
        "DRAFT_BADGE": '<span class="draft-badge">Portfolio draft · artwork pending</span>' if site["draft"] else ""
    }
    (OUT / "index.html").write_text(render("index.html", values))
    for index, project in enumerate(projects):
        dest = OUT / "projects" / project["slug"]
        dest.mkdir(parents=True)
        previous = projects[(index - 1) % len(projects)]
        following = projects[(index + 1) % len(projects)]
        (dest / "index.html").write_text(project_page(project, previous, following, common))
    for asset in ("styles.css", "site.js", "project.js", "favicon.svg", "favicon.png", "apple-touch-icon.png", "Joey_Krieger_GraphicDesigner.pdf"):
        shutil.copyfile(ROOT / "assets" / asset, OUT / asset)
    shutil.copyfile(ROOT / "assets" / "share-preview.png", OUT / share_image_name)
    (OUT / ".nojekyll").touch()
    style_bytes = (OUT / "styles.css").stat().st_size
    shell_bytes = (OUT / "index.html").stat().st_size + style_bytes + (OUT / "site.js").stat().st_size
    project_script_bytes = (OUT / "project.js").stat().st_size
    page_bytes = [page.stat().st_size + style_bytes + project_script_bytes for page in (OUT / "projects").glob("*/index.html")]
    require(max([shell_bytes, *page_bytes]) < 100_000, "A page's HTML, CSS, and JavaScript exceed the 100 KB budget.")
    print(f"Built {'publish-ready site' if publish else 'local draft'}: {OUT}")
    print(f"Homepage HTML + CSS + JS: {shell_bytes:,} bytes. {len(projects)} project pages, largest shell: {max(page_bytes):,} bytes.")
    print("Responsive images are shared across pages; artwork originals are excluded from dist.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true", help="Reject drafts and missing artwork/contact before deployment.")
    args = parser.parse_args()
    try:
        build(args.publish)
    except (ValueError, KeyError, OSError, ImportError) as error:
        print(f"Build stopped: {error}", file=sys.stderr)
        sys.exit(1)
