/**
 * main.js — navigation, section tracking, pointer-reactive cards,
 * theme-matched PDF links and small page utilities.
 *
 * Every feature degrades to plain HTML if its API is missing.
 */
(function () {
  "use strict";

  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------------------
     Sticky navigation — gains glass depth once the page has scrolled
     --------------------------------------------------------------------- */

  var nav = document.querySelector("[data-nav]");

  if (nav) {
    var setScrolled = function () {
      nav.setAttribute("data-scrolled", String(window.scrollY > 24));
    };
    setScrolled();
    window.addEventListener("scroll", setScrolled, { passive: true });
  }

  /* ---------------------------------------------------------------------
     Mobile menu
     --------------------------------------------------------------------- */

  var burger = document.querySelector("[data-menu-toggle]");
  var menu = document.querySelector("[data-menu]");

  if (burger && menu) {
    var setMenu = function (open, restoreFocus) {
      burger.setAttribute("aria-expanded", String(open));
      burger.setAttribute("aria-label", open ? "메뉴 닫기" : "메뉴 열기");
      menu.setAttribute("data-open", String(open));
      menu.setAttribute("aria-hidden", String(!open));
      document.body.classList.toggle("menu-open", open);

      if (open) {
        window.setTimeout(function () {
          if (burger.getAttribute("aria-expanded") !== "true") return;
          var first = menu.querySelector("a[href]");
          if (first) first.focus({ preventScroll: true });
        }, 260);
      } else if (restoreFocus) {
        burger.focus();
      }
    };

    setMenu(false, false);

    burger.addEventListener("click", function () {
      setMenu(burger.getAttribute("aria-expanded") !== "true", false);
    });

    menu.addEventListener("click", function (event) {
      if (event.target.closest("a")) setMenu(false, false);
    });

    document.addEventListener("keydown", function (event) {
      var open = burger.getAttribute("aria-expanded") === "true";
      if (event.key === "Escape" && open) {
        event.preventDefault();
        setMenu(false, true);
        return;
      }

      if (event.key !== "Tab" || !open) return;
      var items = Array.prototype.slice.call(menu.querySelectorAll("a[href]"));
      if (!items.length) return;
      var first = items[0];
      var last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 1080) setMenu(false, false);
    });

    window.addEventListener("orientationchange", function () {
      setMenu(false, false);
    });
  }

  /* ---------------------------------------------------------------------
     Active section tracking — homepage nav and case-study tables of contents
     --------------------------------------------------------------------- */

  var trackers = document.querySelectorAll("[data-spy]");

  if (trackers.length && "IntersectionObserver" in window) {
    trackers.forEach(function (group) {
      var links = Array.prototype.slice.call(group.querySelectorAll("a[href^='#']"));
      if (!links.length) return;

      var sections = links
        .map(function (link) {
          var id = link.getAttribute("href").slice(1);
          var el = id ? document.getElementById(id) : null;
          return el ? { id: id, el: el, link: link } : null;
        })
        .filter(Boolean);

      if (!sections.length) return;

      var visible = new Map();

      var setActive = function (id) {
        sections.forEach(function (entry) {
          if (entry.id === id) {
            entry.link.setAttribute("aria-current", "true");
          } else {
            entry.link.removeAttribute("aria-current");
          }
        });
      };

      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              visible.set(entry.target.id, entry.intersectionRatio);
            } else {
              visible.delete(entry.target.id);
            }
          });

          if (!visible.size) return;

          // Nearest section to the top of the reading area wins.
          var best = null;
          var bestTop = Infinity;
          visible.forEach(function (_ratio, id) {
            var el = document.getElementById(id);
            if (!el) return;
            var top = Math.abs(el.getBoundingClientRect().top - 120);
            if (top < bestTop) {
              bestTop = top;
              best = id;
            }
          });

          if (best) setActive(best);
        },
        { rootMargin: "-18% 0px -62% 0px", threshold: [0, 0.25, 0.6, 1] }
      );

      sections.forEach(function (entry) {
        observer.observe(entry.el);
      });
    });
  }

  /* ---------------------------------------------------------------------
     Pointer-reactive cards — a very small radial sheen, desktop pointers only
     --------------------------------------------------------------------- */

  var finePointer =
    window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  if (finePointer && !reduceMotion) {
    document.querySelectorAll(".card--reactive").forEach(function (card) {
      card.addEventListener(
        "pointermove",
        function (event) {
          var rect = card.getBoundingClientRect();
          card.style.setProperty(
            "--px",
            ((event.clientX - rect.left) / rect.width) * 100 + "%"
          );
          card.style.setProperty(
            "--py",
            ((event.clientY - rect.top) / rect.height) * 100 + "%"
          );
        },
        { passive: true }
      );
    });
  }

  /* ---------------------------------------------------------------------
     PDF links follow the active theme (dark deck ↔ light deck).
     Without JS the markup already points at a valid file.
     --------------------------------------------------------------------- */

  var syncPdfLinks = function (theme) {
    var wanted = theme === "light" ? "light" : "dark";
    document.querySelectorAll("a[data-pdf-variant]").forEach(function (link) {
      var href = link.getAttribute("href") || "";
      var next = href.replace(
        /(^|\/)pdf\/(dark|light)\//,
        "$1pdf/" + wanted + "/"
      );
      if (next !== href) link.setAttribute("href", next);

      var label = link.getAttribute("data-pdf-label");
      if (label) {
        link.setAttribute(
          "title",
          label + " · " + (wanted === "light" ? "화이트 모드 PDF" : "다크 모드 PDF")
        );
      }
    });
  };

  syncPdfLinks(document.documentElement.getAttribute("data-theme"));
  window.addEventListener("themechange", function (event) {
    syncPdfLinks(event.detail && event.detail.theme);
  });

  /* ---------------------------------------------------------------------
     Email and phone links copy their value instead of opening a handler.
     Without JS (or a clipboard API) the mailto:/tel: links work as-is.
     --------------------------------------------------------------------- */

  var copyToast = null;
  var copyToastTimer = 0;

  var showCopyToast = function (message) {
    if (!copyToast) {
      copyToast = document.createElement("div");
      copyToast.className = "copy-toast";
      copyToast.setAttribute("role", "status");
      document.body.appendChild(copyToast);
    }
    copyToast.textContent = message;
    copyToast.setAttribute("data-open", "true");
    window.clearTimeout(copyToastTimer);
    copyToastTimer = window.setTimeout(function () {
      copyToast.setAttribute("data-open", "false");
    }, 2200);
  };

  var bindCopyLink = function (link, title, getValue) {
    link.setAttribute("title", title);
    link.addEventListener("click", function (event) {
      if (!navigator.clipboard || !navigator.clipboard.writeText) return;
      event.preventDefault();
      navigator.clipboard.writeText(getValue()).then(
        function () {
          showCopyToast("복사되었습니다!");
        },
        function () {
          window.location.href = link.getAttribute("href");
        }
      );
    });
  };

  document.querySelectorAll('a[href^="mailto:"]').forEach(function (link) {
    bindCopyLink(link, "클릭하면 이메일 주소가 복사됩니다", function () {
      return (link.getAttribute("href") || "")
        .replace(/^mailto:/, "")
        .split("?")[0];
    });
  });

  document.querySelectorAll('a[href^="tel:"]').forEach(function (link) {
    bindCopyLink(link, "클릭하면 전화번호가 복사됩니다", function () {
      var valueEl = link.querySelector(".contact__value");
      var text = ((valueEl || link).textContent || "").trim();
      return text || (link.getAttribute("href") || "").replace(/^tel:/, "");
    });
  });

  /* Page transitions are declared in CSS (@view-transition) rather than by
     intercepting clicks here. Nothing may stand between a link and its
     navigation. */

  /* ---------------------------------------------------------------------
     Footer year
     --------------------------------------------------------------------- */

  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();
