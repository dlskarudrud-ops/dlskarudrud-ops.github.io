/* Tower UI mockup — opens the reward / effect popups over the base screen.
   Panels are cloned from the documentation sections below, so the markup
   lives in one place. Without JS the static popup sections still show. */
(function () {
  "use strict";
  var overlay = document.querySelector("[data-ui-overlay]");
  if (!overlay) return;
  var slot = overlay.querySelector(".ui-live-overlay__slot");
  var sources = {
    effect: document.querySelector(".ui-panel--effect"),
    reward: document.querySelector(".ui-panel--reward")
  };
  var lastTrigger = null;

  function onKey(event) {
    if (event.key === "Escape") close();
  }

  function open(kind, trigger) {
    var source = sources[kind];
    if (!source) return;
    slot.innerHTML = "";
    var panel = source.cloneNode(true);
    panel.classList.add("is-live");
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-modal", "true");
    var head = panel.querySelector(".ui-panel__head");
    var closer = head && head.lastElementChild;
    if (closer) {
      closer.setAttribute("data-ui-close", "");
      closer.setAttribute("role", "button");
      closer.setAttribute("tabindex", "0");
      closer.setAttribute("aria-label", "팝업 닫기");
    }
    slot.appendChild(panel);
    overlay.hidden = false;
    lastTrigger = trigger;
    if (closer) closer.focus();
    document.addEventListener("keydown", onKey);
  }

  function close() {
    if (overlay.hidden) return;
    overlay.hidden = true;
    slot.innerHTML = "";
    document.removeEventListener("keydown", onKey);
    if (lastTrigger) lastTrigger.focus();
  }

  document.querySelectorAll("[data-ui-open]").forEach(function (button) {
    button.addEventListener("click", function () {
      open(button.getAttribute("data-ui-open"), button);
    });
  });

  overlay.addEventListener("click", function (event) {
    if (event.target.closest("[data-ui-close]")) close();
  });
  overlay.addEventListener("keydown", function (event) {
    if ((event.key === "Enter" || event.key === " ") && event.target.closest("[data-ui-close]")) {
      event.preventDefault();
      close();
    }
  });
})();
