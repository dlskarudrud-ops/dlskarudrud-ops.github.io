/**
 * shaders.js — GLSL for the hero atmosphere.
 *
 * Two surfaces only:
 *   FIELD  — a soft environmental light field sitting far behind everything.
 *   VOLUME — a large, slowly deforming optical sheet read as glass, lit by
 *            fresnel and one refracted gradient rather than a real envmap.
 *
 * There are no particles and no post-processing. A broad caustic ribbon and
 * restrained spectral edge add the polished optical finish while the motion
 * stays slow enough to read closer to still photography than animation.
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
  // Two coherent waves give the sheet its slow, soft ribbon fold. Noise only
  // breaks the symmetry; the silhouette is carried by these broad motions.
  float ribbonA = sin(p.x * 0.42 + p.y * 0.16 + t * 0.035) * 0.22;
  float ribbonB = cos(p.y * 0.36 - p.x * 0.12 - t * 0.028) * 0.12;
  return a * 0.58 + b * 0.2 + ribbonA + ribbonB;
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
  // The surface normal starts in object space. Move it into view space so it
  // can be compared with vView and the view-space studio light correctly.
  vec3 objectNormal = normalize(cross(tangent, bitangent));
  vNormal = normalize(normalMatrix * objectNormal);

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
uniform vec3  uPrismA;
uniform vec3  uPrismB;
uniform vec3  uLightDir;
uniform float uTime;
uniform float uOpacity;
uniform float uFresnelPower;
uniform float uSpecular;

varying vec3  vNormal;
varying vec3  vView;
varying vec2  vUv;
varying float vHeight;

void main() {
  vec3 V = normalize(vView);
  vec3 rawN = normalize(vNormal);
  // Orient the interpolated normal toward the viewer. gl_FrontFacing
  // changes per triangle and can split a strongly folded, double-sided sheet
  // into bright/dark shards at grazing angles.
  vec3 N = faceforward(rawN, -V, rawN);
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

  // One broad studio caustic moves across the sheet. It is intentionally a
  // single band rather than a repeated pattern so it reads as reflected light.
  float causticAxis = (vUv.x - 0.5) * 0.82
                    + (vUv.y - 0.5) * 0.34
                    + vHeight * 0.09;
  float causticShift = sin(uTime * 0.022) * 0.16;
  float causticDistance = (causticAxis - causticShift) * 4.8;
  float caustic = exp(-causticDistance * causticDistance);

  // Very low chroma at the grazing edge suggests dispersion in thick glass
  // without turning the warm portfolio palette into a rainbow gradient.
  float spectralMix = clamp(0.5 + vHeight * 0.28 + N.x * 0.18, 0.0, 1.0);
  vec3 prism = mix(uPrismA, uPrismB, spectralMix);
  float glassRim = pow(1.0 - max(dot(N, V), 0.0), 4.2);

  vec3 color = env + uTint * fresnel * 1.26 + vec3(spec) * 0.58;
  color += prism * glassRim * 0.16;
  color += mix(uLight, prism, 0.42) * caustic * (0.045 + body * 0.085);

  // Sub-1/255 screen-space dither prevents visible banding in large dark
  // gradients. This is texture correction, not visible film grain.
  float dither = fract(52.9829189 * fract(dot(
    gl_FragCoord.xy, vec2(0.06711056, 0.00583715)
  ))) - 0.5;
  color += vec3(dither / 255.0);

  // Fade the outer edge so the geometry border is never visible. The CSS mask
  // already softens the container, so this only needs to cover the last band.
  vec2 d = abs(vUv - 0.5) * 2.0;
  float edge = (1.0 - smoothstep(0.62, 0.94, d.x))
             * (1.0 - smoothstep(0.66, 0.94, d.y));

  float presence = 0.2 + body * 0.4 + fresnel * 0.58
                 + spec * 0.42 + caustic * 0.08;

  gl_FragColor = vec4(color, clamp(presence * uOpacity * edge, 0.0, 1.0));

  #include <tonemapping_fragment>
  #include <colorspace_fragment>
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
  vec2 edgeDistance = abs(uv - 0.5) * 2.0;
  float fieldEdge = (1.0 - smoothstep(0.72, 0.96, edgeDistance.x))
                  * (1.0 - smoothstep(0.72, 0.96, edgeDistance.y));
  // Keep the environmental field broad but translucent. Compressing its
  // shoulders prevents it from becoming an opaque fog behind typography.
  float alpha = pow(max(body, 0.0), 1.35) * uOpacity * vignette * fieldEdge;

  float dither = fract(52.9829189 * fract(dot(
    gl_FragCoord.xy, vec2(0.06711056, 0.00583715)
  ))) - 0.5;
  color += vec3(dither / 255.0);

  gl_FragColor = vec4(color, clamp(alpha, 0.0, 1.0));

  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

/* ---------------------------------------------------------------------------
   AMBIENT — fixed, full-viewport light field shared by every page
   --------------------------------------------------------------------------- */

export const AMBIENT_VERT = /* glsl */ `
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position.xy, 0.0, 1.0);
}
`;

export const AMBIENT_FRAG = /* glsl */ `
precision mediump float;

uniform float uTime;
uniform float uScroll;
uniform float uAspect;
uniform float uOpacity;
uniform vec3  uWarm;
uniform vec3  uCool;
uniform vec3  uNeutral;

varying vec2 vUv;

${NOISE_GLSL}

float softLight(vec2 p, vec2 centre, vec2 spread) {
  vec2 d = (p - centre) / spread;
  return exp(-dot(d, d) * 1.45);
}

void main() {
  vec2 p = vUv - 0.5;
  p.x *= uAspect;

  float drift = uTime * 0.018;
  float scrollWave = uScroll * 6.2831853;

  vec2 warmCentre = vec2(
    uAspect * (0.32 + sin(drift) * 0.035),
    0.28 - cos(scrollWave * 0.34) * 0.18
  );
  vec2 coolCentre = vec2(
    -uAspect * (0.3 + cos(drift * 0.76) * 0.04),
    -0.22 + sin(scrollWave * 0.42) * 0.2
  );
  vec2 neutralCentre = vec2(
    sin(scrollWave * 0.27) * uAspect * 0.18,
    cos(scrollWave * 0.31) * 0.24
  );

  float warm = softLight(p, warmCentre, vec2(uAspect * 0.5, 0.56));
  float cool = softLight(p, coolCentre, vec2(uAspect * 0.46, 0.62));
  float neutral = softLight(p, neutralCentre, vec2(uAspect * 0.72, 0.8));

  float fieldNoise = snoise(p * 0.74 + vec2(drift * 0.16, -drift * 0.11));
  float modulation = 0.84 + fieldNoise * 0.16;
  warm *= modulation;
  cool *= 1.0 - fieldNoise * 0.08;

  vec3 color = uWarm * warm + uCool * cool + uNeutral * neutral * 0.46;
  float alpha = max(max(warm, cool), neutral * 0.58) * uOpacity;

  float dither = fract(52.9829189 * fract(dot(
    gl_FragCoord.xy, vec2(0.06711056, 0.00583715)
  ))) - 0.5;
  color += vec3(dither / 255.0);

  gl_FragColor = vec4(color, clamp(alpha, 0.0, 1.0));

  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;
