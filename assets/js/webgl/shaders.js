/**
 * shaders.js — GLSL for the hero atmosphere.
 *
 * Two surfaces only:
 *   FIELD  — a soft environmental light field sitting far behind everything.
 *   VOLUME — a large, slowly deforming optical sheet read as glass, lit by
 *            fresnel and one refracted gradient rather than a real envmap.
 *
 * There is no rotation, no particles and no post-processing. The motion is
 * slow enough that the scene reads closer to still photography than animation.
 */

/* Compact 2D simplex noise (Ashima / webgl-noise, MIT). Used for the low
   frequency deformation only — never for visible high frequency detail. */
export const NOISE_GLSL = /* glsl */ `
vec3 permute289(vec3 x) { return mod(((x * 34.0) + 1.0) * x, 289.0); }

float snoise(vec2 v) {
  const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                     -0.577350269189626, 0.024390243902439);
  vec2 i  = floor(v + dot(v, C.yy));
  vec2 x0 = v -   i + dot(i, C.xx);
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod(i, 289.0);
  vec3 p = permute289(permute289(i.y + vec3(0.0, i1.y, 1.0))
                    + i.x + vec3(0.0, i1.x, 1.0));
  vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy),
                          dot(x12.zw, x12.zw)), 0.0);
  m = m * m; m = m * m;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
  vec3 g;
  g.x  = a0.x  * x0.x  + h.x  * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}
`;

/* ---------------------------------------------------------------------------
   VOLUME — the optical sheet
   --------------------------------------------------------------------------- */

export const VOLUME_VERT = /* glsl */ `
uniform float uTime;
uniform float uAmplitude;
uniform float uScale;

varying vec3 vNormal;
varying vec3 vView;
varying vec2 vUv;
varying float vHeight;

${NOISE_GLSL}

// Two low frequency octaves. Anything faster would start pulling the eye
// away from the hero copy, which is the one thing this scene must not do.
float surface(vec2 p, float t) {
  float a = snoise(vec2(p.x * uScale + t * 0.055, p.y * uScale - t * 0.041));
  float b = snoise(vec2(p.x * uScale * 2.15 - t * 0.031,
                        p.y * uScale * 1.95 + t * 0.037));
  return a * 0.72 + b * 0.28;
}

void main() {
  vUv = uv;

  vec3 pos = position;
  float t = uTime;
  float h = surface(pos.xy, t);
  pos.z += h * uAmplitude;
  vHeight = h;

  // Analytic normal from two neighbouring samples of the same field.
  float e = 0.18;
  float hx = surface(pos.xy + vec2(e, 0.0), t);
  float hy = surface(pos.xy + vec2(0.0, e), t);
  vec3 tangent   = normalize(vec3(e, 0.0, (hx - h) * uAmplitude));
  vec3 bitangent = normalize(vec3(0.0, e, (hy - h) * uAmplitude));
  vNormal = normalize(cross(tangent, bitangent));

  vec4 mv = modelViewMatrix * vec4(pos, 1.0);
  vView = -mv.xyz;
  gl_Position = projectionMatrix * mv;
}
`;

export const VOLUME_FRAG = /* glsl */ `
precision highp float;

uniform vec3  uDeep;
uniform vec3  uLight;
uniform vec3  uTint;
uniform vec3  uLightDir;
uniform float uOpacity;
uniform float uFresnelPower;
uniform float uSpecular;

varying vec3  vNormal;
varying vec3  vView;
varying vec2  vUv;
varying float vHeight;

void main() {
  vec3 N = normalize(vNormal);
  vec3 V = normalize(vView);
  vec3 L = normalize(uLightDir);

  // Wrapped diffuse. Broad and smooth so the sheet reads as one lit body
  // rather than a field of separate highlights.
  float wrap = clamp(dot(N, L) * 0.5 + 0.5, 0.0, 1.0);
  float body = pow(wrap, 1.7);

  // A single refracted direction stands in for an environment probe: enough
  // to bend the gradient across the surface like thick glass does.
  vec3 refracted = refract(-V, N, 0.72);
  float bend = clamp(refracted.y * 0.35 + 0.5, 0.0, 1.0);

  vec3 env = mix(uDeep, uLight, clamp(body * 0.72 + bend * 0.28, 0.0, 1.0));

  float fresnel = pow(1.0 - max(dot(N, V), 0.0), uFresnelPower);

  // Wide, low sheen — a soft studio reflection, not a plastic hotspot.
  float spec = pow(max(dot(reflect(-L, N), V), 0.0), 16.0) * uSpecular;

  vec3 color = env + uTint * fresnel * 1.35 + vec3(spec) * 0.6;

  // Fade the outer edge so the geometry border is never visible. The CSS mask
  // already softens the container, so this only needs to cover the last band.
  vec2 d = abs(vUv - 0.5) * 2.0;
  float edge = (1.0 - smoothstep(0.66, 1.0, d.x)) * (1.0 - smoothstep(0.7, 1.0, d.y));

  float presence = 0.2 + body * 0.4 + fresnel * 0.62 + spec * 0.45;

  gl_FragColor = vec4(color, clamp(presence * uOpacity * edge, 0.0, 1.0));
}
`;

/* ---------------------------------------------------------------------------
   FIELD — the environmental illumination behind the sheet
   --------------------------------------------------------------------------- */

export const FIELD_VERT = /* glsl */ `
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

export const FIELD_FRAG = /* glsl */ `
precision mediump float;

uniform float uTime;
uniform vec3  uGlow;
uniform vec3  uShade;
uniform float uOpacity;

varying vec2 vUv;

${NOISE_GLSL}

void main() {
  vec2 uv = vUv;

  // Very slow drift of a single broad illumination centre.
  vec2 centre = vec2(0.62 + sin(uTime * 0.035) * 0.045,
                     0.46 + cos(uTime * 0.028) * 0.038);

  float d = distance(uv, centre);
  float core = 1.0 - smoothstep(0.05, 0.72, d);

  float grain = snoise(uv * 2.4 + uTime * 0.02) * 0.5 + 0.5;
  float body = core * mix(0.72, 1.0, grain);

  vec3 color = mix(uShade, uGlow, body);

  float vignette = 1.0 - smoothstep(0.42, 1.02, distance(uv, vec2(0.5)));
  float alpha = body * uOpacity * vignette;

  gl_FragColor = vec4(color, clamp(alpha, 0.0, 1.0));
}
`;
