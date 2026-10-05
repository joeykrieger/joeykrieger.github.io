"use strict";

// Load a small thumbnail only when someone previews an inspiration link.
const preview = document.querySelector(".inspiration-preview");
const previewLinks = [...document.querySelectorAll("a[data-preview-src]")];
const hoverPointer = window.matchMedia("(hover: hover) and (pointer: fine)");
let activePreviewLink = null;
let previewPointer = null;
let previewFrame = 0;

if (preview) {
  const image = preview.querySelector("img");

  function hidePreview() {
    cancelAnimationFrame(previewFrame);
    previewFrame = 0;
    preview.hidden = true;
    activePreviewLink = null;
    previewPointer = null;
  }

  function positionPreview() {
    previewFrame = 0;
    if (!activePreviewLink || preview.hidden) return;
    const width = preview.offsetWidth;
    const height = preview.offsetHeight;
    let left, top;
    if (previewPointer) {
      left = previewPointer.x + 14;
      top = previewPointer.y + 14;
      if (left + width > window.innerWidth - 12) left = previewPointer.x - width - 14;
      if (top + height > window.innerHeight - 12) top = previewPointer.y - height - 14;
    } else {
      // Keyboard focus gets a stationary preview next to the link.
      const anchor = activePreviewLink.getBoundingClientRect();
      left = anchor.left;
      top = anchor.bottom + 10;
      if (top + height > window.innerHeight - 12) top = anchor.top - height - 10;
    }
    left = Math.max(12, Math.min(left, window.innerWidth - width - 12));
    top = Math.max(12, Math.min(top, window.innerHeight - height - 12));
    preview.style.transform = `translate3d(${left}px, ${top}px, 0)`;
  }

  function queuePosition() {
    if (!previewFrame) previewFrame = requestAnimationFrame(positionPreview);
  }

  function showPreview(link, pointer = null) {
    activePreviewLink = link;
    previewPointer = pointer;
    if (image.getAttribute("src") !== link.dataset.previewSrc) image.src = link.dataset.previewSrc;
    preview.hidden = false;
    queuePosition();
  }

  for (const link of previewLinks) {
    link.addEventListener("pointerenter", event => {
      if (hoverPointer.matches) showPreview(link, { x: event.clientX, y: event.clientY });
    });
    link.addEventListener("pointermove", event => {
      if (hoverPointer.matches && activePreviewLink === link && !preview.hidden) {
        previewPointer = { x: event.clientX, y: event.clientY };
        queuePosition();
      }
    });
    link.addEventListener("pointerleave", () => {
      if (activePreviewLink !== link) return;
      if (link.matches(":focus-visible")) showPreview(link);
      else hidePreview();
    });
    link.addEventListener("focus", () => {
      if (link.matches(":focus-visible")) showPreview(link);
    });
    link.addEventListener("blur", () => {
      if (activePreviewLink === link && !(hoverPointer.matches && link.matches(":hover"))) hidePreview();
    });
    link.addEventListener("click", hidePreview);
  }
  image.addEventListener("error", hidePreview);
  document.addEventListener("keydown", event => {
    if (event.key === "Escape") hidePreview();
  });
  window.addEventListener("scroll", () => {
    if (activePreviewLink?.matches(":focus-visible") && !previewPointer) queuePosition();
    else hidePreview();
  }, { passive: true });
  window.addEventListener("resize", hidePreview);
}
