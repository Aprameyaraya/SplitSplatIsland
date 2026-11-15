"use strict";
// Splitsplat Island - browser game shell: island map, profiles, credits, saving, input.
const REGIONS = CONTENT.regions, START = [], NODES = REGIONS.map(r => [r.pos[0] * 4, r.pos[1] * 4]);
let TOTAL = 0;
REGIONS.forEach(r => { START.push(TOTAL); TOTAL += r.levels.length; });
const SAVE_KEY = "splitsplat_v2";

function storeRead() {
  let data = {};
  try { data = JSON.parse(localStorage.getItem(SAVE_KEY) || "{}"); } catch (e) { data = {}; }
  if (!data || typeof data !== "object") data = {};
  if (data.progress !== undefined && !(data.players && Object.keys(data.players).length)) data = { players: { PLAYER: { progress: +data.progress || 0 } }, last: "PLAYER" };
  data.players = data.players || {}; data.last = data.last || "";
  return data;
}
function storeWrite(d) { try { localStorage.setItem(SAVE_KEY, JSON.stringify(d)); } catch (e) { /* private mode: progress just won't persist */ } }
const checksum = (name, prog) => { let s = 0; [...(name + prog)].forEach((c, i) => { s += (i + 7) * c.charCodeAt(0); }); return (s % 4096).toString(16).toUpperCase().padStart(3, "0"); };
const makeCode = (name, prog) => `SPLIT-${name}-${prog}-${checksum(name, prog)}`;
function parseCode(code) {
  const p = code.trim().toUpperCase().split("-");
  if (p.length !== 4 || p[0] !== "SPLIT" || !p[1] || !/^\d+$/.test(p[2])) return null;
  const prog = parseInt(p[2], 10);
  return prog > TOTAL || checksum(p[1], prog) !== p[3] ? null : [p[1], prog];
}

function drawIsland(t) {
  waves(0, 160, t); lw.ell(SAND, 8, 18, 224, 138); lw.ell(GRASS, 16, 26, 208, 122);
  const pts = REGIONS.map(r => r.pos); for (let i = 0; i + 1 < pts.length; i++) lw.line([205, 165, 100], pts[i], pts[i + 1], 3);
  R(SEAC, 56, 36, 12, 118); R(WOODC, 52, 92, 20, 8); R(STONE, 52, 106, 20, 8); R(LEAF, 52, 92, 20, 2);
  for (const x of [84, 102, 120, 138]) mountain(x, 22, 36, 38);
  R(DARKC, 114, 56, 12, 8); lw.circ(DARKC, 120, 58, 6); mountain(176, 26, 44, 34, [130, 135, 150]); R(STONE, 188, 46, 16, 10); R([110, 110, 120], 186, 43, 20, 3); R(DARKC, 194, 49, 4, 7);
  palm(20, 118); palm(40, 124); rock(50, 140);
  for (const [x, y] of [[86, 130], [104, 138], [114, 128]]) { lw.ell(SEAL, x, y, 12, 6); rock(x + 10, y + 5); }
  R(DARKC, 118, 92, 20, 22); R(WOODD, 114, 100, 28, 2); R(TRUNK, 114, 97, 28, 1);
  for (const [x, y] of [[150, 70], [160, 90], [176, 78], [180, 94], [168, 64]]) palm(x, y, true);
  lw.ell([80, 112, 96], 188, 112, 28, 16); for (let x = 190; x < 214; x += 5) R([54, 92, 60], x, 108, 1, 8);
  R(WOODC, 214, 84, 26, 8); for (let x = 214; x < 240; x += 4) R(WOODD, x, 84, 1, 8);
  lw.poly(WOODD, [[226, 100], [240, 100], [238, 108], [228, 108]]); R(TRUNK, 232, 90, 1, 10);
  flushWorld();
}

const NEWNAME = "Type a name (letters and numbers). Your progress is saved under this name on this device.";
class Game {
  constructor() {
    this.mode = "title"; this.data = storeRead(); this.player = null; this.progress = 0; this.unlockAll = false; this.ri = 0; this.li = 0; this.scenes = []; this.si = 0; this.t = 0; this.entry = null; this.msg = "";
    this.start = new Button([380, 470, 200, 60], "Start", GREENB); this.back = new Button([W - 104, 0, 104, 30], "< Back", PURP);
    this.bu = new Button([20, 596, 220, 36], "", WOOD); this.bc = new Button([250, 596, 130, 36], "Credits", WOOD); this.bs = new Button([390, 596, 170, 36], "Switch player", WOOD); this.bk = new Button([570, 596, 150, 36], "Save code", WOOD);
    this.yt = new Button([130, 470, 330, 50], "Open the YouTube playlist", DRED); this.site = new Button([500, 470, 330, 50], "Open gametheory101.com", DRED);
  }
  save() { if (this.player) { this.data.players[this.player] = { progress: this.progress }; this.data.last = this.player; } storeWrite(this.data); }
  select(name) { this.player = name; this.progress = Math.min(TOTAL, +((this.data.players[name] || {}).progress || 0)); this.save(); this.mode = "island"; }
  profButtons() {
    const names = Object.keys(this.data.players).sort().slice(0, 6);
    const out = names.map((n, i) => ["p", n, new Button([290, 150 + i * 58, 380, 50], `${n}   (${this.data.players[n].progress}/${TOTAL} levels)`)]);
    let y = 150 + names.length * 58 + 8;
    if (names.length < 6) { out.push(["new", "", new Button([290, y, 380, 50], "+ New player", GREENB)]); y += 58; }
    out.push(["code", "", new Button([290, y, 380, 50], "Enter a save code", PURP)]);
    return out;
  }
  newName() { this.entry = new TextEntry("shore", "Create your player", NEWNAME, 12); this.mode = "newname"; }
  goBack() { this.mode = this.mode === "level" ? "region" : "island"; }
  regionNodes() { const n = REGIONS[this.ri].levels.length; return [...Array(n).keys()].map(i => [Math.floor(n === 1 ? 480 : 110 + i * (740 / (n - 1))), Math.floor(380 + 30 * Math.sin(i * 1.4))]); }
  ok(idx) { return this.unlockAll || idx <= this.progress; }
  begin(ri, li) { this.ri = ri; this.li = li; this.scenes = REGIONS[ri].levels[li].scenes.map(makeScene); this.si = 0; this.mode = "level"; }

  event(ev) {
    const m = this.mode;
    if (["level", "region", "credits", "showcode"].includes(m) && this.back.hit(ev)) { this.goBack(); return; }
    const esc = ev.type === "key" && ev.key === "Escape";
    if (m === "title") { if (this.start.hit(ev)) { if (Object.keys(this.data.players).length) this.mode = "profiles"; else this.newName(); } }
    else if (m === "profiles") {
      for (const [kind, name, b] of this.profButtons()) if (b.hit(ev)) {
        this.msg = "";
        if (kind === "p") this.select(name); else if (kind === "new") this.newName();
        else { this.entry = new TextEntry("shore", "Enter a save code", "Type the code from 'Save code' on your other device (it looks like SPLIT-NAME-12-1AB).", 30, true); this.mode = "entercode"; }
        break;
      }
    } else if (m === "newname" || m === "entercode") {
      this.entry.event(ev);
      if (this.entry.cancel) this.mode = Object.keys(this.data.players).length ? "profiles" : "title";
      else if (this.entry.done) {
        if (m === "newname") { const name = this.entry.value.replace(/-/g, ""); if (!this.data.players[name]) this.data.players[name] = { progress: 0 }; this.select(name); }
        else {
          const res = parseCode(this.entry.value);
          if (res) { const [name, prog] = res, old = (this.data.players[name] || {}).progress || 0; this.data.players[name] = { progress: Math.max(old, prog) }; this.select(name); }
          else { this.msg = "That save code is not valid. Check it and try again."; this.mode = "profiles"; }
        }
      }
    } else if (m === "island") {
      if (ev.type === "key" && ev.key.toLowerCase() === "u") this.unlockAll = !this.unlockAll;
      if (this.bu.hit(ev)) this.unlockAll = !this.unlockAll;
      if (this.bc.hit(ev)) this.mode = "credits";
      if (this.bs.hit(ev)) { this.msg = ""; if (Object.keys(this.data.players).length) this.mode = "profiles"; else this.newName(); }
      if (this.bk.hit(ev)) this.mode = "showcode";
      if (ev.type === "down") NODES.forEach(([x, y], i) => { if (this.ok(START[i]) && Math.hypot(ev.x - x, ev.y - y) < 32) { this.ri = i; this.mode = "region"; } });
    } else if (m === "credits") { if (this.yt.hit(ev)) window.open(CONTENT.yt, "_blank"); if (this.site.hit(ev)) window.open(CONTENT.site, "_blank"); if (esc) this.mode = "island"; }
    else if (m === "showcode") { if (esc) this.mode = "island"; }
    else if (m === "region") {
      if (esc) this.mode = "island";
      if (ev.type === "down") this.regionNodes().forEach(([x, y], i) => { if (this.ok(START[this.ri] + i) && Math.hypot(ev.x - x, ev.y - y) < 30 && this.mode === "region") this.begin(this.ri, i); });
    } else if (m === "level") {
      if (esc) this.mode = "region"; else if (this.si < this.scenes.length && !this.scenes[this.si].done) this.scenes[this.si].event(ev);
    } else if (m === "ending" && (ev.type === "key" || ev.type === "down")) this.mode = "island";
  }

  update() {
    this.t = TICK;
    if (this.mode === "level" && this.scenes[this.si].done) {
      this.si++;
      if (this.si >= this.scenes.length) {
        if (START[this.ri] + this.li === this.progress) { this.progress++; this.save(); }
        this.mode = this.progress >= TOTAL ? "ending" : "region";
      }
    }
  }

  draw() {
    const m = this.mode, t = this.t;
    if (m === "title") {
      scene("shore", t); char("Gus the Gull", 190, 410, 7); char("Clara the Crab", 770, 410, 7); panel([170, 60, 620, 215]);
      FT("SPLITSPLAT ISLAND", INK, W / 2, 85, { center: true }); FB("A Game Theory 101 adventure", [150, 80, 20], W / 2, 150, { center: true });
      fit("Based on William Spaniel's Game Theory 101: all 9 units, from the Prisoner's Dilemma to Perfect Bayesian Equilibrium.", [210, 195, 540, 60], { center: true, sizes: [20, 18, 16] });
      this.start.draw(); FS("Unofficial fan project. Not endorsed by William Spaniel.", WHITE, W / 2, 545, { center: true }); FS("Free to play. Watch the real lectures at gametheory101.com", WHITE, W / 2, 570, { center: true });
    } else if (m === "profiles") {
      scene("shore", t); panel([250, 40, 460, 560]); FB("Who is playing?", INK, W / 2, 64, { center: true });
      fit("Players are saved on this device. Progress saves automatically.", [270, 100, 420, 40], { center: true, sizes: [17, 15] });
      this.profButtons().forEach(([, , b]) => b.draw()); fit(this.msg, [270, 545, 420, 44], { col: RED, center: true, sizes: [17, 15] });
    } else if (m === "newname" || m === "entercode") this.entry.draw();
    else if (m === "island") {
      drawIsland(t); panel([20, 12, 700, 44]); FM(`Splitsplat Island - pick a region   (${this.player})`, INK, 38, 22);
      NODES.forEach(([x, y], i) => {
        const n = REGIONS[i].levels.length, done = [...Array(n).keys()].filter(j => START[i] + j < this.progress).length, allok = this.ok(START[i]);
        const col = done === n ? GREENB : allok ? GOLD : GREY, r = 18 + (allok && done < n ? Math.floor(2 * Math.sin(t / 8)) : 0);
        fc([50, 28, 14], x, y, r + 3); fc(col, x, y, r); FB(String(i + 1), INK, x, y - 14, { center: true });
        const lab = `${REGIONS[i].name}  ${done}/${n}`, w = tw(lab, 14, true) + 10; fr([50, 28, 14], x - w / 2 - 2, y + 22, w + 4, 24); fr(CREAM, x - w / 2, y + 24, w, 20); text(lab, 14, INK, x, y + 26, { bold: true, center: true });
      });
      const cur = REGIONS.findIndex((r, i) => START[i] + r.levels.length > this.progress), ci = cur < 0 ? REGIONS.length - 1 : cur, [px, py] = NODES[ci];
      char("You", px, py - 26 + Math.floor(3 * Math.sin(t / 8)), 2);
      this.bu.label = "Unlock all levels: " + (this.unlockAll ? "ON" : "off"); [this.bu, this.bc, this.bs, this.bk].forEach(b => b.draw());
    } else if (m === "showcode") {
      scene("shore", t); panel([120, 100, 720, 380]); FB("Your save code", INK, W / 2, 124, { center: true }); FT(makeCode(this.player || "PLAYER", this.progress), BLUE, W / 2, 190, { center: true });
      fit(`Write this down or copy it. On another device choose 'Enter a save code' on the player screen and type it in. It restores your progress (${this.progress}/${TOTAL} levels).`, [160, 280, 640, 120], { center: true, sizes: [22, 20, 18] }); this.back.draw();
    } else if (m === "credits") {
      scene("shore", t); panel([60, 40, 840, 560]); FB("About and credits", INK, W / 2, 60, { center: true }); fit(CONTENT.credits, [100, 110, 760, 340], { sizes: [21, 19, 17, 15] });
      this.yt.draw(); this.site.draw(); this.back.draw();
    } else if (m === "region") {
      const R0 = REGIONS[this.ri]; scene(R0.theme, t); panel([20, 12, 830, 80]); FB(R0.name, INK, 40, 22); FM(R0.unit, [150, 80, 20], 40, 54);
      const pts = this.regionNodes(); for (let i = 0; i + 1 < pts.length; i++) ln([205, 165, 100], pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 6);
      pts.forEach(([x, y], i) => {
        const idx = START[this.ri] + i; let col = idx < this.progress ? GREENB : idx === this.progress ? GOLD : GREY; if (this.unlockAll && idx > this.progress) col = [200, 170, 90];
        const r = 20 + (idx === this.progress ? Math.floor(2 * Math.sin(t / 8)) : 0); fc([50, 28, 14], x, y, r + 3); fc(col, x, y, r); FB(String(i + 1), INK, x, y - 14, { center: true });
        fr([50, 28, 14], x - 62, y + 24, 124, 44); fr(CREAM, x - 60, y + 26, 120, 40); fit(R0.levels[i].name, [x - 57, y + 28, 114, 36], { sizes: [15, 14, 12, 11], bold: true, center: true });
      });
      this.back.draw();
    } else if (m === "level") { this.scenes[this.si].draw(); this.back.draw(); }
    else if (m === "ending") {
      waves(0, 160, t); R(SKY, 0, 0, 240, 60); cloud(40, 14); cloud(160, 24); lw.ell(SAND, -60, 70, 90, 40); palm(10, 62);
      const x = Math.floor(t / 2) % 300 - 30, y = 96 + Math.floor(2 * Math.sin(t / 12));
      lw.poly(WOODD, [[x - 14, y], [x + 14, y], [x + 9, y + 8], [x - 9, y + 8]]); R(TRUNK, x, y - 20, 2, 20); lw.poly(WHITE, [[x + 3, y - 19], [x + 3, y - 3], [x + 15, y - 3]]); flushWorld();
      panel([60, 40, 840, 250]); FT("YOU ESCAPED SPLITSPLAT ISLAND!", INK, W / 2, 60, { center: true });
      fit("You completed all 9 units of Game Theory 101: strict dominance, Nash equilibrium, mixed strategies, subgame perfection, repeated games, expected utility, Bayesian Nash equilibrium and perfect Bayesian equilibrium. Thank you to William Spaniel for the lectures. Keep watching them at gametheory101.com!", [90, 130, 780, 150], { center: true, sizes: [24, 22, 20, 18] });
      FM("Tap or press any key to return to the island", WHITE, W / 2, 580, { center: true });
    }
  }
}

function start() {
  const cv = document.getElementById("c"); cv.width = W; cv.height = H; setCtx(cv.getContext("2d"));
  const g = new Game(); window.__game = g;
  const pos = e => { const r = cv.getBoundingClientRect(); return { x: (e.clientX - r.left) * W / r.width, y: (e.clientY - r.top) * H / r.height }; };
  const guard = fn => { try { fn(); } catch (err) { console.error(err); try { localStorage.setItem("splitsplat_log", String(err.stack || err)); } catch (e2) { /* ignore */ } g.mode = g.mode === "level" ? "region" : g.player ? "island" : "title"; } };
  cv.addEventListener("pointerdown", e => { if (e.pointerType === "touch") TOUCH = true; const p = pos(e); mouse.x = p.x; mouse.y = p.y; guard(() => g.event({ type: "down", x: p.x, y: p.y })); e.preventDefault(); });
  cv.addEventListener("pointermove", e => { const p = pos(e); mouse.x = p.x; mouse.y = p.y; });
  window.addEventListener("keydown", e => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if ([" ", "Tab", "Backspace", "Enter"].includes(e.key)) e.preventDefault();
    guard(() => g.event({ type: "key", key: e.key }));
  });
  (function loop() { setTick(Math.floor(performance.now() * 0.06)); ctx.imageSmoothingEnabled = false; guard(() => { g.update(); g.draw(); }); requestAnimationFrame(loop); })();
}
if (typeof window !== "undefined" && !window.__TEST__ && typeof document !== "undefined" && document.getElementById("c")) start();
