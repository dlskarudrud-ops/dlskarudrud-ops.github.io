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
} from "./shaders.js";

export const PALETTES = {
  light: {
    volume: {
      // Shadowed areas sit below the paper tone so the sheet reads as a
      // translucent body catching daylight rather than a white-on-white wash.
      deep: [0.6, 0.585, 0.552],
      light: [1.0, 0.99, 0.962],
      tint: [0.55, 0.4, 0.17],
      opacity: 0.62,
      fresnel: 2.2,
      specular: 0.45,
    },
    field: {
      glow: [1.0, 0.978, 0.928],
      shade: [0.82, 0.81, 0.785],
      opacity: 0.6,
    },
  },
  dark: {
    volume: {
      deep: [0.052, 0.048, 0.045],
      light: [0.6, 0.47, 0.29],
      tint: [0.88, 0.7, 0.42],
      opacity: 0.82,
      fresnel: 2.9,
      specular: 0.6,
    },
    field: {
      glow: [0.3, 0.225, 0.14],
      shade: [0.042, 0.04, 0.039],
      opacity: 0.8,
    },
  },
};

/** Accent variant used on the Project-TS pages, if the hero is ever reused. */
export const STEEL = {
  light: { tint: [0.28, 0.45, 0.62], glow: [0.9, 0.94, 0.99] },
  dark: { tint: [0.45, 0.66, 0.85], glow: [0.13, 0.2, 0.28] },
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
