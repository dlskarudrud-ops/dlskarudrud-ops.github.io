/**
 * theme.js — light / dark theme controller.
 *
 * The initial theme is resolved by a tiny inline script in <head> so the page
 * never paints with the wrong theme. This file only owns the toggle, the
 * persistence rule, and the `themechange` event other modules listen to.
 */
(function () {
  "use strict";

  var STORAGE_KEY = "theme";
  var root = document.documentElement;

  function current() {
    return root.getAttribute("data-theme") === "light" ? "light" : "dark";
  }

  function apply(theme, persist) {
    root.setAttribute("data-theme", theme);

    if (persist) {
      try {
        localStorage.setItem(STORAGE_KEY, theme);
      } catch (err) {
        /* private mode — the session still works, it just will not persist */
      }
    }

    var nextLabel = theme === "dark" ? "화이트 모드" : "다크 모드";

    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(theme === "dark"));
      btn.setAttribute("aria-label", nextLabel + "로 전환");

      // Labelled switches spell out the mode they will switch to.
      var label = btn.querySelector("[data-theme-label]");
      if (label) label.textContent = nextLabel;
    });

    window.dispatchEvent(
      new CustomEvent("themechange", { detail: { theme: theme } })
    );
  }

  document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      apply(current() === "dark" ? "light" : "dark", true);
    });
  });

  // Follow the OS only while the visitor has not made an explicit choice.
  var stored = null;
  try {
    stored = localStorage.getItem(STORAGE_KEY);
  } catch (err) {
    stored = null;
  }

  if (!stored && window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    var onChange = function (event) {
      apply(event.matches ? "dark" : "light", false);
    };
    if (typeof mq.addEventListener === "function") {
      mq.addEventListener("change", onChange);
    } else if (typeof mq.addListener === "function") {
      mq.addListener(onChange);
    }
  }

  // Sync the toggle's accessible state with whatever the inline script chose.
  apply(current(), false);
})();
