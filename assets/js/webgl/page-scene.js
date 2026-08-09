/**
 * page-scene.js — lightweight GLSL atmosphere for resumes, documents and
 * case-study heroes. It reuses the homepage optical material at roughly half
 * intensity and a lower geometry tier so long-form reading remains dominant.
 */

import {
  PALETTES,
  STEEL,
  createVolume,
  createField,
} from "./materials.js?v=15";

const THREE_URL = "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js";
const hero = document.querySelector(".page-hero");
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
  return Boolean(window.WebGL2RenderingContext);
}

function boundedPixelRatio(width, height, cap, maxPixels) {
  const budgetRatio = Math.sqrt(
    maxPixels / Math.max(1, width * height)
  );
  return Math.max(
    0.35,
    Math.min(window.devicePixelRatio || 1, cap, budgetRatio)
  );
}

function resolveTier() {
  const connection = navigator.connection || navigator.mozConnection;
  if (connection && connection.saveData) return null;

  const width = window.innerWidth;
  const cores = navigator.hardwareConcurrency || 8;
  const memory = navigator.deviceMemory || 8;
  if (width < 720 || cores <= 4 || memory <= 4) {
    return { segments: 32, dpr: 1, fps: 24 };
  }
  if (width < 1200 || cores <= 6) {
    return { segments: 48, dpr: 1.2, fps: 30 };
  }
  return { segments: 64, dpr: 1.35, fps: 45 };
}

async function init() {
  const tier = resolveTier();
  if (
    !hero ||
    !tier ||
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
  host.className = "page-hero__atmosphere";
  host.setAttribute("aria-hidden", "true");
  hero.prepend(host);

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
  renderer.toneMappingExposure = 0.96;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.className = "page-hero__canvas";
  renderer.domElement.setAttribute("aria-hidden", "true");
  host.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 40);
  const volume = createVolume(THREE, tier.segments);
  const field = createField(THREE);

  // Page heroes use a broader, more face-on veil than the homepage. A steep
  // grazing angle turns low-frequency folds into razor-thin lines on short or
  // narrow viewports, which reads as a torn canvas rather than soft glass.
  volume.material.uniforms.uAmplitude.value = 0.54;
  volume.material.uniforms.uScale.value = 0.21;
  volume.scale.setScalar(0.9);
  volume.position.set(0.94, -0.06, 0);
  volume.rotation.set(-0.88, 0.22, -0.42);
  field.position.set(0.8, 0.12, -3.5);
  scene.add(field, volume);

  let reduceMotion = Boolean(motionQuery && motionQuery.matches);
  let forcedColors = false;
  let elapsed = 7.5;
  let scrollProgress = 0;
  let heroVisible = true;
  let tabVisible = document.visibilityState !== "hidden";
  let running = false;
  let disposed = false;
  let contextLost = false;
  let frame = 0;
  let staticFrame = 0;
  let scrollFrame = 0;
  let lastFrameTime = 0;
  let hasRendered = false;
  let rendererDpr = 0;
  let frameStep = 1000 / tier.fps;
  const clock = new THREE.Clock(false);

  const current = {
    deep: new THREE.Color(),
    light: new THREE.Color(),
    tint: new THREE.Color(),
    prismA: new THREE.Color(),
    prismB: new THREE.Color(),
    glow: new THREE.Color(),
    shade: new THREE.Color(),
    opacity: 0,
    fieldOpacity: 0,
    fresnel: 2.7,
    specular: 0.45,
    exposure: 1,
  };

  const target = {
    deep: new THREE.Color(),
    light: new THREE.Color(),
    tint: new THREE.Color(),
    prismA: new THREE.Color(),
    prismB: new THREE.Color(),
    glow: new THREE.Color(),
    shade: new THREE.Color(),
    opacity: 0,
    fieldOpacity: 0,
    fresnel: 2.7,
    specular: 0.45,
    exposure: 1,
  };

  const damp = (a, b, k) => a + (b - a) * k;

  function copyTarget() {
    current.deep.copy(target.deep);
    current.light.copy(target.light);
    current.tint.copy(target.tint);
    current.prismA.copy(target.prismA);
    current.prismB.copy(target.prismB);
    current.glow.copy(target.glow);
    current.shade.copy(target.shade);
    current.opacity = target.opacity;
    current.fieldOpacity = target.fieldOpacity;
    current.fresnel = target.fresnel;
    current.specular = target.specular;
    current.exposure = target.exposure;
  }

  function readTheme(firstPaint) {
    const root = document.documentElement;
    const name = root.getAttribute("data-theme") === "light" ? "light" : "dark";
    const palette = PALETTES[name];
    const accent = root.getAttribute("data-accent") === "steel" ? STEEL[name] : null;

    target.deep.setRGB(...palette.volume.deep);
    target.light.setRGB(...palette.volume.light);
    target.tint.setRGB(...(accent ? accent.tint : palette.volume.tint));
    target.prismA.setRGB(...(accent ? accent.prismA : palette.volume.prismA));
    target.prismB.setRGB(...(accent ? accent.prismB : palette.volume.prismB));
    target.glow.setRGB(...(accent ? accent.glow : palette.field.glow));
    target.shade.setRGB(...palette.field.shade);
    target.opacity = palette.volume.opacity * (name === "light" ? 0.78 : 0.68);
    target.fieldOpacity = palette.field.opacity * (name === "light" ? 0.54 : 0.3);
    // A lower power spreads the dark-mode rim over the face-on page veil.
    // The homepage keeps the narrow cinematic edge; document pages need one
    // continuous glass body rather than isolated contour lines.
    target.fresnel = name === "light" ? palette.volume.fresnel : 1.85;
    target.specular = palette.volume.specular * 0.78;
    target.exposure = name === "light" ? 0.86 : 0.96;

    if (firstPaint || reduceMotion) copyTarget();
  }

  function resize() {
    if (disposed || contextLost) return;
    const rect = host.getBoundingClientRect();
    const width = Math.max(1, Math.round(rect.width));
    const height = Math.max(1, Math.round(rect.height));
    const nextDpr = boundedPixelRatio(width, height, tier.dpr, 2000000);
    if (Math.abs(nextDpr - rendererDpr) > 0.01) {
      rendererDpr = nextDpr;
      renderer.setPixelRatio(rendererDpr);
    }
    const responsiveFps = window.innerWidth < 720
      ? Math.min(tier.fps, 24)
      : tier.fps;
    frameStep = 1000 / responsiveFps;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  function draw(delta) {
    if (disposed || contextLost || forcedColors) return;
    const k = reduceMotion ? 1 : Math.min(1, Math.max(delta, 1 / 120) * 3.4);
    const recede = 1 - scrollProgress * 0.72;

    current.deep.lerp(target.deep, k);
    current.light.lerp(target.light, k);
    current.tint.lerp(target.tint, k);
    current.prismA.lerp(target.prismA, k);
    current.prismB.lerp(target.prismB, k);
    current.glow.lerp(target.glow, k);
    current.shade.lerp(target.shade, k);
    current.opacity = damp(current.opacity, target.opacity * recede, k);
    current.fieldOpacity = damp(current.fieldOpacity, target.fieldOpacity * recede, k);
    current.fresnel = damp(current.fresnel, target.fresnel, k);
    current.specular = damp(current.specular, target.specular, k);
    current.exposure = damp(current.exposure, target.exposure, k);
    renderer.toneMappingExposure = current.exposure;

    const vu = volume.material.uniforms;
    vu.uTime.value = elapsed;
    vu.uDeep.value.copy(current.deep);
    vu.uLight.value.copy(current.light);
    vu.uTint.value.copy(current.tint);
    vu.uPrismA.value.copy(current.prismA);
    vu.uPrismB.value.copy(current.prismB);
    vu.uOpacity.value = current.opacity;
    vu.uFresnelPower.value = current.fresnel;
    vu.uSpecular.value = current.specular;

    const fu = field.material.uniforms;
    fu.uTime.value = elapsed;
    fu.uGlow.value.copy(current.glow);
    fu.uShade.value.copy(current.shade);
    fu.uOpacity.value = current.fieldOpacity;

    camera.position.x = 0.06 + Math.sin(elapsed * 0.035) * 0.08;
    camera.position.y = -0.02 + Math.cos(elapsed * 0.028) * 0.06;
    camera.position.z = 4.0 + scrollProgress * 0.44;
    camera.lookAt(0.62, 0.02, 0);
    volume.rotation.z = -0.42 + Math.sin(elapsed * 0.018) * 0.014;
    volume.rotation.x = -0.88 + Math.cos(elapsed * 0.016) * 0.012;

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
    const delta = Math.min(clock.getDelta() || 1 / tier.fps, 0.05);
    elapsed += delta;
    draw(delta);
  }

  function renderStatic() {
    cancelAnimationFrame(staticFrame);
    staticFrame = requestAnimationFrame(() => draw(1 / 60));
  }

  function sync() {
    const shouldRun =
      heroVisible && tabVisible && !forcedColors && !contextLost && !disposed;
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
    const rect = hero.getBoundingClientRect();
    const height = rect.height || 1;
    scrollProgress = Math.min(1, Math.max(0, -rect.top / height));
    if (reduceMotion && heroVisible) renderStatic();
  }

  function onScroll() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScroll);
  }

  function onThemeChange() {
    readTheme(false);
    if (reduceMotion) renderStatic();
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

  let resizeObserver = null;
  if ("ResizeObserver" in window) {
    resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(host);
  } else {
    window.addEventListener("resize", resize);
  }

  let visibilityObserver = null;
  if ("IntersectionObserver" in window) {
    visibilityObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          heroVisible = entry.isIntersecting;
          sync();
        });
      },
      { threshold: 0 }
    );
    visibilityObserver.observe(hero);
  }

  document.addEventListener("visibilitychange", onVisibilityChange);
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("themechange", onThemeChange);
  renderer.domElement.addEventListener("webglcontextlost", onContextLost);
  renderer.domElement.addEventListener("webglcontextrestored", onContextRestored);
  if (motionQuery && motionQuery.addEventListener) {
    motionQuery.addEventListener("change", onMotionChange);
  }
  if (forcedColorsQuery && forcedColorsQuery.addEventListener) {
    forcedColorsQuery.addEventListener("change", onForcedColorsChange);
  }

  updateScroll();
  draw(1 / 60);
  sync();

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
    if (resizeObserver) resizeObserver.disconnect();
    if (visibilityObserver) visibilityObserver.disconnect();
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
    volume.geometry.dispose();
    volume.material.dispose();
    field.geometry.dispose();
    field.material.dispose();
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
    const rect = hero.getBoundingClientRect();
    heroVisible = rect.bottom > 0 && rect.top < window.innerHeight;
    resize();
    updateScroll();
    sync();
  }

  window.addEventListener("pagehide", onPageHide);
  window.addEventListener("pageshow", onPageShow);
}

init();
