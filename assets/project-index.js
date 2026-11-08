"use strict";

// The overview and project galleries share this document and the pinned bio.
const projectIndex = document.querySelector(".project-index");
const projectGrid = document.querySelector(".project-grid");
const projectViewer = document.querySelector(".project-viewer");
const returnLink = document.querySelector(".index-return");
const cards = [...projectGrid.querySelectorAll(".project-card")];
const projects = [...projectViewer.querySelectorAll(".project-row")];
const projectById = new Map(projects.map(project => [project.id, project]));
const cardById = new Map(cards.map(card => [card.hash.slice(1), card]));
let currentProject = null;
let lastCard = null;
let indexScrollY = 0;
let layoutFrame = 0;

function layoutGrid() {
  layoutFrame = 0;
  if (projectIndex.hidden) return;
  // Measure natural card heights, then let Grid keep their DOM/reading order.
  const heights = cards.map(card => card.getBoundingClientRect().height);
  projectGrid.classList.add("masonry-ready");
  cards.forEach((card, index) => {
    const span = Math.ceil(heights[index] / 4);
    if (card.style.gridRowEnd !== `span ${span}`) card.style.gridRowEnd = `span ${span}`;
  });
}

function queueLayout() {
  if (!layoutFrame) layoutFrame = requestAnimationFrame(layoutGrid);
}

function scrollToViewer() {
  const main = document.querySelector("main");
  const gutter = parseFloat(getComputedStyle(document.querySelector(".portfolio-layout")).paddingTop);
  const top = Math.max(0, window.scrollY + main.getBoundingClientRect().top - gutter);
  window.scrollTo({ top, behavior: "instant" });
}

function showProject(id, { focus = true } = {}) {
  const project = projectById.get(id);
  if (!project) return;
  currentProject = id;
  lastCard = cardById.get(id);
  projectIndex.hidden = true;
  projectViewer.hidden = false;
  projects.forEach(item => { item.hidden = item !== project; });
  cards.forEach(card => card.setAttribute("aria-expanded", String(card === lastCard)));
  scrollToViewer();
  if (focus) project.querySelector(".project-title").focus({ preventScroll: true });
}

function showIndex({ restore = true, focus = true } = {}) {
  currentProject = null;
  projectViewer.hidden = true;
  projectIndex.hidden = false;
  cards.forEach(card => card.setAttribute("aria-expanded", "false"));
  layoutGrid();
  if (restore) window.scrollTo({ top: indexScrollY, behavior: "instant" });
  if (focus && lastCard) lastCard.focus({ preventScroll: true });
}

function closeProject() {
  if (!currentProject) return;
  if (history.state?.fromProjectIndex) history.back();
  else {
    history.replaceState({ portfolioView: "index", indexScrollY }, "", "#projects");
    showIndex();
  }
}

for (const card of cards) {
  card.addEventListener("click", event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const id = card.hash.slice(1);
    indexScrollY = window.scrollY;
    history.replaceState({ ...history.state, portfolioView: "index", indexScrollY }, "");
    history.pushState({ portfolioView: "project", fromProjectIndex: true, indexScrollY }, "", `#${id}`);
    showProject(id);
  });
  card.querySelector("img").addEventListener("load", queueLayout);
}

returnLink.addEventListener("click", event => {
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  closeProject();
});

document.addEventListener("keydown", event => {
  if (event.key === "Escape" && currentProject) {
    event.preventDefault();
    closeProject();
  }
});

function syncLocation({ focus = true } = {}) {
  const id = location.hash.slice(1);
  indexScrollY = history.state?.indexScrollY ?? indexScrollY;
  if (projectById.has(id)) showProject(id, { focus });
  else showIndex({ restore: true, focus });
}

window.addEventListener("popstate", () => syncLocation());
window.addEventListener("hashchange", () => {
  const id = location.hash.slice(1);
  if (projectById.has(id) && currentProject !== id) showProject(id);
  else if (id === "projects" && currentProject) showIndex();
});

if ("ResizeObserver" in window) {
  const observer = new ResizeObserver(queueLayout);
  observer.observe(projectGrid);
  cards.forEach(card => observer.observe(card));
} else window.addEventListener("resize", queueLayout);

history.scrollRestoration = "manual";
const initialId = location.hash.slice(1);
if (projectById.has(initialId)) showProject(initialId, { focus: false });
else showIndex({ restore: false, focus: false });
