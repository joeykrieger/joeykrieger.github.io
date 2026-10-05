"use strict";

// Native details provides an inline description if the modal is unavailable.
const details = document.querySelector(".project-details");
const dialog = document.querySelector(".project-dialog");

if (details && dialog && typeof dialog.showModal === "function") {
  const trigger = details.querySelector("summary");
  const card = dialog.querySelector(".project-dialog-card");
  const story = details.querySelector(".project-story");
  const close = dialog.querySelector(".project-dialog-close");
  let backdropPressed = false;

  dialog.querySelector(".project-dialog-story").append(story);
  trigger.setAttribute("aria-haspopup", "dialog");
  trigger.setAttribute("aria-controls", dialog.id);

  trigger.addEventListener("click", event => {
    event.preventDefault();
    dialog.showModal();
    document.documentElement.classList.add("project-modal-open");
    card.scrollTop = 0;
  });

  close.addEventListener("click", () => dialog.close());
  dialog.addEventListener("pointerdown", event => {
    backdropPressed = event.target === dialog;
  });
  dialog.addEventListener("click", event => {
    if (backdropPressed && event.target === dialog) dialog.close();
  });
  // Escape uses the dialog's native cancel behavior, focus trap, and close event.
  dialog.addEventListener("close", () => {
    document.documentElement.classList.remove("project-modal-open");
    trigger.focus({ preventScroll: true });
  });
}
