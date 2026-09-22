/* page_surface.mjs - T19's pure page-surface geometry.
   This is deliberately a standalone helper, not a renderer or an inlined engine region. The later player slice can
   consume its returned stage quad, native host, chart box, viewBox and plane homography without measuring the DOM.
   The registered surface is supplied by the caller; no page profile layout lives here. */
import { minJerk } from "./ease.mjs";
import { planeMatrix } from "./homography.mjs";

export const SURFACE_PAGE = Object.freeze({
  VIEW_H: 560,
  GROW_S: 0.45,
  ASPECT_TOL: 0.001,       /* 0.1%: CSS chart box and SVG viewBox must agree. */
});

const psFinite = (value) => typeof value === "number" && Number.isFinite(value);
const psFail = (what, detail) => { throw new TypeError(`page-surface: ${what} ${detail}`); };
const psNumber = (value, what) => {
  const out = +value;
  if (!psFinite(out)) psFail(what, "must be finite");
  return out;
};

const psPointQuad = (quad, what, normalized = false) => {
  if (!Array.isArray(quad) || quad.length !== 4) psFail(what, "must contain four [x, y] points");
  const out = quad.map((point, i) => {
    if (!Array.isArray(point) || point.length < 2) psFail(`${what}[${i}]`, "must be [x, y]");
    const x = psNumber(point[0], `${what}[${i}].x`), y = psNumber(point[1], `${what}[${i}].y`);
    if (normalized && (x < 0 || x > 1 || y < 0 || y > 1)) {
      psFail(`${what}[${i}]`, "must be normalized to [0, 1]");
    }
    return [x, y];
  });
  const area = Math.abs(out.reduce((sum, p, i) => {
    const q = out[(i + 1) % out.length];
    return sum + p[0] * q[1] - q[0] * p[1];
  }, 0)) / 2;
  if (out.some((p, i) => psEdgeLength(p, out[(i + 1) % out.length]) <= 1e-12)) {
    psFail(what, "must not repeat adjacent corners");
  }
  if (!(area > 1e-12)) psFail(what, "must be non-degenerate");
  return out;
};

const psStageOf = (stage) => {
  let w, h;
  if (Array.isArray(stage)) [w, h] = stage;
  else if (stage && typeof stage === "object") {
    w = stage.w ?? stage.width ?? stage.W;
    h = stage.h ?? stage.height ?? stage.H;
  }
  w = psNumber(w, "stage.width");
  h = psNumber(h, "stage.height");
  if (!(w > 0) || !(h > 0)) psFail("stage", "width and height must be positive");
  return { w, h };
};

const psEdgeLength = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
const psEdgeMeans = (quad, what) => {
  const w = (psEdgeLength(quad[0], quad[1]) + psEdgeLength(quad[3], quad[2])) / 2;
  const h = (psEdgeLength(quad[0], quad[3]) + psEdgeLength(quad[1], quad[2])) / 2;
  if (!(w > 0) || !(h > 0) || !psFinite(w) || !psFinite(h)) psFail(what, "has no finite positive edge lengths");
  return { w, h };
};

const psToStageQuad = (normalized, stage) => normalized.map(([x, y]) => [x * stage.w, y * stage.h]);
const psFullStageQuad = (stage) => [[0, 0], [stage.w, 0], [stage.w, stage.h], [0, stage.h]];
const psCopyQuad = (quad) => quad.map(([x, y]) => [x, y]);
const psLerp = (a, b, u) => a + (b - a) * u;
const psLerpQuad = (a, b, u) => a.map((p, i) => [psLerp(p[0], b[i][0], u), psLerp(p[1], b[i][1], u)]);
const psPick = (...values) => values.find((value) => value != null);

/* A public conversion is useful to the renderer and makes the normalized -> stage boundary explicit. */
export const surfaceStageQuad = (normalizedQuad, stage) => {
  const S = psStageOf(stage), Qn = psPointQuad(normalizedQuad, "registered quad", true);
  return psToStageQuad(Qn, S);
};

/* The source state: the registered quad in stage pixels and a native host whose aspect is the measured surface.
   `viewH` is positional to mirror the compiler's surface_plot_geometry(quad, stage_size, view_h=560) law. */
export const surfacePlotGeometry = (normalizedQuad, stage, viewH = SURFACE_PAGE.VIEW_H) => {
  if (viewH && typeof viewH === "object") viewH = viewH.viewH ?? viewH.height;
  const S = psStageOf(stage), Qn = psPointQuad(normalizedQuad, "registered quad", true);
  const viewHeight = psNumber(viewH, "viewH");
  if (!(viewHeight > 0)) psFail("viewH", "must be positive");
  const quad = psToStageQuad(Qn, S), fullQuad = psFullStageQuad(S), host = psEdgeMeans(quad, "registered quad");
  const viewWidth = viewHeight * host.w / host.h;
  return {
    registeredQuad: psCopyQuad(Qn),
    stage: { w: S.w, h: S.h },
    quad: psCopyQuad(quad),
    fullQuad: psCopyQuad(fullQuad),
    hostW: host.w,
    hostH: host.h,
    viewW: viewWidth,
    viewH: viewHeight,
    chart: { x: 0, y: 0, w: host.w, h: host.h },
    viewBox: { x: 0, y: 0, w: viewWidth, h: viewHeight },
  };
};

const psDestinationProfile = (destination, viewH) => {
  if (!destination || typeof destination !== "object") psFail("destination", "geometry/profile is required");
  const box = destination.chartBox || destination.chart || destination.box || destination;
  if (!box || typeof box !== "object") psFail("destination.chart", "must be a geometry object");
  const x = psNumber(psPick(box.x, box.X), "destination.x");
  const y = psNumber(psPick(box.y, box.Y), "destination.y");
  const w = psNumber(psPick(box.w, box.W), "destination.w");
  const h = psNumber(psPick(box.h, box.H), "destination.h");
  if (!(w > 0) || !(h > 0)) psFail("destination", "chart width and height must be positive");

  const vb = destination.viewBox || destination.viewbox || {};
  const destViewH = psNumber(psPick(vb.h, vb.height, destination.vh, destination.viewH, destination.VH, viewH), "destination.viewH");
  const destViewWValue = psPick(vb.w, vb.width, destination.vw, destination.viewW, destination.VW);
  const destViewW = destViewWValue == null ? destViewH * w / h : psNumber(destViewWValue, "destination.viewW");
  if (!(destViewW > 0) || !(destViewH > 0)) psFail("destination", "viewBox dimensions must be positive");
  if (Math.abs(destViewH - viewH) > 1e-9) {
    psFail("destination.viewH", `must equal source viewH ${viewH}`);
  }
  const aspectDelta = Math.abs((w / h) / (destViewW / destViewH) - 1);
  if (aspectDelta > SURFACE_PAGE.ASPECT_TOL) {
    psFail("destination", `chart/viewBox aspect mismatch ${(aspectDelta * 100).toFixed(4)}%`);
  }
  return {
    chart: { x, y, w, h },
    viewBox: { x: 0, y: 0, w: destViewW, h: destViewH },
  };
};

const psSourceProfile = (source) => {
  if (!source || typeof source !== "object") psFail("source", "surfacePlotGeometry output is required");
  const normalized = psPointQuad(source.registeredQuad, "source.registeredQuad", true);
  const viewH = psNumber(source.viewH, "source.viewH");
  return surfacePlotGeometry(normalized, source.stage, viewH);
};

const psProgressFor = (time, duration) => {
  const t = psNumber(time, "time"), d = psNumber(duration, "duration");
  if (!(d > 0)) psFail("duration", "must be positive");
  return { time: t, duration: d, progress: Math.min(1, Math.max(0, t / d)) };
};

/* One seek -> one frame. `destination` is the actual selected page/profile geometry supplied by the caller, e.g.
   `{x, y, w, h, vw, vh}` from the readability profile. Intermediate CSS height is derived from the current width and
   viewBox aspect, so no browser `meet` letterbox or anisotropic scale is introduced. */
export const surfaceGeometryAt = (source, destination, time, options = {}) => {
  const base = psSourceProfile(source);
  const duration = options.duration == null ? SURFACE_PAGE.GROW_S : options.duration;
  const clock = psProgressFor(time, duration), dest = psDestinationProfile(destination, base.viewH);
  const u = minJerk(clock.progress);
  const endpoint = clock.progress <= 0 ? 0 : (clock.progress >= 1 ? 1 : null);
  const quad = endpoint === 0 ? psCopyQuad(base.quad) : (endpoint === 1 ? psCopyQuad(base.fullQuad) : psLerpQuad(base.quad, base.fullQuad, u));
  const host = psEdgeMeans(quad, "surface quad");
  const matrix = planeMatrix(quad, host.w, host.h, 0, 0);
  if (!matrix) psFail("surface quad", "cannot produce a homography");

  let chart, viewBox;
  if (endpoint === 0) {
    chart = { ...base.chart };
    viewBox = { ...base.viewBox };
  } else if (endpoint === 1) {
    chart = { ...dest.chart };
    viewBox = { ...dest.viewBox };
  } else {
    const viewW = psLerp(base.viewW, dest.viewBox.w, u);
    const width = psLerp(base.hostW, dest.chart.w, u);
    chart = {
      x: psLerp(0, dest.chart.x, u),
      y: psLerp(0, dest.chart.y, u),
      w: width,
      h: width * base.viewH / viewW,
    };
    viewBox = { x: 0, y: 0, w: viewW, h: base.viewH };
  }

  return {
    time: clock.time,
    duration: clock.duration,
    progress: clock.progress,
    eased: u,
    quad,
    hostW: host.w,
    hostH: host.h,
    host: { x: 0, y: 0, w: host.w, h: host.h },
    matrix,
    chart,
    viewBox,
    chartAspect: chart.w / chart.h,
    viewBoxAspect: viewBox.w / viewBox.h,
  };
};
