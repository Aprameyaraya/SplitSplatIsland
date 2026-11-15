"""
SPLITSPLAT ISLAND - a pixel-art story-mode game based on William Spaniel's Game Theory 101.
Unofficial, free fan project. Not affiliated with or endorsed by William Spaniel.

Desktop:  pip install pygame     then     python main.py
Browser:  pip install pygbag     then     pygbag splitsplat      (see README.txt)

Controls: mouse or touch. SPACE/ENTER/tap advances dialogue. ESC or the on-screen Back button goes back.
"""
import sys, os, json, math, asyncio
import pygame
from sp_engine import *
import sp_links  # noqa: F401  (fills in the lecture links)
from sp_levels_1 import REGION1, REGION2, REGION3
from sp_levels_2 import REGION4, REGION5, REGION6, REGION7, REGION8, REGION9

pygame.display.set_caption("Splitsplat Island - Game Theory 101 Adventure (unofficial fan project)")
clock = pygame.time.Clock()
YT_PLAYLIST = "https://www.youtube.com/playlist?list=PLKI1h_nAkaQoDzI4xDIXzx6U2ergFmedo"
SITE = "https://gametheory101.com/courses/game-theory-101/"

# (island name, unit name, theme, levels, node position in the 240x160 world)
REGIONS = [
    ("Coconut Coast", "Unit 1: The Basics", "shore", REGION1, (30, 130)),
    ("River Crossing", "Unit 2: Extensive Form Games", "bridges", REGION2, (62, 99)),
    ("Crab Cove", "Unit 3: Advanced Strategic Form", "tide", REGION3, (100, 134)),
    ("Bottomless Chasm", "Unit 4: Infinite Strategy Spaces", "rope", REGION4, (128, 102)),
    ("Gambler's Cave", "Unit 5: Expected Utility Theory", "cave", REGION5, (120, 60)),
    ("Banana Jungle", "Unit 6: Repeated Games", "jungle", REGION6, (164, 78)),
    ("Temple of Types", "Unit 7: Bayesian Nash Equilibrium", "temple", REGION7, (196, 48)),
    ("Foggy Marsh", "Unit 8: Perfect Bayesian Equilibrium", "marsh", REGION8, (200, 122)),
    ("The Dock", "Final Exam", "dock", REGION9, (222, 88)),
]
START, tot = [], 0
for _r in REGIONS:
    START.append(tot)
    tot += len(_r[3])
TOTAL = tot
NODES = [(r[4][0] * 4, r[4][1] * 4) for r in REGIONS]


# ------------------------------------------------------------------ saving: local player profiles
SAVE_KEY = "splitsplat_v2"
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "splitsplat_save.json")
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_log.txt")


def store_read():
    data = {}
    try:
        if EMS:
            import platform
            raw = platform.window.localStorage.getItem(SAVE_KEY)
        else:
            raw = open(SAVE_FILE).read() if os.path.exists(SAVE_FILE) else None
        data = json.loads(str(raw)) if raw else {}
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    if "progress" in data and not data.get("players"):  # migrate the old single-player save
        data = {"players": {"PLAYER": {"progress": int(data.get("progress", 0))}}, "last": "PLAYER"}
    data.setdefault("players", {})
    data.setdefault("last", "")
    return data


def store_write(data):
    try:
        raw = json.dumps(data)
        if EMS:
            import platform
            platform.window.localStorage.setItem(SAVE_KEY, raw)
        else:
            with open(SAVE_FILE, "w") as f:
                f.write(raw)
    except Exception:
        pass


def checksum(name, prog):
    return "%03X" % (sum((i + 7) * ord(c) for i, c in enumerate(name + str(prog))) % 4096)


def make_code(name, prog):
    return f"SPLIT-{name}-{prog}-{checksum(name, prog)}"


def parse_code(code):
    parts = code.strip().upper().split("-")
    if len(parts) != 4 or parts[0] != "SPLIT" or not parts[1] or not parts[2].isdigit():
        return None
    name, prog = parts[1], int(parts[2])
    if prog > TOTAL or checksum(name, prog) != parts[3]:
        return None
    return name, prog


# ------------------------------------------------------------------ the island map
def draw_island(t):
    waves(0, 160, t)
    pygame.draw.ellipse(LW, SAND, (8, 18, 224, 138))
    pygame.draw.ellipse(LW, GRASS, (16, 26, 208, 122))
    pts = [r[4] for r in REGIONS]
    for a, b in zip(pts, pts[1:]):
        pygame.draw.line(LW, (205, 165, 100), a, b, 3)
    R(SEAC, 56, 36, 12, 118)  # river
    R(WOODC, 52, 92, 20, 8)
    R(STONE, 52, 106, 20, 8)
    R(LEAF, 52, 92, 20, 2)
    for x in (84, 102, 120, 138):  # mountains and cave
        mountain(x, 22, 36, 38)
    R(DARKC, 114, 56, 12, 8)
    pygame.draw.circle(LW, DARKC, (120, 58), 6)
    mountain(176, 26, 44, 34, (130, 135, 150))  # temple
    R(STONE, 188, 46, 16, 10)
    R((110, 110, 120), 186, 43, 20, 3)
    R(DARKC, 194, 49, 4, 7)
    palm(20, 118)  # shore
    palm(40, 124)
    rock(50, 140)
    for x, y in ((86, 130), (104, 138), (114, 128)):  # tide pools
        pygame.draw.ellipse(LW, SEAL, (x, y, 12, 6))
        rock(x + 10, y + 5)
    R(DARKC, 118, 92, 20, 22)  # chasm and rope bridge
    R(WOODD, 114, 100, 28, 2)
    R(TRUNK, 114, 97, 28, 1)
    for x, y in ((150, 70), (160, 90), (176, 78), (180, 94), (168, 64)):  # jungle
        palm(x, y, True)
    pygame.draw.ellipse(LW, (80, 112, 96), (188, 112, 28, 16))  # marsh
    for x in range(190, 214, 5):
        R((54, 92, 60), x, 108, 1, 8)
    R(WOODC, 214, 84, 26, 8)  # dock
    for x in range(214, 240, 4):
        R(WOODD, x, 84, 1, 8)
    pygame.draw.polygon(LW, WOODD, [(226, 100), (240, 100), (238, 108), (228, 108)])
    R(TRUNK, 232, 90, 1, 10)
    pygame.transform.scale(LW, (W, H), screen)


CREDITS = ("SPLITSPLAT ISLAND is a free, UNOFFICIAL fan project that turns William Spaniel's Game Theory 101 course into a game. "
           "It is not affiliated with or endorsed by William Spaniel.\n\n"
           "The course structure, lecture titles and ideas come from his free lectures at gametheory101.com and on YouTube. "
           "Every level's title card has 'Watch' buttons linking to the matching lectures: please watch them, they are the real teacher.\n\n"
           "The exercises, numbers, art and game design are original to this project, so any mistakes in the game are the game's, not his.\n\n"
           "Built with pygame, with help from Claude (Anthropic). Players are saved on this device (browser storage in the web version). "
           "Use 'Save code' to move progress to another device; a cloud login would need a server.")


class Game:
    def __init__(s):
        s.mode, s.data, s.player, s.progress, s.unlock_all = "title", store_read(), None, 0, False
        s.ri, s.li, s.scenes, s.si, s.t, s.entry, s.msg = 0, 0, [], 0, 0, None, ""
        s.start = Button((380, 470, 200, 60), "Start", GREENB)
        s.back = Button((W - 104, 0, 104, 30), "< Back", PURP)
        s.bu = Button((20, 596, 220, 36), "", WOOD)
        s.bc = Button((250, 596, 130, 36), "Credits", WOOD)
        s.bs = Button((390, 596, 170, 36), "Switch player", WOOD)
        s.bk = Button((570, 596, 150, 36), "Save code", WOOD)
        s.yt = Button((130, 470, 330, 50), "Open the YouTube playlist", (170, 50, 50))
        s.site = Button((500, 470, 330, 50), "Open gametheory101.com", (170, 50, 50))

    # ---- players
    def save(s):
        if s.player:
            s.data["players"][s.player] = {"progress": s.progress}
            s.data["last"] = s.player
        store_write(s.data)

    def select(s, name):
        s.player = name
        s.progress = min(TOTAL, int(s.data["players"].get(name, {}).get("progress", 0)))
        s.save()
        s.mode = "island"

    def prof_buttons(s):
        names = sorted(s.data["players"])[:6]
        out = [("p", n, Button((290, 150 + i * 58, 380, 50), f"{n}   ({s.data['players'][n]['progress']}/{TOTAL} levels)")) for i, n in enumerate(names)]
        y = 150 + len(names) * 58 + 8
        if len(names) < 6:
            out.append(("new", "", Button((290, y, 380, 50), "+ New player", GREENB)))
            y += 58
        out.append(("code", "", Button((290, y, 380, 50), "Enter a save code", PURP)))
        return out

    def go_back(s):
        s.mode = "region" if s.mode == "level" else "island"

    def region_nodes(s):
        n = len(REGIONS[s.ri][3])
        return [(int(480 if n == 1 else 110 + i * (740 / (n - 1))), int(380 + 30 * math.sin(i * 1.4))) for i in range(n)]

    def ok(s, idx):
        return s.unlock_all or idx <= s.progress

    def begin(s, ri, li):
        s.ri, s.li = ri, li
        s.scenes, s.si, s.mode = REGIONS[ri][3][li][1](), 0, "level"

    # ---- events
    def event(s, ev):
        if s.mode in ("level", "region", "credits", "showcode") and s.back.hit(ev):
            s.go_back()
            return
        if s.mode == "title":
            if s.start.hit(ev):
                s.mode = "profiles" if s.data["players"] else "newname"
                if s.mode == "newname":
                    s.entry = TextEntry("shore", "Create your player", "Type a name (letters and numbers). Your progress is saved under this name on this device.", 12)
        elif s.mode == "profiles":
            for kind, name, b in s.prof_buttons():
                if b.hit(ev):
                    s.msg = ""
                    if kind == "p":
                        s.select(name)
                    elif kind == "new":
                        s.entry, s.mode = TextEntry("shore", "Create your player", "Type a name (letters and numbers). Your progress is saved under this name on this device.", 12), "newname"
                    else:
                        s.entry, s.mode = TextEntry("shore", "Enter a save code", "Type the code from 'Save code' on your other device (it looks like SPLIT-NAME-12-1AB).", 30, True), "entercode"
        elif s.mode in ("newname", "entercode"):
            s.entry.event(ev)
            if s.entry.cancel:
                s.mode = "profiles" if s.data["players"] else "title"
            elif s.entry.done:
                if s.mode == "newname":
                    name = s.entry.value.replace("-", "")
                    s.data["players"].setdefault(name, {"progress": 0})
                    s.select(name)
                else:
                    res = parse_code(s.entry.value)
                    if res:
                        name, prog = res
                        old = s.data["players"].get(name, {}).get("progress", 0)
                        s.data["players"][name] = {"progress": max(old, prog)}
                        s.select(name)
                    else:
                        s.msg, s.mode = "That save code is not valid. Check it and try again.", "profiles"
        elif s.mode == "island":
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_u:
                s.unlock_all = not s.unlock_all
            if s.bu.hit(ev):
                s.unlock_all = not s.unlock_all
            if s.bc.hit(ev):
                s.mode = "credits"
            if s.bs.hit(ev):
                s.msg, s.mode = "", "profiles" if s.data["players"] else "newname"
                if s.mode == "newname":
                    s.entry = TextEntry("shore", "Create your player", "Type a name (letters and numbers).", 12)
            if s.bk.hit(ev):
                s.mode = "showcode"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, (x, y) in enumerate(NODES):
                    if s.ok(START[i]) and math.hypot(ev.pos[0] - x, ev.pos[1] - y) < 32:
                        s.ri, s.mode = i, "region"
        elif s.mode == "credits":
            if s.yt.hit(ev):
                open_url(YT_PLAYLIST)
            if s.site.hit(ev):
                open_url(SITE)
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                s.mode = "island"
        elif s.mode == "showcode":
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                s.mode = "island"
        elif s.mode == "region":
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                s.mode = "island"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, (x, y) in enumerate(s.region_nodes()):
                    if s.ok(START[s.ri] + i) and math.hypot(ev.pos[0] - x, ev.pos[1] - y) < 30:
                        s.begin(s.ri, i)
        elif s.mode == "level":
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                s.mode = "region"
            elif s.si < len(s.scenes) and not s.scenes[s.si].done:
                s.scenes[s.si].event(ev)
        elif s.mode == "ending" and ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            s.mode = "island"

    def update(s):
        s.t += 1
        if s.mode == "level" and s.scenes[s.si].done:
            s.si += 1
            if s.si >= len(s.scenes):
                idx = START[s.ri] + s.li
                if idx == s.progress:
                    s.progress += 1
                    s.save()
                s.mode = "ending" if s.progress >= TOTAL else "region"

    # ---- drawing
    def draw(s):
        m = s.mode
        if m == "title":
            scene("shore", s.t)
            draw_char(190, 410, "gull", CHARS["Gus the Gull"][1], 7)
            draw_char(770, 410, "crab", CHARS["Clara the Crab"][1], 7)
            panel((170, 60, 620, 215))
            text("SPLITSPLAT ISLAND", FT, INK, W // 2, 85, center=True)
            text("A Game Theory 101 adventure", FB, (150, 80, 20), W // 2, 150, center=True)
            fit("Based on William Spaniel's Game Theory 101: all 9 units, from the Prisoner's Dilemma to Perfect Bayesian Equilibrium.", (210, 195, 540, 60), center=True, sizes=(20, 18, 16))
            s.start.draw()
            text("Unofficial fan project. Not endorsed by William Spaniel.", FS, WHITE, W // 2, 545, center=True)
            text("Free to play. Watch the real lectures at gametheory101.com", FS, WHITE, W // 2, 570, center=True)
        elif m == "profiles":
            scene("shore", s.t)
            panel((250, 40, 460, 560))
            text("Who is playing?", FB, INK, W // 2, 64, center=True)
            fit("Players are saved on this device. Progress saves automatically.", (270, 100, 420, 40), center=True, sizes=(17, 15))
            for _, _, b in s.prof_buttons():
                b.draw()
            fit(s.msg, (270, 545, 420, 44), col=RED, center=True, sizes=(17, 15))
        elif m in ("newname", "entercode"):
            s.entry.draw()
        elif m == "island":
            draw_island(s.t)
            panel((20, 12, 700, 44))
            text(f"Splitsplat Island - pick a region   ({s.player})", FM, INK, 38, 22)
            for i, (x, y) in enumerate(NODES):
                done = sum(1 for j in range(len(REGIONS[i][3])) if START[i] + j < s.progress)
                allok = s.ok(START[i])
                col = GREENB if done == len(REGIONS[i][3]) else GOLD if allok else GREY
                r = 18 + (int(2 * math.sin(s.t / 8)) if allok and done < len(REGIONS[i][3]) else 0)
                pygame.draw.circle(screen, (50, 28, 14), (x, y), r + 3)
                pygame.draw.circle(screen, col, (x, y), r)
                text(str(i + 1), FB, INK, x, y - 14, center=True)
                lab = getf(14, True).render(f"{REGIONS[i][0]}  {done}/{len(REGIONS[i][3])}", True, INK)
                rc = lab.get_rect(midtop=(x, y + 24)).inflate(10, 4)
                pygame.draw.rect(screen, (50, 28, 14), rc.inflate(4, 4))
                pygame.draw.rect(screen, CREAM, rc)
                screen.blit(lab, lab.get_rect(center=rc.center))
            cur = next((i for i in range(len(REGIONS)) if START[i] + len(REGIONS[i][3]) > s.progress), len(REGIONS) - 1)
            x, y = NODES[cur]
            draw_char(x, y - 26 + int(3 * math.sin(s.t / 8)), "player", CHARS["You"][1], 2)
            s.bu.label = "Unlock all levels: " + ("ON" if s.unlock_all else "off")
            for b in (s.bu, s.bc, s.bs, s.bk):
                b.draw()
        elif m == "showcode":
            scene("shore", s.t)
            panel((120, 100, 720, 380))
            text("Your save code", FB, INK, W // 2, 124, center=True)
            code = make_code(s.player or "PLAYER", s.progress)
            text(code, FT, BLUE, W // 2, 190, center=True)
            fit("Write this down or copy it. On another device choose 'Enter a save code' on the player screen and type it in. It restores your progress (" + str(s.progress) + "/" + str(TOTAL) + " levels).", (160, 280, 640, 120), center=True, sizes=(22, 20, 18))
            s.back.draw()
        elif m == "credits":
            scene("shore", s.t)
            panel((60, 40, 840, 560))
            text("About and credits", FB, INK, W // 2, 60, center=True)
            fit(CREDITS, (100, 110, 760, 340), sizes=(21, 19, 17, 15))
            s.yt.draw()
            s.site.draw()
            s.back.draw()
        elif m == "region":
            name, unit, theme, levels, _ = REGIONS[s.ri]
            scene(theme, s.t)
            panel((20, 12, 830, 80))
            text(name, FB, INK, 40, 22)
            text(unit, FM, (150, 80, 20), 40, 54)
            pts = s.region_nodes()
            if len(pts) > 1:
                pygame.draw.lines(screen, (205, 165, 100), False, pts, 6)
            for i, (x, y) in enumerate(pts):
                idx = START[s.ri] + i
                col = GREENB if idx < s.progress else GOLD if idx == s.progress else GREY
                if s.unlock_all and idx > s.progress:
                    col = (200, 170, 90)
                r = 20 + (int(2 * math.sin(s.t / 8)) if idx == s.progress else 0)
                pygame.draw.circle(screen, (50, 28, 14), (x, y), r + 3)
                pygame.draw.circle(screen, col, (x, y), r)
                text(str(i + 1), FB, INK, x, y - 14, center=True)
                rc = pygame.Rect(x - 60, y + 26, 120, 40)
                pygame.draw.rect(screen, (50, 28, 14), rc.inflate(4, 4))
                pygame.draw.rect(screen, CREAM, rc)
                fit(levels[i][0], rc.inflate(-6, -4), sizes=(15, 14, 12, 11), bold=True, center=True)
            s.back.draw()
        elif m == "level":
            s.scenes[s.si].draw()
            s.back.draw()
        elif m == "ending":
            waves(0, 160, s.t)
            R(SKY, 0, 0, 240, 60)
            cloud(40, 14)
            cloud(160, 24)
            pygame.draw.ellipse(LW, SAND, (-60, 70, 90, 40))
            palm(10, 62)
            x = (s.t // 2) % 300 - 30
            y = 96 + int(2 * math.sin(s.t / 12))
            pygame.draw.polygon(LW, WOODD, [(x - 14, y), (x + 14, y), (x + 9, y + 8), (x - 9, y + 8)])
            R(TRUNK, x, y - 20, 2, 20)
            pygame.draw.polygon(LW, WHITE, [(x + 3, y - 19), (x + 3, y - 3), (x + 15, y - 3)])
            pygame.transform.scale(LW, (W, H), screen)
            panel((60, 40, 840, 250))
            text("YOU ESCAPED SPLITSPLAT ISLAND!", FT, INK, W // 2, 60, center=True)
            fit("You completed all 9 units of Game Theory 101: strict dominance, Nash equilibrium, mixed strategies, subgame perfection, repeated games, expected utility, Bayesian Nash equilibrium and perfect Bayesian equilibrium. Thank you to William Spaniel for the lectures. Keep watching them at gametheory101.com!",
                (90, 130, 780, 150), center=True, sizes=(24, 22, 20, 18))
            text("Tap or press any key to return to the island", FM, WHITE, W // 2, 580, center=True)


def guard(g, fn, *a):
    """Run one step; on an unexpected error, log it and drop back instead of crashing."""
    try:
        fn(*a)
    except Exception:
        import traceback
        try:
            with open(LOG, "a") as f:
                f.write(traceback.format_exc() + "\n")
        except Exception:
            pass
        g.mode = "region" if g.mode == "level" else "island" if g.player else "title"


async def main():
    g = Game()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            guard(g, g.event, ev)
        guard(g, g.update)
        guard(g, g.draw)
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # required so the browser build can breathe


if __name__ == "__main__":
    asyncio.run(main())
