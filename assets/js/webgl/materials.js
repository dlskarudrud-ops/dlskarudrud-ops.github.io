/**
 * materials.js — theme palettes and material construction for the hero scene.
 *
 * Light and dark are not inversions of each other. They share one identity but
 * are art-directed separately: light reads as clear glass in daylight, dark as
 * a denser volume with stronger edge reflections and a lower ambient floor.
 */

import {
  VOLUME_VERT,
  VOLUME_FRAG,
  FIELD_VERT,
  FIELD_FRAG,
  AMBIENT_VERT,
  AMBIENT_FRAG,
} from "./shaders.js?v=15";

export const PALETTES = {
  light: {
    volume: {
      // Shadowed areas sit below the paper tone so the sheet reads as a
      // translucent body catching daylight rather than a white-on-white wash.
      // Daylight glass needs a real shadow body; a white highlight alone
      // disappears on the warm paper background.
      deep: [0.06, 0.18, 0.42],
      light: [0.68, 0.84, 1.0],
      tint: [0.08, 0.34, 0.82],
      prismA: [0.12, 0.52, 1.0],
      prismB: [0.02, 0.18, 0.72],
      opacity: 0.86,
      fresnel: 1.65,
      specular: 0.44,
    },
    field: {
      glow: [0.36, 0.62, 1.0],
      shade: [0.08, 0.2, 0.45],
      opacity: 0.22,
    },
  },
  dark: {
    volume: {
      deep: [0.052, 0.048, 0.045],
      light: [0.52, 0.38, 0.21],
      tint: [0.78, 0.56, 0.28],
      prismA: [0.18, 0.54, 1.0],
      prismB: [0.05, 0.25, 0.72],
      opacity: 0.72,
      fresnel: 2.9,
      specular: 0.6,
    },
    field: {
      glow: [0.3, 0.225, 0.14],
      shade: [0.042, 0.04, 0.039],
      opacity: 0.24,
    },
  },
};

/** Accent variant used on the Project-TS pages, if the hero is ever reused. */
export const STEEL = {
  light: {
    tint: [0.28, 0.45, 0.62],
    glow: [0.9, 0.94, 0.99],
    prismA: [0.28, 0.62, 1.0],
    prismB: [0.08, 0.34, 0.8],
  },
  dark: {
    tint: [0.45, 0.66, 0.85],
    glow: [0.13, 0.2, 0.28],
    prismA: [0.24, 0.66, 1.0],
    prismB: [0.06, 0.3, 0.78],
  },
};

/** Full-page light is art-directed independently from the optical sheet. */
export const AMBIENT_PALETTES = {
  light: {
    // Near-white gold is only a quiet bridge to the typographic accent;
    // blue owns the wide optical field in daylight.
    warm: [1.0, 0.92, 0.76],
    cool: [0.28, 0.56, 0.96],
    neutral: [0.62, 0.76, 0.94],
    opacity: 0.24,
    exposure: 0.88,
  },
  dark: {
    warm: [0.48, 0.25, 0.08],
    cool: [0.08, 0.18, 0.38],
    neutral: [0.2, 0.12, 0.06],
    opacity: 0.36,
    exposure: 1.05,
  },
};

export function createVolume(THREE, segments) {
  const geometry = new THREE.PlaneGeometry(9.5, 9.5, segments, segments);

  const material = new THREE.ShaderMaterial({
    vertexShader: VOLUME_VERT,
    fragmentShader: VOLUME_FRAG,
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
    uniforms: {
      uTime: { value: 0 },
      uAmplitude: { value: 1.2 },
      uScale: { value: 0.28 },
      uDeep: { value: new THREE.Color() },
      uLight: { value: new THREE.Color() },
      uTint: { value: new THREE.Color() },
      uPrismA: { value: new THREE.Color() },
      uPrismB: { value: new THREE.Color() },
      uLightDir: { value: new THREE.Vector3(-0.45, 0.72, 0.55) },
      uOpacity: { value: 0 },
      uFresnelPower: { value: 3.0 },
      uSpecular: { value: 0.7 },
    },
  });

  const mesh = new THREE.Mesh(geometry, material);
  // Deliberately off-axis, cropped and seen near grazing angle: this is an
  // optical installation, not an object on a turntable.
  mesh.rotation.set(-0.98, 0.3, -0.42);
  mesh.position.set(0.7, -0.28, 0);
  return mesh;
}

export function createField(THREE) {
  const geometry = new THREE.PlaneGeometry(16, 16, 1, 1);

  const material = new THREE.ShaderMaterial({
    vertexShader: FIELD_VERT,
    fragmentShader: FIELD_FRAG,
    transparent: true,
    depthWrite: false,
    uniforms: {
      uTime: { value: 0 },
      uGlow: { value: new THREE.Color() },
      uShade: { value: new THREE.Color() },
      uOpacity: { value: 0 },
    },
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(0.4, 0.1, -3.4);
  return mesh;
}

export function createAmbient(THREE) {
  const geometry = new THREE.PlaneGeometry(2, 2, 1, 1);
  const material = new THREE.ShaderMaterial({
    vertexShader: AMBIENT_VERT,
    fragmentShader: AMBIENT_FRAG,
    transparent: true,
    depthWrite: false,
    depthTest: false,
    uniforms: {
      uTime: { value: 0 },
      uScroll: { value: 0 },
      uAspect: { value: 1 },
      uOpacity: { value: 0 },
      uWarm: { value: new THREE.Color() },
      uCool: { value: new THREE.Color() },
      uNeutral: { value: new THREE.Color() },
    },
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  return mesh;
}
