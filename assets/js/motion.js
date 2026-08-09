/**
 * motion.js — progressive content reveals and user-driven motion graphics.
 *
 * The script adds the class that enables hidden reveal states. If it fails,
 * content stays visible. Reduced-motion and forced-colors can change while
 * the page is open; both stop scroll transforms and reveal all content.
 */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("motion-ready");

  var motionQuery = window.matchMedia
    ? window.matchMedia("(prefers-reduced-motion: reduce)")
    : null;
  var forcedColorsQuery = window.matchMedia
    ? window.matchMedia("(forced-colors: active)")
    : null;
  var reduceMotion = Boolean(motionQuery && motionQuery.matches);
  var forcedColors = Boolean(forcedColorsQuery && forcedColorsQuery.matches);
  var targets = document.querySelectorAll("[data-reveal]");
  var revealObserver = null;

  var motionDisabled = function () {
    return reduceMotion || forcedColors;
  };

  var revealAll = function () {
    targets.forEach(function (el) {
      el.classList.add("is-revealed");
    });
  };

  var prepareReveals = function () {
    if (!targets.length) return;
    if (motionDisabled() || !("IntersectionObserver" in window)) {
      revealAll();
      return;
    }

    document.querySelectorAll("[data-reveal-group]").forEach(function (group) {
      var step = parseInt(group.getAttribute("data-reveal-group"), 10) || 70;
      Array.prototype.slice
        .call(group.querySelectorAll(":scope > [data-reveal]"))
        .forEach(function (el, index) {
          el.style.setProperty("--reveal-delay", Math.min(index, 6) * step + "ms");
        });
    });

    revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-revealed");
          revealObserver.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.06 }
    );

    targets.forEach(function (el) {
      revealObserver.observe(el);
    });

    window.setTimeout(function () {
      targets.forEach(function (el) {
        var rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight) el.classList.add("is-revealed");
      });
    }, 1200);
  };

  prepareReveals();

  var hero = document.querySelector(".hero, .page-hero");
  var heroVisual = document.querySelector(".page-hero__visual img");
  var motionFrame = 0;
  var motionActive = false;

  var clamp = function (value, min, max) {
    return Math.min(max, Math.max(min, value));
  };

  var updateMotion = function () {
    motionFrame = 0;

    var pageMax = Math.max(
      1,
      document.documentElement.scrollHeight - window.innerHeight
    );
    root.style.setProperty(
      "--page-progress",
      clamp(window.scrollY / pageMax, 0, 1).toFixed(4)
    );

    if (hero) {
      var heroRect = hero.getBoundingClientRect();
      var heroProgress = clamp(
        -heroRect.top / Math.max(1, heroRect.height),
        0,
        1
      );
      hero.style.setProperty(
        "--hero-copy-shift",
        (-18 * heroProgress).toFixed(2) + "px"
      );
      hero.style.setProperty(
        "--hero-panel-shift",
        (13 * heroProgress).toFixed(2) + "px"
      );
      hero.style.setProperty(
        "--hero-rail-shift",
        (-7 * heroProgress).toFixed(2) + "px"
      );
      hero.style.setProperty(
        "--hero-atmosphere-shift",
        (22 * heroProgress).toFixed(2) + "px"
      );
    }

    if (heroVisual) {
      var visualRect = heroVisual.parentElement.getBoundingClientRect();
      var visible =
        visualRect.bottom > 0 && visualRect.top < window.innerHeight;
      if (visible) {
        var visualCenter = visualRect.top + visualRect.height / 2;
        var visualProgress = clamp(
          (window.innerHeight / 2 - visualCenter) / window.innerHeight,
          -0.5,
          0.5
        );
        heroVisual.style.setProperty(
          "--visual-shift",
          (visualProgress * 18).toFixed(2) + "px"
        );
      }
    }
  };

  var queueMotion = function () {
    if (motionFrame) return;
    motionFrame = requestAnimationFrame(updateMotion);
  };

  var resetMotion = function () {
    root.style.removeProperty("--page-progress");
    if (hero) {
      hero.style.removeProperty("--hero-copy-shift");
      hero.style.removeProperty("--hero-panel-shift");
      hero.style.removeProperty("--hero-rail-shift");
      hero.style.removeProperty("--hero-atmosphere-shift");
    }
    if (heroVisual) heroVisual.style.removeProperty("--visual-shift");
  };

  var startMotion = function () {
    if (motionActive || motionDisabled()) return;
    motionActive = true;
    window.addEventListener("scroll", queueMotion, { passive: true });
    window.addEventListener("resize", queueMotion, { passive: true });
    updateMotion();
  };

  var stopMotion = function () {
    if (motionFrame) cancelAnimationFrame(motionFrame);
    motionFrame = 0;
    if (motionActive) {
      window.removeEventListener("scroll", queueMotion);
      window.removeEventListener("resize", queueMotion);
      motionActive = false;
    }
    resetMotion();
  };

  var syncPreferences = function () {
    if (motionDisabled()) {
      if (revealObserver) {
        revealObserver.disconnect();
        revealObserver = null;
      }
      revealAll();
      stopMotion();
    } else {
      startMotion();
    }
  };

  var onMotionChange = function (event) {
    reduceMotion = event.matches;
    syncPreferences();
  };

  var onForcedColorsChange = function (event) {
    forcedColors = event.matches;
    syncPreferences();
  };

  if (motionQuery && motionQuery.addEventListener) {
    motionQuery.addEventListener("change", onMotionChange);
  }
  if (forcedColorsQuery && forcedColorsQuery.addEventListener) {
    forcedColorsQuery.addEventListener("change", onForcedColorsChange);
  }

  startMotion();
})();
