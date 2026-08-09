/**
 * ambient-scene.js — fixed full-viewport GLSL light field for the whole site.
 *
 * One low-resolution draw call remains behind every section while scroll
 * progress slowly repositions the broad lights. Home and page-hero ribbons
 * stay separate foreground signatures; this layer supplies continuity.
 */

import {
  AMBIENT_PALETTES,
  createAmbient,
} from "./materials.js?v=15";

const THREE_URL = "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js";
const motionQuery = window.matchMedia
  ? window.matchMedia("(prefers-reduced-motion: reduce)")
  : null;
const forcedColorsQuery = window.matchMedia
  ? window.matchMedia("(forced-colors: active)")
  : null;
const compactHeightQuery = window.matchMedia
  ? window.matchMedia("(max-height: 260px)")
  : null;

function supportsWebGL2() {
  // Three r169 is WebGL2-only. Avoid opening a throwaway probe context;
  // renderer construction below remains the definitive capability test.
  return Boolean(window.WebGL2RenderingContext);
}

function boundedPixelRatio(width, height, cap, maxPixels) {
  const budgetRatio = Math.sqrt(
    maxPixels / Math.max(1, width * height)
  );
  return Math.max(
    0.2,
    Math.min(window.devicePixelRatio || 1, cap, budgetRatio)
  );
}

async function init() {
  const connection = navigator.connection || navigator.mozConnection;
  if (
    (connection && connection.saveData) ||
    (forcedColorsQuery && forcedColorsQuery.matches) ||
    (compactHeightQuery && compactHeightQuery.matches) ||
    !supportsWebGL2()
  ) return;

  let THREE;
  try {
    THREE = await import(/* @vite-ignore */ THREE_URL);
  } catch (_error) {
    return;
  }

  const host = document.createElement("div");
  host.className = "site-atmosphere";
  host.setAttribute("aria-hidden", "true");
  document.body.prepend(host);

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: false,
      powerPreference: "low-power",
      failIfMajorPerformanceCaveat: false,
    });
  } catch (_error) {
    host.remove();
    return;
  }

  renderer.setClearColor(0x000000, 0);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.className = "site-atmosphere__canvas";
  renderer.domElement.setAttribute("aria-hidden", "true");
  host.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.Camera();
  const ambient = createAmbient(THREE);
  scene.add(ambient);
  const foreground = document.querySelector(".hero, .page-hero");

  let reduceMotion = Boolean(motionQuery && motionQuery.matches);
  let forcedColors = false;
  let tabVisible = document.visibilityState !== "hidden";
  let foregroundVisible = Boolean(foreground && "IntersectionObserver" in window);
  let running = false;
  let disposed = false;
  let contextLost = false;
  let hasRendered = false;
  let frame = 0;
  let staticFrame = 0;
  let scrollFrame = 0;
  let elapsed = 11.0;
  let scrollProgress = 0;
  let lastFrameTime = 0;
  let rendererDpr = 0;
  let frameStep = 1000 / (window.innerWidth < 720 ? 18 : 24);
  const clock = new THREE.Clock(false);

  const current = {
    warm: new THREE.Color(),
    cool: new THREE.Color(),
    neutral: new THREE.Color(),
    opacity: 0,
    exposure: 1,
  };
  const target = {
    warm: new THREE.Color(),
    cool: new THREE.Color(),
    neutral: new THREE.Color(),
    opacity: 0,
    exposure: 1,
  };

  const damp = (a, b, k) => a + (b - a) * k;

  function copyTarget() {
    current.warm.copy(target.warm);
    current.cool.copy(target.cool);
    current.neutral.copy(target.neutral);
    current.opacity = target.opacity;
    current.exposure = target.exposure;
  }

  function readTheme(firstPaint) {
    const name =
      document.documentElement.getAttribute("data-theme") === "light"
        ? "light"
        : "dark";
    const palette = AMBIENT_PALETTES[name];
    target.warm.setRGB(...palette.warm);
    target.cool.setRGB(...palette.cool);
    target.neutral.setRGB(...palette.neutral);
    target.opacity = palette.opacity;
    target.exposure = palette.exposure;
    if (firstPaint || reduceMotion) copyTarget();
  }

  function resize() {
    if (disposed || contextLost) return;
    const width = Math.max(1, window.innerWidth);
    const height = Math.max(1, window.innerHeight);
    const nextDpr = boundedPixelRatio(
      width,
      height,
      width < 720 ? 0.55 : 0.7,
      1800000
    );
    if (Math.abs(nextDpr - rendererDpr) > 0.01) {
      rendererDpr = nextDpr;
      renderer.setPixelRatio(rendererDpr);
    }
    frameStep = 1000 / (width < 720 ? 18 : 24);
    renderer.setSize(width, height, false);
    ambient.material.uniforms.uAspect.value = width / height;
  }

  function draw(delta) {
    if (disposed || contextLost || forcedColors) return;
    const k = reduceMotion ? 1 : Math.min(1, Math.max(delta, 1 / 120) * 2.5);
    current.warm.lerp(target.warm, k);
    current.cool.lerp(target.cool, k);
    current.neutral.lerp(target.neutral, k);
    current.opacity = damp(current.opacity, target.opacity, k);
    current.exposure = damp(current.exposure, target.exposure, k);

    const uniforms = ambient.material.uniforms;
    uniforms.uTime.value = elapsed;
    uniforms.uScroll.value = scrollProgress;
    uniforms.uWarm.value.copy(current.warm);
    uniforms.uCool.value.copy(current.cool);
    uniforms.uNeutral.value.copy(current.neutral);
    uniforms.uOpacity.value = current.opacity;
    renderer.toneMappingExposure = current.exposure;

    renderer.render(scene, camera);
    if (!hasRendered) {
      hasRendered = true;
      host.setAttribute("data-ready", "true");
    }
  }

  function render(now) {
    if (!running) return;
    frame = requestAnimationFrame(render);
    if (lastFrameTime) {
      const frameDelta = now - lastFrameTime;
      if (frameDelta < frameStep) return;
      lastFrameTime = now - (frameDelta % frameStep);
    } else {
      lastFrameTime = now;
    }
    const delta = Math.min(clock.getDelta() || 1 / 24, 0.08);
    elapsed += delta;
    draw(delta);
  }

  function renderStatic() {
    cancelAnimationFrame(staticFrame);
    staticFrame = requestAnimationFrame(() => draw(1 / 60));
  }

  function sync() {
    const shouldRun =
      tabVisible &&
      !foregroundVisible &&
      !forcedColors &&
      !contextLost &&
      !disposed;
    if (reduceMotion) {
      if (running) {
        running = false;
        cancelAnimationFrame(frame);
        clock.stop();
      }
      if (shouldRun) renderStatic();
      return;
    }
    if (shouldRun && !running) {
      running = true;
      lastFrameTime = 0;
      clock.start();
      frame = requestAnimationFrame(render);
    } else if (!shouldRun && running) {
      running = false;
      cancelAnimationFrame(frame);
      clock.stop();
    }
  }

  function updateScroll() {
    scrollFrame = 0;
    const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    scrollProgress = Math.min(1, Math.max(0, window.scrollY / max));
    if (reduceMotion) renderStatic();
  }

  function onScroll() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScroll);
  }

  function onThemeChange() {
    readTheme(false);
    if (reduceMotion || foregroundVisible) {
      copyTarget();
      renderStatic();
    }
  }

  function onMotionChange(event) {
    reduceMotion = event.matches;
    if (reduceMotion) copyTarget();
    sync();
  }

  function onForcedColorsChange(event) {
    forcedColors = event.matches;
    if (forcedColors) {
      host.removeAttribute("data-ready");
      sync();
      return;
    }
    hasRendered = false;
    renderStatic();
    sync();
  }

  function onVisibilityChange() {
    tabVisible = document.visibilityState !== "hidden";
    sync();
  }

  function onContextLost(event) {
    event.preventDefault();
    contextLost = true;
    hasRendered = false;
    host.removeAttribute("data-ready");
    sync();
  }

  function onContextRestored() {
    contextLost = false;
    resize();
    sync();
  }

  readTheme(true);
  resize();
  updateScroll();
  draw(1 / 60);
  sync();

  window.addEventListener("resize", resize, { passive: true });
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("themechange", onThemeChange);
  document.addEventListener("visibilitychange", onVisibilityChange);
  renderer.domElement.addEventListener("webglcontextlost", onContextLost);
  renderer.domElement.addEventListener("webglcontextrestored", onContextRestored);
  if (motionQuery && motionQuery.addEventListener) {
    motionQuery.addEventListener("change", onMotionChange);
  }
  if (forcedColorsQuery && forcedColorsQuery.addEventListener) {
    forcedColorsQuery.addEventListener("change", onForcedColorsChange);
  }

  let foregroundObserver = null;
  if (foreground && "IntersectionObserver" in window) {
    foregroundObserver = new IntersectionObserver(
      ([entry]) => {
        foregroundVisible = Boolean(entry && entry.isIntersecting);
        if (foregroundVisible) renderStatic();
        sync();
      },
      { threshold: 0 }
    );
    foregroundObserver.observe(foreground);
  }

  function stop() {
    running = false;
    cancelAnimationFrame(frame);
    cancelAnimationFrame(staticFrame);
    cancelAnimationFrame(scrollFrame);
    clock.stop();
  }

  function dispose() {
    if (disposed) return;
    disposed = true;
    stop();
    if (foregroundObserver) foregroundObserver.disconnect();
    window.removeEventListener("resize", resize);
    window.removeEventListener("scroll", onScroll);
    window.removeEventListener("themechange", onThemeChange);
    window.removeEventListener("pagehide", onPageHide);
    window.removeEventListener("pageshow", onPageShow);
    document.removeEventListener("visibilitychange", onVisibilityChange);
    renderer.domElement.removeEventListener("webglcontextlost", onContextLost);
    renderer.domElement.removeEventListener("webglcontextrestored", onContextRestored);
    if (motionQuery && motionQuery.removeEventListener) {
      motionQuery.removeEventListener("change", onMotionChange);
    }
    if (forcedColorsQuery && forcedColorsQuery.removeEventListener) {
      forcedColorsQuery.removeEventListener("change", onForcedColorsChange);
    }
    ambient.geometry.dispose();
    ambient.material.dispose();
    renderer.dispose();
  }

  function onPageHide(event) {
    if (event.persisted) {
      stop();
      return;
    }
    dispose();
  }

  function onPageShow(event) {
    if (!event.persisted || disposed) return;
    tabVisible = document.visibilityState !== "hidden";
    if (foreground) {
      const rect = foreground.getBoundingClientRect();
      foregroundVisible = rect.bottom > 0 && rect.top < window.innerHeight;
    }
    resize();
    updateScroll();
    sync();
  }

  window.addEventListener("pagehide", onPageHide);
  window.addEventListener("pageshow", onPageShow);
}

init();
