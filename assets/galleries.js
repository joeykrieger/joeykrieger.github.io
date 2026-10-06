"use strict";

// Each project owns its current image. Keep the frame and scroll position steady.
for (const gallery of document.querySelectorAll(".gallery")) {
  const slides = JSON.parse(gallery.querySelector(".gallery-data").textContent);
  if (slides.length < 2) continue;
  const stage = gallery.querySelector(".gallery-stage");
  const image = gallery.querySelector(".gallery-image");
  const caption = gallery.querySelector(".gallery-caption");
  const status = gallery.querySelector(".gallery-status");
  const previous = gallery.querySelector(".gallery-prev");
  const next = gallery.querySelector(".gallery-next");
  let displayedIndex = 0;
  let requestedIndex = 0;
  let requestId = 0;
  let swipeStart = null;
  let suppressClickUntil = 0;

  async function move(step) {
    requestedIndex = (requestedIndex + step + slides.length) % slides.length;
    const targetIndex = requestedIndex;
    const thisRequest = ++requestId;
    const slide = slides[targetIndex];
    stage.classList.add("is-loading");
    gallery.setAttribute("aria-busy", "true");
    status.textContent = "";
    try {
      const incoming = new Image();
      incoming.decoding = "async";
      incoming.sizes = image.sizes;
      incoming.srcset = slide.srcset;
      incoming.src = slide.src;
      await incoming.decode();
      if (thisRequest !== requestId) return;
      image.width = slide.width;
      image.height = slide.height;
      image.alt = slide.alt;
      image.srcset = slide.srcset;
      image.src = slide.src;
      image.loading = "eager";
      caption.textContent = slide.caption;
      caption.hidden = !slide.caption;
      displayedIndex = targetIndex;
      status.textContent = slide.alt;
    } catch {
      if (thisRequest !== requestId) return;
      requestedIndex = displayedIndex;
      status.textContent = "This image couldn’t load. Please try again.";
    } finally {
      if (thisRequest === requestId) {
        stage.classList.remove("is-loading");
        gallery.removeAttribute("aria-busy");
      }
    }
  }

  previous.addEventListener("click", () => {
    if (performance.now() >= suppressClickUntil) move(-1);
  });
  next.addEventListener("click", () => {
    if (performance.now() >= suppressClickUntil) move(1);
  });
  gallery.addEventListener("keydown", event => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    move(event.key === "ArrowLeft" ? -1 : 1);
  });

  stage.addEventListener("pointerdown", event => {
    if (event.pointerType !== "touch" || !event.isPrimary) return;
    swipeStart = { x: event.clientX, y: event.clientY, id: event.pointerId };
  });
  stage.addEventListener("pointerup", event => {
    if (!swipeStart || swipeStart.id !== event.pointerId) return;
    const dx = event.clientX - swipeStart.x;
    const dy = event.clientY - swipeStart.y;
    swipeStart = null;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.4) {
      suppressClickUntil = performance.now() + 450;
      move(dx < 0 ? 1 : -1);
    }
  });
  stage.addEventListener("pointercancel", () => { swipeStart = null; });
  gallery.classList.add("gallery-ready");
}
