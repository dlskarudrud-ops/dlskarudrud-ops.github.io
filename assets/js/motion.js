/**
 * motion.js — content reveal on scroll.
 *
 * Reveals are a hierarchy cue, not decoration: an element moves 16px and fades
 * once, then never animates again. Anything already on screen at load reveals
 * immediately so nothing important is ever hidden waiting for a scroll.
 */
(function () {
  "use strict";

  var targets = document.querySelectorAll("[data-reveal]");
  if (!targets.length) return;

  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var revealAll = function () {
    targets.forEach(function (el) {
      el.classList.add("is-revealed");
    });
  };

  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealAll();
    return;
  }

  // Stagger siblings inside a shared [data-reveal-group] container.
  document.querySelectorAll("[data-reveal-group]").forEach(function (group) {
    var step = parseInt(group.getAttribute("data-reveal-group"), 10) || 70;
    Array.prototype.slice
      .call(group.querySelectorAll(":scope > [data-reveal]"))
      .forEach(function (el, index) {
        el.style.setProperty("--reveal-delay", Math.min(index, 6) * step + "ms");
      });
  });

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-revealed");
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.06 }
  );

  targets.forEach(function (el) {
    observer.observe(el);
  });

  // Safety net: if anything is still hidden after the page settles, show it.
  window.setTimeout(function () {
    targets.forEach(function (el) {
      var rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight) el.classList.add("is-revealed");
    });
  }, 1200);
})();
