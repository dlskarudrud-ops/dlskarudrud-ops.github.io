/**
 * scene.js — hero atmosphere lifecycle.
 *
 * WebGL is the last layer of the site, never a dependency: if three.js fails to
 * load, WebGL is unavailable, the device is weak or the visitor asked for
 * reduced motion, the CSS light field in the markup stays as it is and nothing
 * else on the page changes.
 *
 * Rendering stops when the hero leaves the viewport or the tab is hidden.
 */

import { PALETTES, createVolume, createField } from "./materials.js";

const THREE_URL = "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js";

const host = document.querySelector("[data-atmosphere]");

const prefersReducedMotion =
  window.matchMedia &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Pick a quality tier from viewport size and coarse device signals. */
function resolveTier() {
  const width = window.innerWidth;
  const cores = navigator.hardwareConcurrency || 8;
  const memory = navigator.deviceMemory || 8;

  if (width < 720 || cores <= 4 || memory <= 4) {
    return { name: "low", segments: 48, dpr: 1.25, amplitude: 0.95 };
  }
  if (width < 1200 || cores <= 6) {
    return { name: "medium", segments: 96, dpr: 1.4, amplitude: 1.1 };
  }
  return { name: "high", segments: 152, dpr: 1.75, amplitude: 1.2 };
}

function supportsWebGL() {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(
      window.WebGLRenderingContext &&
        (canvas.getContext("webgl2") || canvas.getContext("webgl"))
    );
  } catch (err) {
    return false;
  }
}

async function init() {
  if (!host || !supportsWebGL()) return;

  let THREE;
  try {
    THREE = await import(/* @vite-ignore */ THREE_URL);
  } catch (err) {
    // CDN unreachable or blocked — the CSS fallback is already on screen.
    return;
  }

  const tier = resolveTier();

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: tier.name === "high",
      powerPreference: "high-performance",
      failIfMajorPerformanceCaveat: false,
    });
  } catch (err) {
    return;
  }

  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, tier.dpr));
  renderer.setClearColor(0x000000, 0);
  renderer.domElement.className = "hero__canvas";
  renderer.domElement.setAttribute("aria-hidden", "true");
  host.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 40);
  camera.position.set(0, 0, 4.1);

  const volume = createVolume(THREE, tier.segments);
  volume.material.uniforms.uAmplitude.value = tier.amplitude;

  const field = createField(THREE);
  scene.add(field, volume);

  /* ---- Theme-driven uniforms, cross-faded rather than switched ---------- */

  const current = {
    deep: new THREE.Color(),
    light: new THREE.Color(),
    tint: new THREE.Color(),
    glow: new THREE.Color(),
    shade: new THREE.Color(),
    opacity: 0,
    fieldOpacity: 0,
    fresnel: 3,
    specular: 0.7,
  };

  const target = { ...current };
  let firstPaint = true;

  function readTheme() {
    const name =
      document.documentElement.getAttribute("data-theme") === "light"
        ? "light"
        : "dark";
    const palette = PALETTES[name];

    target.deep = new THREE.Color(...palette.volume.deep);
    target.light = new THREE.Color(...palette.volume.light);
    target.tint = new THREE.Color(...palette.volume.tint);
    target.glow = new THREE.Color(...palette.field.glow);
    target.shade = new THREE.Color(...palette.field.shade);
    target.opacity = palette.volume.opacity;
    target.fieldOpacity = palette.field.opacity;
    target.fresnel = palette.volume.fresnel;
    target.specular = palette.volume.specular;

    if (firstPaint) {
      current.deep.copy(target.deep);
      current.light.copy(target.light);
      current.tint.copy(target.tint);
      current.glow.copy(target.glow);
      current.shade.copy(target.shade);
      current.fresnel = target.fresnel;
      current.specular = target.specular;
      firstPaint = false;
    }
  }

  readTheme();
  window.addEventListener("themechange", readTheme);

  /* ---- Pointer: a hint of parallax, never a chase ----------------------- */

  const pointer = { x: 0, y: 0, tx: 0, ty: 0 };
  const finePointer =
    window.matchMedia &&
    window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  if (finePointer && !prefersReducedMotion) {
    window.addEventListener(
      "pointermove",
      (event) => {
        pointer.tx = (event.clientX / window.innerWidth - 0.5) * 2;
        pointer.ty = (event.clientY / window.innerHeight - 0.5) * 2;
      },
      { passive: true }
    );
  }

  /* ---- Sizing ----------------------------------------------------------- */

  function resize() {
    const rect = host.getBoundingClientRect();
    const width = Math.max(1, Math.round(rect.width));
    const height = Math.max(1, Math.round(rect.height));
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  resize();

  if ("ResizeObserver" in window) {
    new ResizeObserver(resize).observe(host);
  } else {
    window.addEventListener("resize", resize);
  }

  /* ---- Visibility gating ------------------------------------------------ */

  let heroVisible = true;
  let tabVisible = document.visibilityState !== "hidden";
  let running = false;
  let frame = 0;
  let clock = new THREE.Clock();
  let scrollProgress = 0;

  const hero = host.closest(".hero") || host;

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          heroVisible = entry.isIntersecting;
          sync();
        });
      },
      { threshold: 0 }
    ).observe(hero);
  }

  document.addEventListener("visibilitychange", () => {
    tabVisible = document.visibilityState !== "hidden";
    sync();
  });

  function sync() {
    const shouldRun = heroVisible && tabVisible;
    if (shouldRun && !running) {
      running = true;
      clock.start();
      frame = requestAnimationFrame(render);
    } else if (!shouldRun && running) {
      running = false;
      cancelAnimationFrame(frame);
      clock.stop();
    }
  }

  window.addEventListener(
    "scroll",
    () => {
      const rect = hero.getBoundingClientRect();
      const height = rect.height || 1;
      scrollProgress = Math.min(1, Math.max(0, -rect.top / height));
    },
    { passive: true }
  );

  /* ---- Frame ------------------------------------------------------------ */

  const damp = (a, b, k) => a + (b - a) * k;
  let elapsed = 0;

  function render() {
    if (!running) return;
    frame = requestAnimationFrame(render);

    const delta = Math.min(clock.getDelta(), 0.05);
    // Reduced motion freezes the deformation but keeps the material on screen.
    elapsed += prefersReducedMotion ? 0 : delta;

    const k = Math.min(1, delta * 3.2);

    current.deep.lerp(target.deep, k);
    current.light.lerp(target.light, k);
    current.tint.lerp(target.tint, k);
    current.glow.lerp(target.glow, k);
    current.shade.lerp(target.shade, k);
    current.fresnel = damp(current.fresnel, target.fresnel, k);
    current.specular = damp(current.specular, target.specular, k);

    // Scene recedes as the hero scrolls away.
    const recede = 1 - scrollProgress * 0.85;
    current.opacity = damp(current.opacity, target.opacity * recede, k);
    current.fieldOpacity = damp(
      current.fieldOpacity,
      target.fieldOpacity * recede,
      k
    );

    const vu = volume.material.uniforms;
    vu.uTime.value = elapsed;
    vu.uDeep.value.copy(current.deep);
    vu.uLight.value.copy(current.light);
    vu.uTint.value.copy(current.tint);
    vu.uOpacity.value = current.opacity;
    vu.uFresnelPower.value = current.fresnel;
    vu.uSpecular.value = current.specular;

    const fu = field.material.uniforms;
    fu.uTime.value = elapsed;
    fu.uGlow.value.copy(current.glow);
    fu.uShade.value.copy(current.shade);
    fu.uOpacity.value = current.fieldOpacity;

    pointer.x = damp(pointer.x, pointer.tx, 0.035);
    pointer.y = damp(pointer.y, pointer.ty, 0.035);

    // Slow drift plus a very small pointer offset. The form never follows
    // the cursor — it only leans.
    camera.position.x = Math.sin(elapsed * 0.048) * 0.16 + pointer.x * 0.075;
    camera.position.y = Math.cos(elapsed * 0.037) * 0.11 - pointer.y * 0.055;
    camera.position.z = 3.6 + scrollProgress * 0.55;
    camera.lookAt(0.3, 0.05, 0);

    volume.rotation.z = -0.42 + Math.sin(elapsed * 0.026) * 0.03;
    volume.rotation.x = -0.98 + Math.cos(elapsed * 0.021) * 0.024;

    renderer.render(scene, camera);
  }

  sync();
  host.setAttribute("data-ready", "true");

  window.addEventListener("pagehide", () => {
    running = false;
    cancelAnimationFrame(frame);
    renderer.dispose();
  });
}

init();
