/**
 * lightbox.js — accessible image viewer.
 *
 * Opens any [data-lightbox] image, preserves the original aspect ratio,
 * traps focus, and closes on Escape, backdrop click or the close button.
 */
(function () {
  "use strict";

  var triggers = document.querySelectorAll("[data-lightbox]");
  if (!triggers.length) return;

  var overlay = document.createElement("div");
  overlay.className = "lightbox";
  overlay.setAttribute("role", "dialog");
  overlay.setAttribute("aria-modal", "true");
  overlay.setAttribute("aria-label", "이미지 확대 보기");
  overlay.setAttribute("data-open", "false");
  overlay.innerHTML =
    '<button type="button" class="lightbox__close" aria-label="닫기">' +
    '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">' +
    '<path d="M3.5 3.5l9 9M12.5 3.5l-9 9" fill="none" stroke="currentColor" ' +
    'stroke-width="1.6" stroke-linecap="round"/></svg></button>' +
    '<figure class="lightbox__figure">' +
    '<img class="lightbox__img" alt="">' +
    '<figcaption class="lightbox__caption"></figcaption>' +
    "</figure>";

  document.body.appendChild(overlay);

  var img = overlay.querySelector(".lightbox__img");
  var caption = overlay.querySelector(".lightbox__caption");
  var closeBtn = overlay.querySelector(".lightbox__close");
  var lastFocused = null;

  function open(source, text) {
    lastFocused = document.activeElement;
    img.src = source.currentSrc || source.src;
    img.alt = source.alt || "";
    caption.textContent = text || "";
    caption.hidden = !text;
    overlay.setAttribute("data-open", "true");
    document.body.classList.add("is-locked");
    closeBtn.focus();
  }

  function close() {
    overlay.setAttribute("data-open", "false");
    document.body.classList.remove("is-locked");
    if (lastFocused && typeof lastFocused.focus === "function") {
      lastFocused.focus();
    }
    // Release the decoded image once the fade-out has finished.
    window.setTimeout(function () {
      if (overlay.getAttribute("data-open") === "false") img.src = "";
    }, 320);
  }

  triggers.forEach(function (el) {
    var target = el.tagName === "IMG" ? el : el.querySelector("img");
    if (!target) return;

    var text = el.getAttribute("data-lightbox-caption") || "";

    el.setAttribute("tabindex", "0");
    el.setAttribute("role", "button");
    el.setAttribute("aria-label", (target.alt || "이미지") + " 확대 보기");
    el.classList.add("media--zoomable");

    el.addEventListener("click", function () {
      open(target, text);
    });

    el.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        open(target, text);
      }
    });
  });

  closeBtn.addEventListener("click", close);

  overlay.addEventListener("click", function (event) {
    if (event.target === overlay || event.target.closest(".lightbox__figure") === null) {
      close();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (overlay.getAttribute("data-open") !== "true") return;

    if (event.key === "Escape") {
      close();
      return;
    }

    // Only the close button is focusable inside the dialog: keep Tab on it.
    if (event.key === "Tab") {
      event.preventDefault();
      closeBtn.focus();
    }
  });
})();
