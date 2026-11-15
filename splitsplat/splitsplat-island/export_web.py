"""Exports every level of the Python game to web/content.js so the browser version teaches exactly the same content.
Run:  python export_web.py     (needs pygame or the stand-in used for testing)"""
import json, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sp_engine as E, sp_links  # noqa
import sp_levels_1 as L1, sp_levels_2 as L2
import main as M

WRONG = {"Clara rigged the pebbles!": "pen_p", "Now let q = Clara's chance": "pen_q", "The goalie improves": "pen2", "Find the mixed equilibrium. r, p, s": "mrps",
         "Find the mixed equilibrium. p = kicker's": "pen1"}


def wrong_id(prompt):
    for k, v in WRONG.items():
        if prompt.startswith(k):
            return v
    if prompt.startswith("Find the mixed equilibrium. p = chance the ROW player picks Opera"):
        return "bos" if "(makes" in prompt else "gbos"
    raise Exception("unmapped wrong-answer lambda: " + prompt[:50])


def enemy_spec(fn):
    if fn is E.e_random: return {"k": "random"}
    if hasattr(fn, "meta"): return {"k": "always", "c": fn.meta[1]}
    if fn.__name__ in ("e_moe", "e_grim", "e_tft"): return {"k": fn.__name__[2:]}
    return {"k": "rpsbias"}


def extra_spec(f):
    if f is None: return None
    m = f.meta
    if m[0] == "matrix": return {"k": "matrix", "pay": m[1], "rows": m[2], "cols": m[3]}
    if m[0] == "info": return {"k": "info", "lines": m[1]}
    return {"k": "tree", "tree": m[1](), "names": m[2]}


def ser(sc, level, last):
    I = E
    if isinstance(sc, I.Dialogue):
        d = {"t": "dlg", "enemy": sc.enemy, "theme": sc.theme, "lines": [list(l) for l in sc.lines], "links": [[t, I.lecture_url(sl)] for t, sl in I.LINKS.get(level, [])]}
        if last: d["praise"] = True
        return d
    if isinstance(sc, I.Boss): return {"t": "boss", "theme": sc.theme, "title": sc.title, "pool": sc.pool, "n": sc.n}
    if isinstance(sc, I.Quiz): return {"t": "quiz", "theme": sc.theme, "title": sc.title, "qs": sc.qs, "extra": extra_spec(sc.extra), "optional": True}
    if isinstance(sc, I.MatrixPlay):
        c = dict(sc.c); c["enemy"] = enemy_spec(c["enemy"]); c["win"] = "avg25" if "win" in c else "tie"
        c["mood"] = c["mood"].__name__[5:] if c.get("mood") else None
        return {"t": "play", "cfg": c}
    if isinstance(sc, I.NashPicker): return {"t": "nash", "cfg": sc.c}
    if isinstance(sc, I.Eliminate): return {"t": "elim", "cfg": sc.c}
    if isinstance(sc, I.Calc):
        probs = []
        for p in sc.P:
            q = {k: v for k, v in p.items() if k != "wrong"}
            if p.get("wrong"): q["wrongId"] = wrong_id(p["prompt"])
            probs.append(q)
        return {"t": "calc", "theme": sc.theme, "title": sc.title, "pages": sc.pages, "problems": probs}
    if isinstance(sc, I.Tree):
        c = dict(sc.c); c["tree"] = c["tree"](); return {"t": "tree", "cfg": c}
    if isinstance(sc, I.TwoStage):
        c = dict(sc.c); c["e2"] = "punish"; return {"t": "two", "cfg": c}
    if isinstance(sc, I.Hotelling): return {"t": "hot", "theme": sc.theme}
    if isinstance(sc, I.MoneyPump): return {"t": "pump", "theme": sc.theme, "goal": sc.goal}
    if isinstance(sc, I.Unravel): return {"t": "unr", "theme": sc.theme}
    if isinstance(sc, I.Signal): return {"t": "sig", "cfg": sc.c}
    raise Exception("cannot export " + type(sc).__name__)


regions = []
for (name, unit, theme, levels, pos) in M.REGIONS:
    out = []
    for (lname, build) in levels:
        scs = build()
        out.append({"name": lname, "scenes": [ser(sc, lname, i == len(scs) - 1) for i, sc in enumerate(scs)]})
    regions.append({"name": name, "unit": unit, "theme": theme, "pos": list(pos), "levels": out})
data = {"regions": regions, "praise": E.PRAISE, "yt": M.YT_PLAYLIST, "site": M.SITE, "credits": M.CREDITS}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "content.js"), "w").write("const CONTENT = " + json.dumps(data, ensure_ascii=False) + ";\n")
print("exported", sum(len(r["levels"]) for r in regions), "levels")
