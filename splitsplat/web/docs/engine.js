"use strict";
// Splitsplat Island - browser engine (plain JavaScript, no libraries). Port of the Python game's engine.
const W = 960, H = 640;
const FONT = "Arial, Helvetica, sans-serif";
const INK = [62, 36, 20], WHITE = [255, 255, 255], CREAM = [253, 238, 196], BLUE = [40, 80, 170], RED = [190, 50, 50], GREEN = [40, 120, 50],
  GOLD = [240, 190, 40], GREY = [150, 140, 130], WOOD = [150, 95, 45], GREENB = [80, 140, 55], PURP = [115, 85, 140], DRED = [170, 50, 50];
const SKY = [132, 196, 232], SKY2 = [160, 214, 240], GRASS = [104, 168, 72], GRASS2 = [88, 150, 60], SAND = [236, 212, 150], SANDD = [214, 186, 120],
  SEAC = [62, 132, 200], SEAL = [96, 160, 220], WOODC = [170, 118, 62], WOODD = [110, 70, 35], STONE = [150, 150, 160], DARKC = [40, 30, 35],
  LEAF = [52, 128, 60], LEAFD = [36, 98, 48], TRUNK = [110, 70, 40];

let ctx = null, mouse = { x: -1, y: -1 }, TOUCH = false;
const setCtx = c => { ctx = c; };
const css = c => (c.length > 3 ? `rgba(${c[0]},${c[1]},${c[2]},${c[3] / 255})` : `rgb(${c[0]},${c[1]},${c[2]})`);
const shade = (c, d) => c.map(v => Math.max(0, Math.min(255, v + d)));
const rnd = n => Math.floor(Math.random() * n);
const fmt = v => (Number.isInteger(v) ? String(v) : v.toFixed(2).replace(/0+$/, "").replace(/\.$/, ""));
const inR = (x, y, r) => x >= r[0] && x < r[0] + r[2] && y >= r[1] && y < r[1] + r[3];
const shuffle = a => { for (let i = a.length - 1; i > 0; i--) { const j = rnd(i + 1); [a[i], a[j]] = [a[j], a[i]]; } return a; };

// ------------------------------------------------------------------ canvas UI helpers
const fr = (c, x, y, w, h) => { ctx.fillStyle = css(c); ctx.fillRect(x, y, w, h); };
const sr = (c, x, y, w, h, lw = 1) => { ctx.strokeStyle = css(c); ctx.lineWidth = lw; ctx.strokeRect(x + lw / 2, y + lw / 2, w - lw, h - lw); };
const fc = (c, x, y, r) => { ctx.fillStyle = css(c); ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill(); };
const ln = (c, x1, y1, x2, y2, w = 1) => { ctx.strokeStyle = css(c); ctx.lineWidth = w; ctx.lineCap = "butt"; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); };
const font = (sz, b) => (b ? "bold " : "") + sz + "px " + FONT;
const tw = (s, sz, b) => { ctx.font = font(sz, b); return ctx.measureText(s).width; };

function wrap(s, sz, b, maxw) {
  const out = [];
  for (const para of s.split("\n")) {
    let cur = "";
    for (const w of para.split(/\s+/).filter(Boolean)) {
      const t = cur ? cur + " " + w : w;
      if (tw(t, sz, b) <= maxw) cur = t; else { out.push(cur); cur = w; }
    }
    out.push(cur);
  }
  return out;
}

function text(s, sz, col, x, y, o = {}) {
  const lines = o.maxw ? wrap(s, sz, !!o.bold, o.maxw) : [s];
  const lh = Math.round(sz * 1.15) + 2;
  ctx.font = font(sz, !!o.bold); ctx.fillStyle = css(col); ctx.textBaseline = "top"; ctx.textAlign = o.center ? "center" : "left";
  lines.forEach((l, i) => ctx.fillText(l, x, y + i * lh));
  return y + lines.length * lh;
}
const FT = (s, col, x, y, o = {}) => text(s, 44, col, x, y, { bold: true, ...o });
const FB = (s, col, x, y, o = {}) => text(s, 26, col, x, y, { bold: true, ...o });
const FM = (s, col, x, y, o = {}) => text(s, 21, col, x, y, o);
const FS = (s, col, x, y, o = {}) => text(s, 16, col, x, y, o);

function fit(s, r, o = {}) {
  const sizes = o.sizes || [24, 22, 20, 18, 16, 14, 12];
  let sz, lines, lh;
  for (sz of sizes) { lines = wrap(s, sz, !!o.bold, r[2]); lh = Math.round(sz * 1.15) + 1; if (lines.length * lh <= r[3]) break; }
  ctx.font = font(sz, !!o.bold); ctx.fillStyle = css(o.col || INK); ctx.textBaseline = "top"; ctx.textAlign = o.center ? "center" : "left";
  let y = r[1];
  for (const l of lines) { ctx.fillText(l, o.center ? r[0] + r[2] / 2 : r[0], y); y += lh; }
}

function panel(r, col = CREAM) {
  const [x, y, w, h] = r;
  fr([70, 40, 18], x, y, w, h); fr([176, 112, 52], x + 3, y + 3, w - 6, h - 6); fr([120, 72, 30], x + 6, y + 6, w - 12, h - 12); fr(col, x + 8, y + 8, w - 16, h - 16);
}

class Button {
  constructor(r, label, color = WOOD) { this.r = r; this.label = label; this.color = color; this.enabled = true; }
  draw() {
    const [x, y, w, h] = this.r;
    let c = this.enabled ? this.color : GREY;
    if (this.enabled && inR(mouse.x, mouse.y, this.r) && !TOUCH) c = shade(c, 30);
    fr([50, 28, 14], x, y, w, h); fr(c, x + 3, y + 3, w - 6, h - 6); fr(shade(c, 45), x + 3, y + 3, w - 6, 3); fr(shade(c, -40), x + 3, y + h - 6, w - 6, 3);
    let sz, lines, lh;
    for (sz of [21, 19, 17, 15, 13, 12]) { lines = wrap(this.label, sz, true, w - 26); lh = Math.round(sz * 1.15); if (lines.length * lh <= h - 12) break; }
    ctx.font = font(sz, true); ctx.textBaseline = "top"; ctx.textAlign = "center";
    let yy = y + h / 2 - (lines.length * lh) / 2;
    for (const l of lines) { ctx.fillStyle = "rgb(40,20,10)"; ctx.fillText(l, x + w / 2 + 1, yy + 1); ctx.fillStyle = "#fff"; ctx.fillText(l, x + w / 2, yy); yy += lh; }
  }
  hit(ev) { return this.enabled && ev.type === "down" && inR(ev.x, ev.y, this.r); }
}

// ------------------------------------------------------------------ pixel buffer (true pixel art, no anti-aliasing)
class Pix {
  constructor(w, h) { this.w = w; this.h = h; this.d = new Uint8ClampedArray(w * h * 4); }
  fill(c) { const d = this.d; for (let i = 0; i < d.length; i += 4) { d[i] = c[0]; d[i + 1] = c[1]; d[i + 2] = c[2]; d[i + 3] = 255; } }
  px(x, y, c) {
    x = Math.floor(x); y = Math.floor(y);
    if (x < 0 || y < 0 || x >= this.w || y >= this.h) return;
    const i = (y * this.w + x) * 4, d = this.d;
    d[i] = c[0]; d[i + 1] = c[1]; d[i + 2] = c[2]; d[i + 3] = c.length > 3 ? c[3] : 255;
  }
  rect(c, x, y, w, h) { for (let j = y; j < y + h; j++) for (let i = x; i < x + w; i++) this.px(i, j, c); }
  ell(c, x, y, w, h, outline = false) {
    const rx = w / 2, ry = h / 2, cx = x + rx, cy = y + ry;
    for (let j = Math.floor(y); j < Math.ceil(y + h); j++) for (let i = Math.floor(x); i < Math.ceil(x + w); i++) {
      const dx = (i + 0.5 - cx) / rx, dy = (j + 0.5 - cy) / ry;
      if (dx * dx + dy * dy > 1) continue;
      if (outline && rx > 1 && ry > 1) { const ix = (i + 0.5 - cx) / (rx - 1), iy = (j + 0.5 - cy) / (ry - 1); if (ix * ix + iy * iy <= 1) continue; }
      this.px(i, j, c);
    }
  }
  circ(c, cx, cy, r) { this.ell(c, cx - r, cy - r, 2 * r, 2 * r); }
  poly(c, pts) {
    let y0 = Infinity, y1 = -Infinity;
    for (const p of pts) { y0 = Math.min(y0, p[1]); y1 = Math.max(y1, p[1]); }
    for (let y = Math.floor(y0); y <= Math.ceil(y1); y++) {
      const xs = [], yc = y + 0.5;
      for (let i = 0; i < pts.length; i++) {
        const a = pts[i], b = pts[(i + 1) % pts.length];
        if ((a[1] <= yc && b[1] > yc) || (b[1] <= yc && a[1] > yc)) xs.push(a[0] + ((yc - a[1]) / (b[1] - a[1])) * (b[0] - a[0]));
      }
      xs.sort((p, q) => p - q);
      for (let k = 0; k + 1 < xs.length; k += 2) for (let x = Math.ceil(xs[k] - 0.5); x <= Math.floor(xs[k + 1] - 0.5); x++) this.px(x, y, c);
    }
  }
  line(c, a, b, wd = 1) {
    let x0 = Math.round(a[0]), y0 = Math.round(a[1]); const x1 = Math.round(b[0]), y1 = Math.round(b[1]);
    const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let err = dx + dy;
    for (;;) {
      this.rect(c, x0 - Math.floor(wd / 2), y0 - Math.floor(wd / 2), wd, wd);
      if (x0 === x1 && y0 === y1) break;
      const e2 = 2 * err; if (e2 >= dy) { err += dy; x0 += sx; } if (e2 <= dx) { err += dx; y0 += sy; }
    }
  }
}
const lw = new Pix(240, 160);
let lwCanvas = null, lwCtx = null;
function flushWorld() {
  if (!lwCanvas) { lwCanvas = document.createElement("canvas"); lwCanvas.width = 240; lwCanvas.height = 160; lwCtx = lwCanvas.getContext("2d"); }
  lwCtx.putImageData(new ImageData(lw.d, 240, 160), 0, 0);
  ctx.imageSmoothingEnabled = false; ctx.drawImage(lwCanvas, 0, 0, W, H);
}
const R = (c, x, y, w, h) => lw.rect(c, x, y, w, h);
function tree(x, y, c = LEAF) { R(TRUNK, x + 3, y + 8, 3, 7); lw.circ(c, x + 4, y + 5, 7); lw.circ(shade(c, 35), x + 2, y + 3, 3); }
function palm(x, y, bananas = false) {
  R(TRUNK, x, y, 2, 15);
  for (const [dx, dy] of [[-7, 3], [-5, -1], [0, -3], [5, -1], [7, 3]]) lw.line(LEAF, [x + 1, y], [x + 1 + dx, y + dy + 2], 2);
  R(bananas ? [240, 210, 60] : TRUNK, x - 1, y + 1, 3, 3);
}
function cloud(x, y) { R(WHITE, x + 2, y + 3, 14, 4); R(WHITE, x + 5, y, 8, 5); }
function mountain(x, y, w, h, c = [120, 125, 140]) {
  lw.poly(c, [[x, y + h], [x + w / 2 | 0, y], [x + w, y + h]]);
  lw.poly(WHITE, [[x + w / 2 | 0, y], [(x + w / 2 | 0) - (w / 8 | 0), y + (h / 4 | 0)], [(x + w / 2 | 0) + (w / 8 | 0), y + (h / 4 | 0)]]);
}
function rock(x, y, c = STONE) { R(c, x, y + 2, 6, 4); R(c, x + 1, y, 4, 3); }
function waves(y0, y1, t = 0) {
  R(SEAC, 0, y0, 240, y1 - y0);
  for (let y = y0 + 2; y < y1; y += 7) for (let x = (y * 3 + Math.floor(t / 20)) % 16; x < 240; x += 16) R(SEAL, x, y, 4, 1);
}
function ground(c, c2, y0) {
  R(c, 0, y0, 240, 160 - y0);
  for (let y = y0 + 3; y < 160; y += 6) for (let x = (y * 5) % 9; x < 240; x += 9) R(c2, x, y, 2, 1);
}

function scene(theme, t = 0) {
  lw.fill(SKY); R(SKY2, 0, 30, 240, 26); cloud(30, 14); cloud(150, 22); cloud(205, 8);
  if (theme === "shore") { waves(55, 82, t); ground(SAND, SANDD, 80); palm(18, 62); palm(210, 66); rock(100, 130); rock(150, 140); }
  else if (theme === "bridges") {
    for (const x of [8, 70, 130, 200]) tree(x, 54);
    ground(GRASS, GRASS2, 72); waves(90, 108, t);
    for (const [x, c] of [[26, WOODC], [170, STONE]]) {
      R(c, x, 88, 26, 22);
      for (let yy = 90; yy < 110; yy += 4) R(c === WOODC ? WOODD : [110, 110, 120], x, yy, 26, 1);
      R(c === WOODC ? LEAF : [130, 130, 140], x, 88, 26, 3);
    }
  } else if (theme === "tide") {
    waves(52, 72, t); ground(SAND, SANDD, 70);
    for (const [x, y, w] of [[24, 104, 40], [110, 116, 50], [180, 98, 32]]) { lw.ell(SEAC, x - 2, y - 1, w + 4, 16); lw.ell(SEAL, x, y, w, 12); }
    for (const [x, y] of [[20, 100], [68, 112], [104, 120], [166, 104], [214, 112]]) rock(x, y);
  } else if (theme === "rope") {
    for (const x of [10, 90, 160]) mountain(x, 26, 80, 46);
    ground(GRASS, GRASS2, 72); R(DARKC, 80, 72, 80, 88); R([70, 50, 40], 76, 72, 4, 88); R([70, 50, 40], 160, 72, 4, 88); R(WOODD, 76, 92, 88, 4);
    for (let x = 78; x < 164; x += 4) R(WOODC, x, 92, 2, 4);
    R(TRUNK, 76, 85, 88, 1); R(TRUNK, 76, 84, 2, 10); R(TRUNK, 162, 84, 2, 10);
  } else if (theme === "cave") {
    mountain(0, 18, 120, 62, [110, 115, 130]); mountain(110, 26, 130, 54, [130, 135, 150]); ground(GRASS, GRASS2, 80);
    lw.circ(DARKC, 118, 78, 20); R(GRASS, 98, 78, 40, 4); R(DARKC, 98, 66, 40, 14); rock(80, 86); rock(150, 90);
  } else if (theme === "jungle") {
    ground(GRASS2, LEAFD, 60);
    for (let x = 0; x < 240; x += 20) tree(x, 36 + (x % 3) * 5, LEAFD);
    for (const x of [50, 100, 170]) palm(x, 66, true);
  } else if (theme === "temple") {
    mountain(120, 20, 120, 60, [120, 125, 140]); ground(GRASS, GRASS2, 84); R(STONE, 70, 40, 100, 46); R([110, 110, 120], 64, 34, 112, 8);
    for (const x of [76, 98, 136, 156]) R([190, 190, 200], x, 42, 6, 44);
    R(DARKC, 110, 58, 20, 28);
    for (let i = 0; i < 4; i++) R([170, 170, 180], 62 - i * 3, 86 + i * 3, 116 + i * 6, 3);
    R(LEAF, 70, 40, 3, 20); R(LEAF, 165, 42, 3, 26);
  } else if (theme === "marsh") {
    lw.fill([150, 170, 170]); R([175, 195, 195], 0, 20, 240, 40); ground([78, 112, 92], [58, 92, 72], 66);
    for (const [x, y, w] of [[20, 100, 46], [100, 112, 56], [170, 96, 40]]) lw.ell([96, 140, 150], x, y, w, 12);
    for (let x = 6; x < 240; x += 20) { R([54, 92, 60], x, 60 + (x % 7), 1, 18); R([54, 92, 60], x + 2, 58 + (x % 5), 1, 18); }
    for (const x of [30, 120, 200]) { R(TRUNK, x, 50, 2, 30); R(TRUNK, x - 4, 56, 10, 1); }
  } else if (theme === "dock") {
    waves(55, 160, t); R(WOODC, 0, 92, 240, 16);
    for (let x = 0; x < 240; x += 8) R(WOODD, x, 92, 1, 16);
    for (const x of [10, 90, 170, 230]) R(WOODD, x, 108, 3, 20);
    lw.poly(WOODD, [[140, 70], [200, 70], [190, 82], [150, 82]]); R(TRUNK, 168, 46, 2, 24); lw.poly(WHITE, [[171, 48], [171, 66], [190, 66]]);
  }
  flushWorld();
}

// ------------------------------------------------------------------ pixel characters
const _sp = {};
function sprite(kind, col) {
  const key = kind + col.join(",");
  if (_sp[key]) return _sp[key];
  const s = new Pix(32, 32), OUT = [45, 28, 20], dark = shade(col, -60), light = shade(col, 50);
  const el = (c, x, y, w, h, o) => s.ell(c, x, y, w, h, !!o), rc = (c, x, y, w, h) => s.rect(c, x, y, w, h), pl = (c, p) => s.poly(c, p);
  el([0, 0, 0, 70], 6, 28, 20, 3);
  if (kind === "player" || kind === "captain") {
    const shirt = kind === "player" ? [200, 60, 60] : [40, 70, 130];
    rc(shirt, 10, 20, 12, 8); rc(OUT, 10, 20, 12, 1); rc([90, 60, 40], 11, 28, 4, 2); rc([90, 60, 40], 17, 28, 4, 2);
    el(col, 9, 6, 14, 15); el(OUT, 9, 6, 14, 15, 1);
    rc(WHITE, 12, 13, 3, 3); rc(WHITE, 18, 13, 3, 3); rc(OUT, 13, 14, 1, 2); rc(OUT, 19, 14, 1, 2); rc(OUT, 14, 18, 4, 1);
    if (kind === "player") { el(GOLD, 4, 5, 24, 5); el(GOLD, 10, 1, 12, 8); rc([190, 60, 40], 10, 6, 12, 1); }
    else { pl([30, 40, 70], [[5, 8], [16, 0], [27, 8]]); rc(GOLD, 5, 8, 22, 1); }
  } else {
    if (kind === "crab") for (const cx of [1, 25]) { el(col, cx, 6, 7, 7); el(OUT, cx, 6, 7, 7, 1); }
    if (kind === "fox") for (const sx of [1, -1]) { const x0 = sx === 1 ? 8 : 24; pl(col, [[x0, 11], [x0 + 3 * sx, 1], [x0 + 7 * sx, 11]]); }
    if (kind === "monkey" || kind === "gorilla") for (const cx of [2, 24]) { el(light, cx, 11, 6, 6); el(OUT, cx, 11, 6, 6, 1); }
    if (kind === "turtle") { el(dark, 3, 14, 26, 15); el(OUT, 3, 14, 26, 15, 1); }
    if (kind === "parrot") for (const dx of [-3, 0, 3]) s.line([220, 50, 50], [16, 8], [16 + dx, 2], 2);
    el(col, 6, 8, 20, 20); el(OUT, 6, 8, 20, 20, 1);
    if (kind === "monkey" || kind === "gorilla") el(light, 9, 15, 14, 11);
    if (kind === "fox") el([250, 240, 225], 9, 18, 14, 9);
    if (kind === "turtle") for (const [x, y] of [[9, 21], [15, 19], [21, 21]]) rc(dark, x, y, 3, 3);
    for (const ex of [11, 19]) { rc(WHITE, ex, 14, 3, 3); rc(OUT, ex + 1, 15, 1, 2); }
    if (kind === "gorilla") rc(OUT, 10, 12, 12, 1);
    if (kind === "gull" || kind === "parrot") pl([250, 160, 30], [[14, 19], [18, 19], [16, 24]]); else rc(OUT, 14, 22, 4, 1);
  }
  const cv = document.createElement("canvas"); cv.width = 32; cv.height = 32;
  cv.getContext("2d").putImageData(new ImageData(s.d, 32, 32), 0, 0);
  return (_sp[key] = cv);
}
function drawChar(cx, feet, kind, col, k = 6) { ctx.imageSmoothingEnabled = false; ctx.drawImage(sprite(kind, col), cx - 16 * k, feet - 30 * k, 32 * k, 32 * k); }
const CHARS = {
  "You": ["player", [240, 190, 140]], "Gus the Gull": ["gull", [225, 230, 240]], "Penny the Pelican": ["gull", [255, 215, 190]],
  "Tess the Turtle": ["turtle", [90, 170, 100]], "Sheldon the Snapper": ["turtle", [80, 120, 165]], "Clara the Crab": ["crab", [225, 90, 70]],
  "Pete the Parrot": ["parrot", [70, 170, 90]], "Kiki the Kiwi": ["parrot", [150, 100, 200]], "Fenwick the Fox": ["fox", [225, 130, 50]],
  "Rusty the Raccoon": ["fox", [150, 150, 165]], "Moe the Monkey": ["monkey", [150, 100, 60]], "Bongo the Baboon": ["monkey", [190, 130, 90]],
  "Grizelda the Gorilla": ["gorilla", [85, 85, 100]], "Gorg the Gorilla": ["gorilla", [60, 110, 75]], "Captain Nash": ["captain", [235, 195, 150]],
};
const char = (n, cx, feet, k) => drawChar(cx, feet, CHARS[n][0], CHARS[n][1], k);

// ------------------------------------------------------------------ game-theory helpers
function nash(pay) {
  const Rn = pay.length, Cn = pay[0].length, out = [];
  for (let r = 0; r < Rn; r++) for (let c = 0; c < Cn; c++) {
    let ok = true;
    for (let r2 = 0; r2 < Rn; r2++) if (pay[r2][c][0] > pay[r][c][0]) ok = false;
    for (let c2 = 0; c2 < Cn; c2++) if (pay[r][c2][1] > pay[r][c][1]) ok = false;
    if (ok) out.push([r, c]);
  }
  return out;
}
const mdims = (pay, maxw = 520, maxh = 190) => [Math.min(190, Math.floor(maxw / pay[0].length)), Math.min(95, Math.floor(maxh / pay.length))];
const cellRect = (x, y, cw, ch, r, c) => [x + c * cw, y + r * ch, cw, ch];
const has = (list, r, c) => list.some(p => p[0] === r && p[1] === c);

function numAt(s, sz, col, cx, cy, bold) {
  ctx.font = font(sz, bold); ctx.fillStyle = css(col); ctx.textBaseline = "middle"; ctx.textAlign = "center"; ctx.fillText(s, cx, cy);
  return ctx.measureText(s).width;
}
function drawMatrix(pay, rows, cols, x, y, cw, ch, hint = false, last = null, sel = [], deadR = [], deadC = []) {
  const Rn = rows.length, Cn = cols.length, big = cw >= 120, f = big ? 26 : 20, lf = big ? 26 : 18;
  const ar = [...Array(Rn).keys()].filter(r => !deadR.includes(r)), ac = [...Array(Cn).keys()].filter(c => !deadC.includes(c));
  for (let c = 0; c < Cn; c++) text(cols[c], lf, deadC.includes(c) ? GREY : INK, x + c * cw + cw / 2, y - 32, { bold: true, center: true });
  for (let r = 0; r < Rn; r++) {
    ctx.font = font(lf, true); ctx.fillStyle = css(deadR.includes(r) ? GREY : INK); ctx.textAlign = "right"; ctx.textBaseline = "middle";
    ctx.fillText(rows[r], x - 10, y + r * ch + ch / 2);
  }
  for (let r = 0; r < Rn; r++) for (let c = 0; c < Cn; c++) {
    const [rx, ry] = cellRect(x, y, cw, ch, r, c), dead = deadR.includes(r) || deadC.includes(c);
    fr(dead ? [200, 190, 175] : has(sel, r, c) ? [255, 225, 140] : [255, 248, 228], rx, ry, cw, ch); sr(INK, rx, ry, cw, ch, 3);
    const [a, b] = pay[r][c], cy = ry + ch / 2, ax = rx + cw / 2 - Math.floor(cw / 4), bx = rx + cw / 2 + Math.floor(cw / 4);
    const wa = numAt(fmt(a), f, dead ? GREY : BLUE, ax, cy, true), wb = numAt(fmt(b), f, dead ? GREY : RED, bx, cy, true);
    numAt(",", f, INK, rx + cw / 2, cy + 2, true);
    if (hint && !dead) {
      if (a === Math.max(...ar.map(rr => pay[rr][c][0]))) ln(BLUE, ax - wa / 2 - 3, cy + f * 0.6 + 3, ax + wa / 2 + 3, cy + f * 0.6 + 3, 4);
      if (b === Math.max(...ac.map(cc => pay[r][cc][1]))) ln(RED, bx - wb / 2 - 3, cy + f * 0.6 + 3, bx + wb / 2 + 3, cy + f * 0.6 + 3, 4);
    }
    if (last && last[0] === r && last[1] === c) sr(GOLD, rx, ry, cw, ch, 6);
  }
}

function dominated(pay, ar, ac, player, i, weak, mixed) {
  const mine = player === 0 ? ar : ac, opp = player === 0 ? ac : ar;
  const u = (a, o) => (player === 0 ? pay[a][o][0] : pay[o][a][1]);
  const others = mine.filter(j => j !== i);
  for (const j of others) {
    const d = opp.map(o => u(j, o) - u(i, o));
    if ((weak && d.every(x => x >= 0) && d.some(x => x > 0)) || (!weak && d.every(x => x > 0))) return ["pure", j];
  }
  if (mixed) for (const a of others) for (const b of others) if (a < b) for (let k = 1; k < 10; k++) {
    const q = k / 10;
    if (opp.every(o => q * u(a, o) + (1 - q) * u(b, o) - u(i, o) > 1e-9)) return ["mix", [a, b, q]];
  }
  return null;
}

// ------------------------------------------------------------------ extensive-form trees
function normTree(n) { return Array.isArray(n) ? { u: n } : (n.u ? n : { n: n.n, p: n.p, a: n.a.map(([l, c]) => [l, normTree(c)]) }); }
const nLeaves = n => (n.u ? 1 : n.a.reduce((s, [, c]) => s + nLeaves(c), 0));
const height = n => (n.u ? 0 : 1 + Math.max(...n.a.map(([, c]) => height(c))));
function layout(root, x0, x1, y0, y1) {
  const pos = new Map(), nl = nLeaves(root), h = height(root); let cnt = 0;
  (function rec(n, d) {
    let x, y;
    if (n.u) { x = x0 + (cnt + 0.5) * (x1 - x0) / nl; y = y1; cnt++; }
    else { const xs = n.a.map(([, c]) => rec(c, d + 1)); x = (xs[0] + xs[xs.length - 1]) / 2; y = y0 + d * (y1 - y0) / Math.max(1, h); }
    pos.set(n, [Math.floor(x), Math.floor(y)]); return x;
  })(root, 0);
  return pos;
}
function drawTree(root, names, pos, chosen = new Map(), cur = null) {
  (function edges(n) { if (n.u) return; n.a.forEach(([l, c], j) => { const a = pos.get(n), b = pos.get(c), on = chosen.get(n) === j; ln(on ? GREEN : INK, a[0], a[1], b[0], b[1], on ? 7 : 3); edges(c); }); })(root);
  (function labels(n) {
    if (n.u) return;
    for (const [l, c] of n.a) {
      const a = pos.get(n), b = pos.get(c), w = tw(l, 14, true) + 8, cx = (a[0] + b[0]) / 2, cy = (a[1] + b[1]) / 2;
      fr(CREAM, cx - w / 2, cy - 10, w, 20); text(l, 14, INK, cx, cy - 8, { bold: true, center: true }); labels(c);
    }
  })(root);
  (function nodes(n) {
    const [x, y] = pos.get(n);
    if (n.u) {
      fr(GOLD, x - 8, y - 8, 16, 16); sr(INK, x - 8, y - 8, 16, 16, 2);
      const [a, b] = n.u, sa = fmt(a), sb = fmt(b), wa = tw(sa, 15, true), wc = tw(",", 15, true), wb = tw(sb, 15, true), x0 = x - (wa + wc + wb) / 2;
      ctx.textAlign = "left"; text(sa, 15, BLUE, x0, y + 11, { bold: true }); text(",", 15, INK, x0 + wa, y + 11, { bold: true }); text(sb, 15, RED, x0 + wa + wc, y + 11, { bold: true });
      return;
    }
    n.a.forEach(([, c]) => nodes(c));
    if (cur === n) fc(GOLD, x, y, 25);
    fc(INK, x, y, 21); fc(n.p === 0 ? BLUE : RED, x, y, 18); text(n.n, 16, WHITE, x, y - 10, { bold: true, center: true });
  })(root);
  text(`blue = ${names[0]}     red = ${names[1]}`, 16, INK, 70, 150);
}

// ------------------------------------------------------------------ quiz extras
function drawExtra(ex, qi, sc) {
  if (!ex) return;
  if (ex.k === "matrix") {
    const [cw, ch] = mdims(ex.pay, 520, 170);
    drawMatrix(ex.pay, ex.rows, ex.cols, 480 - cw * ex.cols.length / 2, 195, cw, ch, true);
    text("blue = you, red = them. Underlines mark best replies.", 16, INK, 250, 384);
  } else if (ex.k === "info") fit(ex.lines[Math.min(qi, ex.lines.length - 1)], [80, 150, 800, 235], { sizes: [22, 20, 18, 16] });
  else if (ex.k === "tree") {
    if (!ex._root) { ex._root = normTree(ex.tree); ex._pos = layout(ex._root, 90, 870, 190, 330); }
    drawTree(ex._root, ex.names, ex._pos);
  } else if (ex.k === "boss") {
    char("Captain Nash", 790, 392, 4);
    sr(INK, 620, 150, 280, 24, 3); fr(RED, 623, 153, Math.floor(274 * Math.max(0, sc.hp) / sc.n), 18);
    text(`Captain Nash HP ${Math.max(0, sc.hp)}/${sc.n}`, 14, INK, 620, 176, { bold: true });
    for (let i = 0; i < sc.maxh; i++) { fr(i < sc.hearts ? RED : GREY, 620 + i * 30, 200, 22, 22); sr(INK, 620 + i * 30, 200, 22, 22, 2); }
    fit("BOSS FIGHT! Every correct answer hits Captain Nash. Every wrong answer costs you a heart. Lose all your hearts and you must start the duel over with new questions.", [60, 160, 520, 150], { sizes: [24, 22, 20, 18] });
  }
}

// ------------------------------------------------------------------ scenes (each: event(ev), draw(), done)
class SDialogue {
  constructor(sp) {
    this.sp = sp; this.i = 0; this.done = false; this.enemy = sp.enemy; this.theme = sp.theme;
    this.lines = sp.praise ? [[sp.enemy, CONTENT.praise[rnd(CONTENT.praise.length)]]] : sp.lines;
    const L = sp.links || [], n = L.length, w = Math.min(280, Math.floor(650 / Math.max(1, n)) - 6);
    this.lb = L.map((l, i) => [new Button([170 + i * (w + 6), 8, w, 36], (n <= 2 ? "Watch: " : "") + l[0], DRED), l[1]]);
  }
  event(ev) {
    for (const [b, u] of this.lb) if (b.hit(ev)) { window.open(u, "_blank"); return; }
    if (ev.type === "down" || (ev.type === "key" && (ev.key === " " || ev.key === "Enter"))) { this.i++; this.done = this.i >= this.lines.length; }
  }
  draw() {
    scene(this.theme, TICK);
    const [who, line] = this.lines[Math.min(this.i, this.lines.length - 1)];
    if (this.enemy) char(this.enemy, 190, 405, who === this.enemy ? 7 : 6);
    char("You", 780, 405, who === "You" ? 7 : 6);
    panel([30, 415, 900, 205]); text(who, 26, [150, 80, 20], 56, 430, { bold: true });
    fit(line, [56, 465, 848, 118], { sizes: [23, 21, 19, 17, 15, 13] });
    text("tap / click / SPACE to continue", 14, GREY, 690, 590);
    this.lb.forEach(([b]) => b.draw());
  }
}

class SQuiz {
  constructor(sp) {
    this.sp = sp; this.title = sp.title; this.theme = sp.theme; this.qs = sp.qs; this.extra = sp.extra; this.qi = 0; this.state = "ask"; this.done = false; this.choose = !!sp.optional;
    this.next = new Button([700, 560, 200, 44], "Continue", GREENB);
    this.take = new Button([110, 330, 360, 70], "Take the quiz (recommended)", GREENB); this.skip = new Button([490, 330, 360, 70], "Skip the quiz", PURP);
    this.mk();
  }
  mk() { const q = this.qs[this.qi]; this.order = shuffle([...q.opts.keys()]); this.btns = this.order.map((j, i) => new Button([60, 410 + i * 52, 840, 44], q.opts[j])); }
  event(ev) {
    if (this.choose) { if (this.take.hit(ev)) this.choose = false; else if (this.skip.hit(ev)) this.done = true; return; }
    if (this.state === "ask") this.btns.forEach((b, i) => { if (b.hit(ev)) this.state = this.order[i] === this.qs[this.qi].ans ? "right" : "wrong"; });
    else if (this.next.hit(ev)) {
      if (this.state === "right") { this.qi++; if (this.qi >= this.qs.length) { this.done = true; return; } }
      this.mk(); this.state = "ask";
    }
  }
  draw() {
    scene(this.theme, TICK); panel([30, 12, 900, 616]); FB(this.title, INK, 50, 24);
    if (this.choose) {
      fit("Quiz time! A few quick questions check what you just learned. The quiz is OPTIONAL: take it to test yourself, or skip it and keep playing.", [80, 120, 800, 160], { sizes: [26, 24, 22, 20], center: true });
      this.take.draw(); this.skip.draw(); return;
    }
    const q = this.qs[this.qi];
    fit(`Q${this.qi + 1}/${this.qs.length}   ` + q.q, [50, 60, 860, 74], { sizes: [22, 20, 18, 16] });
    drawExtra(this.extra, this.qi, this);
    if (this.state === "ask") this.btns.forEach(b => b.draw());
    else {
      panel([50, 405, 860, 205], WHITE); const ok = this.state === "right";
      FB(ok ? "Correct!" : "Not quite.", ok ? GREEN : RED, 72, 424);
      fit(ok ? q.why : q.hint, [72, 460, 816, 96], { sizes: [22, 20, 18, 16, 14] });
      this.next.label = ok ? "Continue" : "Try again"; this.next.draw();
    }
  }
}

class SBoss extends SQuiz {
  constructor(sp) {
    super({ title: sp.title, theme: sp.theme, qs: shuffle([...sp.pool]).slice(0, sp.n), extra: { k: "boss" }, optional: false });
    this.pool = sp.pool; this.n = sp.n; this.maxh = 3; this.hp = sp.n; this.hearts = 3; this.lost = false;
    this.retry = new Button([330, 375, 300, 56], "Rematch!", GREENB);
  }
  restart() { this.qs = shuffle([...this.pool]).slice(0, this.n); this.qi = 0; this.state = "ask"; this.hp = this.n; this.hearts = this.maxh; this.lost = false; this.mk(); }
  event(ev) {
    if (this.lost) { if (this.retry.hit(ev)) this.restart(); return; }
    const prev = this.state; super.event(ev);
    if (prev === "ask" && this.state === "wrong") { this.hearts--; if (this.hearts <= 0) this.lost = true; }
    if (prev === "ask" && this.state === "right") this.hp--;
  }
  draw() {
    super.draw();
    if (this.lost) {
      panel([200, 250, 560, 200]); FB("The boss wins this round!", RED, 480, 270, { center: true });
      fit("You ran out of hearts. Review the lectures (links are on each level's title card) and try again with new questions.", [230, 315, 500, 56], { center: true, sizes: [19, 17] });
      this.retry.draw();
    }
  }
}

const ENEMY = {
  random: () => rnd(2), moe: (h, i, t) => (i === t - 1 || h.some(x => x[0] === 1) ? 1 : 0), grim: h => (h.some(x => x[0] === 1) ? 1 : 0),
  tft: h => (h.length ? h[h.length - 1][0] : 0), rpsbias: () => { const r = Math.random(); return r < 0.6 ? 0 : r < 0.8 ? 1 : 2; },
};
const MOOD = { grim: h => (h.some(x => x[0] === 1) ? ["FURIOUS (grim trigger pulled)", RED] : ["trusting", GREEN]), tft: h => ["copying your last move", !h.length || h[h.length - 1][0] === 0 ? GREEN : RED] };

class SPlay {
  constructor(sp) {
    this.c = sp.cfg; this.total = this.c.rounds; this.done = false; this.hint = false;
    this.win = this.c.win === "avg25" ? (sc, n) => sc[0] / Math.max(1, n) >= 2.5 : (sc, n) => sc[0] >= sc[1];
    const e = this.c.enemy; this.enemyFn = e.k === "always" ? () => e.c : ENEMY[e.k];
    const Rn = this.c.rows.length, w = Math.min(180, Math.floor(380 / Rn) - 8);
    this.rb = this.c.rows.map((n, i) => new Button([170 + i * (w + 8), 470, w, 48], "Play " + n));
    this.hb = new Button([170, 548, 370, 40], "Toggle: show best replies", PURP); this.cont = new Button([170, 470, 370, 50], "Continue", GREENB);
    this.reset();
  }
  reset() { this.hist = []; this.sc = [0, 0]; this.last = null; this.over = false; }
  event(ev) {
    if (this.hb.hit(ev)) this.hint = !this.hint;
    if (this.over) { if (this.cont.hit(ev)) { if (this.win(this.sc, this.hist.length)) this.done = true; else this.reset(); } return; }
    this.rb.forEach((b, r) => {
      if (!b.hit(ev)) return;
      const c = this.enemyFn(this.hist, this.hist.length, this.total), [a, e] = this.c.pay[r][c];
      this.sc[0] += a; this.sc[1] += e; this.hist.push([r, c]); this.last = [r, c];
      const n = this.hist.length; this.over = this.total ? n >= this.total : (n >= 25 || (n >= 6 && Math.random() > 0.9));
    });
  }
  draw() {
    const c = this.c; scene(c.theme, TICK); panel([30, 12, 900, 616]); FB(c.title, INK, 50, 24);
    fit(c.tip, [50, 58, 860, 40], { sizes: [18, 16, 14] }); fit(c.goal, [50, 100, 860, 24], { col: GREEN, sizes: [18, 16, 14], bold: true });
    const [cw, ch] = mdims(c.pay, 400, 190); drawMatrix(c.pay, c.rows, c.cols, 170, 195, cw, ch, this.hint, this.last);
    text("blue = YOU        red = " + c.short, 16, INK, 170, 398);
    const n = this.hist.length;
    if (this.total) FB(`Round ${Math.min(n + 1, this.total)} of ${this.total}`, INK, 610, 140);
    else fit(`Round ${n + 1}  (each round has a 90% chance of another)`, [610, 140, 290, 40], { sizes: [20, 16] });
    FM(`You: ${fmt(this.sc[0])}      ${c.short}: ${fmt(this.sc[1])}`, INK, 610, 180);
    if (!this.total) FM(`Your average: ${(this.sc[0] / Math.max(1, n)).toFixed(2)} per round`, INK, 610, 210);
    if (c.mood) { const [m, mc] = MOOD[c.mood](this.hist); fit(c.short + " feels: " + m, [610, 240, 290, 40], { col: mc, sizes: [20, 16] }); }
    FS("Recent rounds:", INK, 610, 290);
    this.hist.map((h, i) => [i, h]).slice(-6).forEach(([i, [r, cc]], k) => { const [a, e] = c.pay[r][cc]; text(`R${i + 1}: you ${c.rows[r]} / they ${c.cols[cc]}  (${fmt(a)} / ${fmt(e)})`, 15, INK, 610, 312 + k * 22); });
    if (this.over) {
      const ok = this.win(this.sc, n);
      fit(ok ? "You win or tie! Well played." : "You lost this match. Think again and retry.", [170, 420, 400, 40], { col: ok ? GREEN : RED, sizes: [22, 18], bold: true });
      this.cont.label = ok ? "Continue" : "Retry the match"; this.cont.draw();
    } else this.rb.forEach(b => b.draw());
    this.hb.draw();
  }
}

class SNash {
  constructor(sp) {
    this.c = sp.cfg; this.sel = []; this.msg = ""; this.ok = false; this.done = false; this.hint = false;
    this.chk = new Button([250, 500, 200, 46], "Check", GREENB); this.hb = new Button([470, 500, 200, 46], "Show best replies", PURP);
    [this.cw, this.ch] = mdims(this.c.pay, 540, 230);
  }
  event(ev) {
    const c = this.c;
    if (this.hb.hit(ev)) this.hint = !this.hint;
    if (ev.type === "down" && !this.ok) for (let r = 0; r < c.rows.length; r++) for (let cc = 0; cc < c.cols.length; cc++)
      if (inR(ev.x, ev.y, cellRect(250, 200, this.cw, this.ch, r, cc))) { const i = this.sel.findIndex(p => p[0] === r && p[1] === cc); if (i >= 0) this.sel.splice(i, 1); else this.sel.push([r, cc]); }
    if (this.chk.hit(ev)) {
      if (this.ok) { this.done = true; return; }
      const N = nash(c.pay), p = c.pay, wrong = this.sel.filter(s => !has(N, s[0], s[1])).sort(), missing = N.filter(n => !has(this.sel, n[0], n[1]));
      if (!this.sel.length) this.msg = "Click the cell(s) you think are pure-strategy Nash equilibria first.";
      else if (wrong.length) {
        const [r, cc] = wrong[0], better = c.rows.map((_, r2) => r2).filter(r2 => p[r2][cc][0] > p[r][cc][0]); let why;
        if (better.length) why = `you'd gain by switching to ${c.rows[better[0]]}`;
        else { const c2 = c.cols.map((_, k) => k).filter(k => p[r][k][1] > p[r][cc][1])[0]; why = `they'd gain by switching to ${c.cols[c2]}`; }
        this.msg = `Not quite. In (${c.rows[r]}, ${c.cols[cc]}) ${why}, so someone wants to deviate.`;
      } else if (missing.length) this.msg = `Right so far, but there are ${N.length} pure equilibria in total. Keep looking!`;
      else { this.ok = true; this.msg = c.ok || "Correct! In every selected cell, nobody can gain by changing ONLY their own choice."; this.chk.label = "Continue"; }
    }
  }
  draw() {
    const c = this.c; scene(c.theme, TICK); panel([30, 12, 900, 616]); FB(c.title, INK, 50, 24);
    fit("Click every cell that is a pure-strategy Nash equilibrium (each strategy is a best reply to the other), then press Check.", [50, 60, 860, 52], { sizes: [22, 20, 18] });
    drawMatrix(c.pay, c.rows, c.cols, 250, 200, this.cw, this.ch, this.hint, null, this.sel);
    FS("blue = you      red = them", INK, 250, 438);
    fit(this.msg, [250, 458, 620, 36], { col: this.ok ? GREEN : RED, sizes: [18, 16, 14] });
    this.chk.draw(); this.hb.draw();
  }
}

class SElim {
  constructor(sp) {
    this.c = sp.cfg; this.ar = this.c.rows.map((_, i) => i); this.ac = this.c.cols.map((_, i) => i); this.msg = ""; this.done = false; this.hint = false;
    [this.cw, this.ch] = mdims(this.c.pay, 540, 230);
    this.hb = new Button([600, 548, 300, 40], "Toggle: show best replies", PURP); this.fin = new Button([600, 490, 300, 46], "Finish", GREENB);
  }
  anyLeft() {
    const c = this.c;
    for (const i of this.ar) if (this.ar.length > 1 && dominated(c.pay, this.ar, this.ac, 0, i, !!c.weak, !!c.mixed)) return true;
    for (const j of this.ac) if (this.ac.length > 1 && dominated(c.pay, this.ar, this.ac, 1, j, !!c.weak, !!c.mixed)) return true;
    return false;
  }
  event(ev) {
    const c = this.c;
    if (this.hb.hit(ev)) this.hint = !this.hint;
    if (!this.anyLeft() && this.fin.hit(ev)) this.done = true;
    if (ev.type !== "down") return;
    let target = null;
    for (const r of this.ar) if (inR(ev.x, ev.y, [120, 200 + r * this.ch, 120, this.ch])) target = [0, r];
    for (const cc of this.ac) if (inR(ev.x, ev.y, [250 + cc * this.cw, 160, this.cw, 38])) target = [1, cc];
    if (!target) return;
    const [pl, i] = target, names = pl === 0 ? c.rows : c.cols, alive = pl === 0 ? this.ar : this.ac;
    if (alive.length < 2) { this.msg = "Only one strategy is left for that player."; return; }
    const res = dominated(c.pay, this.ar, this.ac, pl, i, !!c.weak, !!c.mixed), kind = c.weak ? "weakly " : "strictly ";
    if (res) {
      if (res[0] === "pure") this.msg = `Yes! ${names[i]} is ${kind}dominated by ${names[res[1]]}. Deleted.`;
      else { const [a, b, q] = res[1]; this.msg = `Yes! A ${Math.round(q * 100)}/${Math.round(100 - q * 100)} mix of ${names[a]} and ${names[b]} strictly beats ${names[i]}. Deleted.`; }
      alive.splice(alive.indexOf(i), 1);
      if (!this.anyLeft()) this.msg += " " + (c.stuck || "Nothing else can be deleted.");
    } else this.msg = `No: ${names[i]} is not ${kind}dominated by anything left. Look for a strategy that is worse than another one in EVERY remaining column/row.`;
  }
  draw() {
    const c = this.c; scene(c.theme, TICK); panel([30, 12, 900, 616]); FB(c.title, INK, 50, 24); fit(c.tip, [50, 60, 860, 52], { sizes: [20, 18, 16] });
    const dr = c.rows.map((_, i) => i).filter(i => !this.ar.includes(i)), dc = c.cols.map((_, i) => i).filter(i => !this.ac.includes(i));
    drawMatrix(c.pay, c.rows, c.cols, 250, 200, this.cw, this.ch, this.hint, null, [], dr, dc);
    FS("blue = you      red = them      (click a strategy NAME to delete it)", INK, 150, 440);
    fit(this.msg, [60, 462, 520, 130], { col: this.msg.startsWith("Yes") ? GREEN : RED, sizes: [20, 18, 16, 14] });
    if (!this.anyLeft()) this.fin.draw();
    this.hb.draw();
  }
}

const PAD_KEYS = [["7", "8", "9", "<"], ["4", "5", "6", "/"], ["1", "2", "3", "."], ["0", "-", "NEXT", "CLOSE"]];
const WRONG = {
  pen_p: v => `At p = ${fmt(Math.round(v[0] * 1000) / 1000)}: against Heads you get ${(3 * v[0] - 1).toFixed(2)}, against Tails ${(1 - 2 * v[0]).toFixed(2)}. They must be EQUAL.`,
  pen_q: v => `At q = ${fmt(Math.round(v[0] * 1000) / 1000)}: Heads earns you ${(3 * v[0] - 1).toFixed(2)}, Tails earns you ${(1 - 2 * v[0]).toFixed(2)}. They must be EQUAL.`,
  bos: v => `Column gets ${v[0].toFixed(2)} from Opera vs ${(2 * (1 - v[0])).toFixed(2)} from Football. Row gets ${(2 * v[1]).toFixed(2)} from Opera vs ${(1 - v[1]).toFixed(2)} from Football. Each pair must be EQUAL.`,
  gbos: v => `Column: Opera ${v[0].toFixed(2)} vs Football ${(3 * (1 - v[0])).toFixed(2)}. Row: Opera ${(4 * v[1]).toFixed(2)} vs Football ${(2 * (1 - v[1])).toFixed(2)}. Each pair must be EQUAL.`,
  pen1: v => `Goalie: dive Left ${(5 * v[0] + (1 - v[0])).toFixed(2)} vs dive Right ${(3 * v[0] + 4 * (1 - v[0])).toFixed(2)}. Kicker: Left ${(5 * v[1] + 7 * (1 - v[1])).toFixed(2)} vs Right ${(9 * v[1] + 6 * (1 - v[1])).toFixed(2)}. Each pair must be EQUAL.`,
  pen2: v => `Goalie: dive Left ${(7 * v[0] + (1 - v[0])).toFixed(2)} vs dive Right ${(3 * v[0] + 4 * (1 - v[0])).toFixed(2)}. Kicker: Left ${(5 * v[1] + 7 * (1 - v[1])).toFixed(2)} vs Right ${(9 * v[1] + 6 * (1 - v[1])).toFixed(2)}.`,
  mrps: v => `Against your guess the actions earn: Rock ${(-v[1] + 2 * v[2]).toFixed(2)}, Paper ${(v[0] - v[2]).toFixed(2)}, Scissors ${(-2 * v[0] + v[1]).toFixed(2)}. All must be equal (0), and r + p + s = ${(v[0] + v[1] + v[2]).toFixed(2)} must be 1.`,
};
function parseNum(s) {
  s = s.trim();
  const one = x => (/^[+-]?(\d+\.?\d*|\.\d+)$/.test(x) ? parseFloat(x) : NaN);
  if (s.includes("/")) { const i = s.indexOf("/"); const a = one(s.slice(0, i)), b = one(s.slice(i + 1)); return b === 0 ? NaN : a / b; }
  return one(s);
}

class SCalc {
  constructor(sp) {
    this.theme = sp.theme; this.title = sp.title; this.P = sp.problems; this.pages = sp.pages || []; this.phase = this.pages.length ? "learn" : "solve"; this.pg = 0; this.pi = 0; this.done = false;
    this.nextb = new Button([700, 545, 200, 44], "Next", GREENB); this.sub = new Button([700, 400, 200, 44], "Check answer", GREENB);
    this.hintb = new Button([700, 452, 200, 44], "Hint", PURP); this.padb = new Button([580, 452, 110, 44], "Keypad", WOOD);
    this.cont = new Button([700, 504, 200, 44], "Continue", GREENB); this.padchk = new Button([300, 548, 376, 40], "Check answer", GREENB);
    this.start();
  }
  start() { const p = this.P[this.pi]; this.vals = p.fields.map(() => ""); this.focus = 0; this.msg = ""; this.hints = 0; this.solved = false; this.net = 0; this.n = 0; this.last = ""; this.pad = false; }
  box(i) { return [430, 398 + i * 50, 130, 42]; }
  padrect(r, c) { return [300 + c * 96, 330 + r * 54, 90, 48]; }
  submit() {
    const p = this.P[this.pi], v = this.vals.map(parseNum);
    if (v.some(x => !Number.isFinite(x))) { this.msg = "Type numbers in every box first (decimals like 0.4 or fractions like 2/5)."; return; }
    if (v.every((a, i) => Math.abs(a - p.fields[i][1]) <= (p.tol || 0.012))) { this.solved = true; this.msg = p.ok || "Correct!"; this.pad = false; }
    else this.msg = p.wrongId ? WRONG[p.wrongId](v) : "Not quite. Re-check your algebra, or use a hint.";
  }
  typeChar(ch) { if (ch === "<") this.vals[this.focus] = this.vals[this.focus].slice(0, -1); else if (this.vals[this.focus].length < 8) this.vals[this.focus] += ch; }
  padClick(ev) {
    PAD_KEYS.forEach((row, r) => row.forEach((k, c) => {
      if (!inR(ev.x, ev.y, this.padrect(r, c))) return;
      if (k === "NEXT") this.focus = (this.focus + 1) % this.vals.length; else if (k === "CLOSE") this.pad = false; else this.typeChar(k);
    }));
    if (this.padchk.hit(ev)) this.submit();
  }
  event(ev) {
    if (this.done || this.pi >= this.P.length) return;
    const p = this.P[this.pi];
    if (this.phase === "learn") {
      if (this.nextb.hit(ev)) { this.pg++; if (this.pg >= this.pages.length) this.phase = "solve"; else if (this.pg === this.pages.length - 1) this.nextb.label = "Let's try!"; }
      return;
    }
    if (!this.solved) {
      if (this.pad && ev.type === "down") { this.padClick(ev); return; }
      if (ev.type === "key") {
        if (ev.key === "Backspace") this.typeChar("<"); else if (ev.key === "Tab") this.focus = (this.focus + 1) % this.vals.length;
        else if (ev.key === "Enter") this.submit(); else if (ev.key.length === 1 && "0123456789./-".includes(ev.key)) this.typeChar(ev.key);
      }
      if (ev.type === "down") this.vals.forEach((_, i) => { if (inR(ev.x, ev.y, this.box(i))) { this.focus = i; if (TOUCH) this.pad = true; } });
      if (this.padb.hit(ev)) this.pad = true;
      if (this.sub.hit(ev)) this.submit();
      if (this.hintb.hit(ev)) this.hints = Math.min((p.hints || []).length, this.hints + 1);
      return;
    }
    let gate = true;
    if (p.throw) {
      const [pay, pp, qq] = p.throw;
      if (this.hintb.hit(ev)) {
        for (let k = 0; k < 20; k++) { const r = Math.random() < pp ? 0 : 1, c = Math.random() < qq ? 0 : 1; this.net += pay[r][c][0]; }
        this.n += 20;
        this.last = `After ${this.n} throws you are at ${fmt(Math.round(this.net * 100) / 100)}. ` + (this.net >= 0 ? "You win or tie, so you can move on!" : "You're behind, but the odds favour you. Keep throwing!");
      }
      gate = this.n >= 20 && this.net >= 0;
    }
    if (gate && this.cont.hit(ev)) { this.pi++; if (this.pi >= this.P.length) this.done = true; else this.start(); }
  }
  draw() {
    scene(this.theme, TICK); panel([30, 12, 900, 616]); FB(this.title, INK, 50, 24);
    if (this.phase === "learn") {
      const [body, mat] = this.pages[this.pg];
      fit(body, [50, 80, mat ? 520 : 860, 420], { sizes: [26, 24, 22, 20, 18] });
      if (mat) { const [pay, rows, cols] = mat, [cw, ch] = mdims(pay, 300, 190); drawMatrix(pay, rows, cols, 650, 190, cols.length > 2 ? cw : 110, rows.length > 2 ? ch : 80); FS("blue = you, red = them", INK, 640, 400); }
      this.nextb.draw(); return;
    }
    const p = this.P[this.pi];
    fit(p.prompt, [50, 58, 860, 76], { sizes: [21, 19, 17, 15] });
    if (p.matrix) { const [pay, rows, cols] = p.matrix; drawMatrix(pay, rows, cols, 150, 190, Math.min(170, Math.floor(440 / cols.length)), Math.min(90, Math.floor(190 / rows.length))); }
    p.fields.forEach(([lab], i) => {
      const b = this.box(i); fit(lab, [50, b[1] + 2, 370, 40], { sizes: [20, 18, 16, 14] });
      fr(this.solved ? [225, 245, 225] : WHITE, ...b); sr(i === this.focus && !this.solved ? GOLD : INK, ...b, 3);
      FM(this.vals[i] + (i === this.focus && !this.solved && Math.floor(performance.now() / 500) % 2 ? "|" : ""), INK, b[0] + 8, b[1] + 8);
    });
    const hs = p.hints || [];
    if (hs.length && !this.solved) { text("Type a number or fraction. TAB switches boxes, ENTER checks.", 14, GREY, 640, 140); for (let i = 0; i < this.hints; i++) fit(hs[i], [640, 165 + i * 68, 260, 64], { sizes: [17, 15, 13] }); }
    if (!this.solved) {
      this.sub.draw(); this.padb.draw();
      if (hs.length) { this.hintb.label = `Hint (${this.hints}/${hs.length})`; this.hintb.draw(); }
      fit(this.msg, [60, 548, 600, 62], { col: RED, sizes: [19, 17, 15] });
      if (this.pad) {
        panel([280, 250, 430, 350]); fit(p.fields[this.focus][0], [300, 262, 390, 26], { sizes: [18, 16, 14], bold: true });
        fr(WHITE, 300, 292, 376, 32); sr(INK, 300, 292, 376, 32, 3); FM(this.vals[this.focus], INK, 308, 296);
        PAD_KEYS.forEach((row, r) => row.forEach((k, c) => new Button(this.padrect(r, c), { "<": "DEL", NEXT: "Next box", CLOSE: "Close" }[k] || k, ["<", "NEXT", "CLOSE"].includes(k) ? PURP : WOOD).draw()));
        this.padchk.draw(); fit(this.msg, [300, 592, 376, 30], { col: RED, sizes: [14, 12] });
      }
    } else {
      fit(this.msg, [60, 548, 600, 62], { col: GREEN, sizes: [19, 17, 15] });
      let gate = true;
      if (p.throw) { this.hintb.label = "Throw 20 pebbles"; this.hintb.draw(); fit(this.last, [60, 505, 620, 40], { col: this.net >= 0 ? GREEN : RED, sizes: [18, 16, 14] }); gate = this.n >= 20 && this.net >= 0; }
      this.cont.enabled = gate; this.cont.draw();
    }
  }
}

class STree {
  constructor(sp) {
    this.c = sp.cfg; this.root = normTree(this.c.tree); this.names = this.c.names; this.pos = layout(this.root, 90, 870, 175, 335); this.order = [];
    const po = n => { if (n.u) return; n.a.forEach(([, c]) => po(c)); this.order.push(n); }; po(this.root);
    this.chosen = new Map(); this.ci = 0; this.msg = ""; this.done = false; this.cont = new Button([700, 560, 200, 44], "Continue", GREENB); this.mk();
  }
  val(n) { return n.u ? n.u : this.val(n.a[this.chosen.get(n)][1]); }
  mk() { this.btns = []; if (this.ci < this.order.length) { const acts = this.order[this.ci].a, w = Math.floor(840 / acts.length) - 10; this.btns = acts.map(([l], i) => new Button([60 + i * (w + 10), 450, w, 46], l)); } }
  event(ev) {
    if (this.ci >= this.order.length) { if (this.cont.hit(ev)) this.done = true; return; }
    const node = this.order[this.ci];
    this.btns.forEach((b, i) => {
      if (!b.hit(ev)) return;
      const vals = node.a.map(([, c]) => this.val(c)[node.p]), who = this.names[node.p], best = Math.max(...vals);
      if (vals[i] === best) {
        this.chosen.set(node, i); this.msg = `Correct: ${who} picks ${node.a[i][0]} (payoff ${fmt(vals[i])}).`;
        if (vals.filter(v => v === best).length > 1) this.msg += " Careful: another action ties, so there is another SPE too.";
        this.ci++; this.mk();
      } else this.msg = `Not quite. For ${who}: ` + vals.map((v, j) => `${node.a[j][0]} gives ${fmt(v)}`).join(", ") + ". Pick the best one.";
    });
  }
  draw() {
    const c = this.c; scene(c.theme, TICK); panel([30, 12, 900, 616]); FB(c.title, INK, 50, 24); fit(c.prompt, [50, 58, 860, 64], { sizes: [20, 18, 16, 14] });
    const cur = this.ci < this.order.length ? this.order[this.ci] : null;
    drawTree(this.root, this.names, this.pos, this.chosen, cur);
    if (cur) { FM(`Solve the LOWEST unsolved node first. Node ${cur.n}: ${this.names[cur.p]} chooses...`, INK, 60, 412); this.btns.forEach(b => b.draw()); }
    else {
      let n = this.root; const path = [];
      while (!n.u) { const [lab, ch] = n.a[this.chosen.get(n)]; path.push(lab); n = ch; }
      const bits = [...this.order].sort((a, b) => (a.n < b.n ? -1 : 1)).map(nd => `${nd.n}: ${nd.a[this.chosen.get(nd)][0]}`);
      this.msg = "SPE (a choice at EVERY node): " + bits.join("; ") + ".  Path of play: " + path.join(", ") + `.  Payoffs (${fmt(n.u[0])}, ${fmt(n.u[1])}).`;
      this.cont.draw();
    }
    fit(this.msg, [60, 502, 630, 106], { col: this.msg.startsWith("Correct") || this.msg.startsWith("SPE") ? GREEN : RED, sizes: [18, 16, 14, 12] });
  }
}

class STwo {
  constructor(sp) { this.c = sp.cfg; this.done = false; this.cont = new Button([600, 520, 300, 50], "Continue", GREENB); this.reset(); }
  reset() { this.stage = 1; this.o1 = null; this.o2 = null; this.tot = [0, 0]; }
  rb(stage) { const rows = stage === 1 ? this.c.rows1 : this.c.rows2, x = stage === 1 ? 120 : 580; return rows.map((n, i) => new Button([x + i * 125, 420, 115, 44], "Play " + n)); }
  event(ev) {
    const c = this.c;
    if (this.stage === 1 || this.stage === 2) {
      this.rb(this.stage).forEach((b, i) => {
        if (!b.hit(ev)) return;
        let col, a, e;
        if (this.stage === 1) { col = c.e1; this.o1 = [i, col]; [a, e] = c.m1[i][col]; }
        else { col = (this.o1[0] === 0 && this.o1[1] === 0) ? 0 : 1; this.o2 = [i, col]; [a, e] = c.m2[i][col]; }
        this.tot[0] += a; this.tot[1] += e; this.stage++;
      });
    } else if (this.cont.hit(ev)) { if (this.tot[0] >= c.goal) this.done = true; else this.reset(); }
  }
  draw() {
    const c = this.c; scene(c.theme, TICK); panel([30, 12, 900, 616]); FB(c.title, INK, 50, 24); fit(c.tip, [50, 58, 860, 52], { sizes: [19, 17, 15] });
    fit(c.goal_text || `Goal: finish with a combined total of at least ${c.goal} points to move on.`, [50, 112, 860, 24], { col: GREEN, sizes: [18, 16, 14], bold: true });
    FM("STAGE 1" + (this.stage === 1 ? "   <- your move" : ""), INK, 120, 152); FM("STAGE 2" + (this.stage === 2 ? "   <- your move" : ""), INK, 580, 152);
    drawMatrix(c.m1, c.rows1, c.cols1, 140, 215, 110, 80, false, this.o1); drawMatrix(c.m2, c.rows2, c.cols2, 600, 215, 110, 80, false, this.o2);
    FS("blue = you, red = " + c.short, INK, 140, 385); FM(`Your total: ${fmt(this.tot[0])}      ${c.short}: ${fmt(this.tot[1])}`, INK, 140, 500);
    if (this.stage <= 2) this.rb(this.stage).forEach(b => b.draw());
    else {
      const ok = this.tot[0] >= c.goal;
      fit(ok ? "You reached the goal! The threat of punishment kept cooperation alive." : "Short of the goal. Look at what the enemy does in stage 2 after each stage-1 outcome.", [140, 535, 440, 70], { col: ok ? GREEN : RED, sizes: [19, 17, 15] });
      this.cont.label = ok ? "Continue" : "Retry"; this.cont.draw();
    }
  }
}

class SHot {
  constructor(sp) { this.theme = sp.theme; this.pos = null; this.enemy = null; this.share = null; this.msg = ""; this.done = false; this.cont = new Button([700, 540, 200, 44], "Continue", GREENB); }
  event(ev) {
    if (this.share !== null && this.share >= 50 && this.cont.hit(ev)) { this.done = true; return; }
    if (ev.type === "down" && inR(ev.x, ev.y, [100, 230, 760, 110])) {
      const x = Math.max(0, Math.min(100, Math.round((ev.x - 100) / 7.6))), e = x < 50 ? x + 1 : x > 50 ? x - 1 : 50;
      this.pos = x; this.enemy = e;
      if (e === x) this.share = 50; else { const m = (x + e) / 2; this.share = x < e ? m : 100 - m; }
      this.msg = `You set up at ${x}; Rusty answered at ${e}. Customers go to the nearer stand, so your share is ${this.share.toFixed(1)}%. ` + (this.share >= 50 ? "You win or tie: you can move on!" : "Rusty squeezed you! Try another spot.");
    }
  }
  draw() {
    scene(this.theme, TICK); panel([30, 12, 900, 616]); FB("Hotelling's Beach - Median Voter", INK, 50, 24);
    fit("Customers are spread evenly along the beach (0 to 100) and walk to the NEAREST ice cream stand. Click to place your stand. Rusty then places his stand wherever is best against you. Win or tie to move on.", [50, 60, 860, 90], { sizes: [20, 18, 16] });
    fr(SAND, 100, 270, 760, 30); sr(INK, 100, 270, 760, 30, 3);
    for (let i = 0; i <= 100; i += 10) { const x = 100 + i * 7.6; ln(INK, x, 300, x, 310, 2); text(String(i), 14, INK, x, 312, { center: true }); }
    for (const [who, x, col] of [["YOU", this.pos, BLUE], ["RUSTY", this.enemy, RED]]) {
      if (x === null) continue;
      const px = 100 + x * 7.6 + (who === "RUSTY" && this.pos === this.enemy ? 12 : 0); fr(col, px - 10, 235, 20, 34); text(who, 14, col, px, 215, { bold: true, center: true });
    }
    if (this.share !== null) {
      const w = Math.floor(7.6 * this.share); fr(BLUE, 100, 360, w, 28); fr(RED, 100 + w, 360, 760 - w, 28); sr(INK, 100, 360, 760, 28, 3);
      text(`your customers ${this.share.toFixed(1)}%`, 16, WHITE, 110, 364, { bold: true });
      fit(this.msg, [60, 410, 800, 100], { col: this.share >= 50 ? GREEN : RED, sizes: [20, 18, 16] });
      if (this.share >= 50) this.cont.draw();
    }
  }
}

class SPump {
  constructor(sp) {
    this.theme = sp.theme; this.goal = sp.goal || 6; this.coins = 0; this.hold = "A"; this.msg = ""; this.done = false;
    this.btns = ["A", "B", "C"].map((x, i) => [x, new Button([90 + i * 280, 440, 250, 56], `Offer item ${x}`)]); this.cont = new Button([700, 545, 200, 44], "Continue", GREENB);
  }
  event(ev) {
    if (this.coins >= this.goal) { if (this.cont.hit(ev)) this.done = true; return; }
    const pref = ["BA", "CB", "AC"];
    for (const [x, b] of this.btns) if (b.hit(ev)) {
      if (x === this.hold) this.msg = "She already holds that item.";
      else if (pref.includes(x + this.hold)) { this.coins++; this.msg = `She prefers ${x} to ${this.hold}, so she swaps and pays you a coin!`; this.hold = x; }
      else this.msg = `She prefers ${this.hold} to ${x}, so she refuses the swap.`;
      if (this.coins >= this.goal) this.msg = "A MONEY PUMP! Her preferences cycle (B over A, C over B, A over C), so you can trade her around the loop forever and collect coins. Transitivity matters.";
    }
  }
  draw() {
    scene(this.theme, TICK); panel([30, 12, 900, 616]); FB("The Money Pump", INK, 50, 24);
    fit(`Kiki prefers B to A, C to B, and A to C (a cycle!). She holds item A and pays you 1 coin for any swap to an item she prefers. Offer items to pump coins out of her. Goal: ${this.goal} coins.`, [50, 60, 860, 70], { sizes: [21, 19, 17] });
    char("Kiki the Kiwi", 200, 400, 5); panel([400, 160, 220, 150], WHITE); FM("Kiki holds", INK, 510, 172, { center: true }); FT(this.hold, BLUE, 510, 210, { center: true });
    FB(`Coins: ${this.coins} / ${this.goal}`, [150, 80, 20], 660, 200);
    fit(this.msg, [60, 505, 600, 100], { col: this.coins >= this.goal ? GREEN : INK, sizes: [20, 18, 16] });
    if (this.coins >= this.goal) this.cont.draw(); else this.btns.forEach(([, b]) => b.draw());
  }
}

class SUnr {
  constructor(sp) { this.theme = sp.theme; this.R = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]; this.nxt = 0; this.msg = ""; this.done = false; this.cont = new Button([700, 545, 200, 44], "Continue", GREENB); }
  rect(i) { return [40 + i * 68, 220, 62, 90]; }
  event(ev) {
    if (this.nxt >= 12) { if (this.cont.hit(ev)) this.done = true; return; }
    if (ev.type !== "down") return;
    for (let i = 0; i < 13; i++) if (inR(ev.x, ev.y, this.rect(i))) {
      if (i === 12) this.msg = "The Ace can never lose, so it always bets. Tap the card that folds NEXT instead.";
      else if (i < this.nxt) this.msg = "That card already folded.";
      else if (i === this.nxt) {
        this.nxt++;
        this.msg = i === 0 ? "The 2 loses to every other card, so betting with it only loses money. It folds." : `Every worse hand already folds, so the ${this.R[i]} can only win against hands that fold anyway. Betting just risks money, so it folds too.`;
        if (this.nxt >= 12) this.msg += "  Only the ACE bets! That chain reaction is called UNRAVELING.";
      } else this.msg = "Not yet! Start from the WORST hand still betting. Which weakest card has no reason to bet?";
    }
  }
  draw() {
    scene(this.theme, TICK); panel([30, 12, 900, 616]); FB("Poker Unraveling", INK, 50, 24);
    fit("Each player draws one card from 2 up to Ace. Both can bet $1 or fold, and the higher card wins. Tap the cards in the order they FOLD, starting with the first hand that should never bet.", [50, 60, 860, 90], { sizes: [21, 19, 17] });
    for (let i = 0; i < 13; i++) {
      const r = this.rect(i), folded = i < this.nxt; fr(folded ? [190, 180, 165] : [255, 248, 228], ...r); sr(INK, ...r, 3);
      FB(this.R[i], folded ? GREY : "JQKA".includes(this.R[i]) ? RED : INK, r[0] + r[2] / 2, r[1] + 14, { center: true });
      text(folded ? "FOLD" : this.nxt >= 12 && i === 12 ? "BET" : "", 14, folded ? GREY : GREEN, r[0] + r[2] / 2, r[1] + 56, { bold: true, center: true });
    }
    fit(this.msg, [60, 340, 840, 150], { sizes: [22, 20, 18, 16] }); if (this.nxt >= 12) this.cont.draw();
  }
}

class SSignal {
  constructor(sp) {
    this.c = sp.cfg; this.strat = [0, 0]; this.off = 0; this.t = 0; this.msg = ""; this.rep = ""; this.done = false; this.solved = false; this.BEL = [0, 0.5, 1];
    this.tb = [0, 1].map(i => new Button([400, 140 + i * 56, 380, 46], "")); this.ob = new Button([50, 258, 730, 46], "", PURP);
    this.test = new Button([50, 316, 240, 46], "Test these strategies", GREENB); this.cont = new Button([700, 560, 200, 44], "Continue", GREENB); this.refresh();
  }
  refresh() { const c = this.c; this.tb.forEach((b, i) => { b.label = `plays: ${c.acts[this.strat[i]]}  (tap to change)`; }); this.ob.label = `Unseen action => receiver believes P(${c.types[0][0]}) = ${this.BEL[this.off]}  (tap to change)`; }
  analyze() {
    const c = this.c, prior = c.types.map(t => t[1]), info = [];
    for (let a = 0; a < 2; a++) {
      const mass = [0, 1].reduce((s, t) => s + (this.strat[t] === a ? prior[t] : 0), 0), on = mass > 0, b0 = on ? (this.strat[0] === a ? prior[0] : 0) / mass : this.BEL[this.off], bel = [b0, 1 - b0];
      const ev = c.resp.map((_, r) => [0, 1].reduce((s, t) => s + bel[t] * c.recv[t][r], 0));
      let r = 0; ev.forEach((v, k) => { if (v > ev[r]) r = k; });
      info.push([r, b0, on]);
    }
    const dev = [];
    for (let t = 0; t < 2; t++) { const a = this.strat[t], u = c.send[t][a][info[a][0]], u2 = c.send[t][1 - a][info[1 - a][0]]; if (u2 > u) dev.push([t, u, u2]); }
    return [info, dev];
  }
  run() {
    const c = this.c, task = c.tasks[this.t], [info, dev] = this.analyze(), lines = [];
    for (let a = 0; a < 2; a++) { const [r, b0, on] = info[a]; lines.push(`After '${c.acts[a]}': belief P(${c.types[0][0]}) = ${b0.toFixed(2)}${on ? "" : " (off the path)"}; receiver picks '${c.resp[r]}'.`); }
    for (const [t, u, u2] of dev) lines.push(`${c.types[t][0]} would switch to '${c.acts[1 - this.strat[t]]}' (payoff ${fmt(u2)} instead of ${fmt(u)}).`);
    this.rep = lines.join("\n");
    const sep = this.strat[0] !== this.strat[1], kind = task[0], s = this.strat;
    const okKind = (kind === "separating" && sep) || (kind === "pooling" && !sep) || (kind === "pool0" && s[0] === 0 && s[1] === 0) || (kind === "pool1" && s[0] === 1 && s[1] === 1);
    if (dev.length) this.msg = "Not an equilibrium: someone gains by deviating. Change a strategy or the off-path belief and test again.";
    else if (!okKind) this.msg = "That is an equilibrium, but not the kind this task asks for. " + task[1];
    else { this.t++; this.msg = "Equilibrium found! " + task[2]; if (this.t >= c.tasks.length) this.solved = true; }
  }
  event(ev) {
    if (this.solved) { if (this.cont.hit(ev)) this.done = true; return; }
    this.tb.forEach((b, i) => { if (b.hit(ev)) { this.strat[i] = 1 - this.strat[i]; this.refresh(); } });
    if (this.ob.hit(ev)) { this.off = (this.off + 1) % 3; this.refresh(); }
    if (this.test.hit(ev)) this.run();
  }
  draw() {
    const c = this.c; scene(c.theme, TICK); panel([30, 12, 900, 616]); FB(c.title, INK, 50, 24); fit(c.intro, [50, 56, 860, 50], { sizes: [18, 16, 14] });
    const task = c.tasks[Math.min(this.t, c.tasks.length - 1)];
    fit(`Task ${Math.min(this.t + 1, c.tasks.length)}/${c.tasks.length}: ${task[1]}`, [50, 106, 860, 30], { col: GREEN, sizes: [19, 17, 15], bold: true });
    c.types.forEach(([nm, pr], i) => { fit(`Type ${nm} (chance ${pr})`, [50, 148 + i * 56, 340, 36], { sizes: [21, 19, 17], bold: true }); this.tb[i].draw(); });
    this.ob.draw(); this.test.draw(); fit(this.rep, [50, 372, 860, 110], { sizes: [18, 16, 14] });
    fit(this.msg, [50, 488, 640, 120], { col: this.msg.startsWith("Equilibrium") ? GREEN : RED, sizes: [19, 17, 15] }); if (this.solved) this.cont.draw();
  }
}

class TextEntry {
  constructor(theme, title, prompt, maxlen = 16, dash = false) {
    this.theme = theme; this.title = title; this.prompt = prompt; this.maxlen = maxlen; this.value = ""; this.done = false; this.cancel = false;
    this.allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" + (dash ? "-" : "");
    const rows = ["1234567890", "QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM" + (dash ? "-" : "")];
    this.keys = []; rows.forEach((row, ri) => [...row].forEach((ch, ci) => this.keys.push([ch, new Button([480 - row.length * 34 + ci * 68, 240 + ri * 60, 62, 52], ch)])));
    this.bk = new Button([190, 490, 200, 50], "Backspace", PURP); this.ok = new Button([410, 490, 140, 50], "OK", GREENB); this.cx = new Button([570, 490, 200, 50], "Cancel", DRED);
  }
  finish() { if (this.value) this.done = true; }
  event(ev) {
    if (ev.type === "key") {
      if (ev.key === "Backspace") this.value = this.value.slice(0, -1); else if (ev.key === "Enter") this.finish(); else if (ev.key === "Escape") this.cancel = true;
      else if (ev.key.length === 1 && this.allowed.includes(ev.key.toUpperCase()) && this.value.length < this.maxlen) this.value += ev.key.toUpperCase();
    }
    for (const [ch, b] of this.keys) if (b.hit(ev) && this.value.length < this.maxlen) this.value += ch;
    if (this.bk.hit(ev)) this.value = this.value.slice(0, -1); if (this.ok.hit(ev)) this.finish(); if (this.cx.hit(ev)) this.cancel = true;
  }
  draw() {
    scene(this.theme, TICK); panel([30, 12, 900, 616]); FB(this.title, INK, 50, 24); fit(this.prompt, [50, 62, 860, 80], { sizes: [21, 19, 17] });
    fr(WHITE, 230, 150, 500, 56); sr(INK, 230, 150, 500, 56, 3); FB(this.value + (Math.floor(performance.now() / 500) % 2 ? "|" : ""), INK, 244, 164);
    this.keys.forEach(([, b]) => b.draw()); this.bk.draw(); this.ok.draw(); this.cx.draw();
  }
}

let TICK = 0;
const setTick = t => { TICK = t; };
function makeScene(sp) {
  switch (sp.t) {
    case "dlg": return new SDialogue(sp); case "quiz": return new SQuiz(sp); case "boss": return new SBoss(sp); case "play": return new SPlay(sp);
    case "nash": return new SNash(sp); case "elim": return new SElim(sp); case "calc": return new SCalc(sp); case "tree": return new STree(sp);
    case "two": return new STwo(sp); case "hot": return new SHot(sp); case "pump": return new SPump(sp); case "unr": return new SUnr(sp); case "sig": return new SSignal(sp);
  }
  throw new Error("unknown scene " + sp.t);
}
