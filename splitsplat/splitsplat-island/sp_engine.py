"""Splitsplat Island engine: pixel-art drawing + reusable teaching scenes."""
import pygame, random, math, sys

pygame.init()
W, H = 960, 640
EMS = sys.platform == "emscripten"  # running in a web browser (pygbag)
try:
    screen = pygame.display.set_mode((W, H), pygame.SCALED)  # scales to any window / phone screen
except Exception:
    screen = pygame.display.set_mode((W, H))
LW = pygame.Surface((240, 160))  # low-res world layer, scaled 4x for the chunky pixel look
_fc = {}


def getf(sz, bold=False):
    if (sz, bold) not in _fc:
        try:
            f = pygame.font.SysFont("arial,helvetica,dejavusans,freesans", sz, bold=bold)
        except Exception:
            f = pygame.font.Font(None, int(sz * 1.25))
        _fc[(sz, bold)] = f
    return _fc[(sz, bold)]


def open_url(url):
    try:
        if EMS:
            import platform
            platform.window.open(url, "_blank")
        else:
            import webbrowser
            webbrowser.open(url)
    except Exception:
        pass


GT = "https://gametheory101.com/courses/game-theory-101/"
LINKS = {}  # level name -> [(lecture title, slug or full url)]; filled in by sp_links.py


def lecture_url(slug):
    return slug if slug.startswith("http") else GT + slug + "/"


FT, FB, FM, FS = getf(44, True), getf(26, True), getf(21), getf(16)
INK, WHITE, CREAM = (62, 36, 20), (255, 255, 255), (253, 238, 196)
BLUE, RED, GREEN, GOLD, GREY = (40, 80, 170), (190, 50, 50), (40, 120, 50), (240, 190, 40), (150, 140, 130)
WOOD, GREENB, PURP = (150, 95, 45), (80, 140, 55), (115, 85, 140)
SKY, SKY2, GRASS, GRASS2 = (132, 196, 232), (160, 214, 240), (104, 168, 72), (88, 150, 60)
SAND, SANDD, SEAC, SEAL = (236, 212, 150), (214, 186, 120), (62, 132, 200), (96, 160, 220)
WOODC, WOODD, STONE, DARKC = (170, 118, 62), (110, 70, 35), (150, 150, 160), (40, 30, 35)
LEAF, LEAFD, TRUNK = (52, 128, 60), (36, 98, 48), (110, 70, 40)


# ------------------------------------------------------------------ text helpers
def wrap(s, f, maxw):
    out = []
    for para in s.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if f.size(t)[0] <= maxw:
                cur = t
            else:
                out.append(cur)
                cur = w
        out.append(cur)
    return out


def text(s, f, col, x, y, maxw=None, center=False):
    lines = wrap(s, f, maxw) if maxw else [s]
    lh = f.get_linesize() + 2
    for i, l in enumerate(lines):
        img = f.render(l, True, col)
        r = img.get_rect()
        if center:
            r.midtop = (x, y + i * lh)
        else:
            r.topleft = (x, y + i * lh)
        screen.blit(img, r)
    return y + len(lines) * lh


def fit(s, rect, col=None, sizes=(24, 22, 20, 18, 16, 14, 12), bold=False, center=False):
    """Draw wrapped text in the largest font size that fits inside rect."""
    rect = pygame.Rect(rect)
    for sz in sizes:
        f = getf(sz, bold)
        lines = wrap(s, f, rect.w)
        lh = f.get_linesize() + 1
        if len(lines) * lh <= rect.h:
            break
    y = rect.y
    for l in lines:
        img = f.render(l, True, col or INK)
        screen.blit(img, img.get_rect(midtop=(rect.centerx, y)) if center else (rect.x, y))
        y += lh


def panel(r, col=CREAM):
    r = pygame.Rect(r)
    pygame.draw.rect(screen, (70, 40, 18), r)
    pygame.draw.rect(screen, (176, 112, 52), r.inflate(-6, -6))
    pygame.draw.rect(screen, (120, 72, 30), r.inflate(-12, -12))
    pygame.draw.rect(screen, col, r.inflate(-16, -16))


def fmt(v):
    return str(int(v)) if float(v).is_integer() else ("%.2f" % v).rstrip("0").rstrip(".")


class Button:
    def __init__(s, rect, label, color=WOOD):
        s.rect, s.label, s.color, s.enabled = pygame.Rect(rect), label, color, True

    def draw(s):
        c = s.color if s.enabled else GREY
        if s.enabled and s.rect.collidepoint(pygame.mouse.get_pos()):
            c = tuple(min(255, v + 30) for v in c)
        r = s.rect
        pygame.draw.rect(screen, (50, 28, 14), r)
        pygame.draw.rect(screen, c, r.inflate(-6, -6))
        pygame.draw.rect(screen, tuple(min(255, v + 45) for v in c), (r.x + 3, r.y + 3, r.w - 6, 3))
        pygame.draw.rect(screen, tuple(max(0, v - 40) for v in c), (r.x + 3, r.bottom - 6, r.w - 6, 3))
        inner = r.inflate(-20, -12)
        for sz in (21, 19, 17, 15, 13, 12):
            f = getf(sz, True)
            lines = wrap(s.label, f, inner.w)
            lh = f.get_linesize()
            if len(lines) * lh <= inner.h:
                break
        y = r.centery - len(lines) * lh // 2
        for l in lines:
            for col, o in (((40, 20, 10), 1), (WHITE, 0)):
                img = f.render(l, True, col)
                screen.blit(img, img.get_rect(midtop=(r.centerx + o, y + o)))
            y += lh

    def hit(s, ev):
        return s.enabled and ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and s.rect.collidepoint(ev.pos)


# ------------------------------------------------------------------ pixel world (drawn at 240x160, scaled 4x)
def R(c, x, y, w, h):
    pygame.draw.rect(LW, c, (x, y, w, h))


def tree(x, y, c=LEAF):
    R(TRUNK, x + 3, y + 8, 3, 7)
    pygame.draw.circle(LW, c, (x + 4, y + 5), 7)
    pygame.draw.circle(LW, tuple(min(255, v + 35) for v in c), (x + 2, y + 3), 3)


def palm(x, y, bananas=False):
    R(TRUNK, x, y, 2, 15)
    for dx, dy in ((-7, 3), (-5, -1), (0, -3), (5, -1), (7, 3)):
        pygame.draw.line(LW, LEAF, (x + 1, y), (x + 1 + dx, y + dy + 2), 2)
    R((240, 210, 60) if bananas else TRUNK, x - 1, y + 1, 3, 3)


def cloud(x, y):
    R(WHITE, x + 2, y + 3, 14, 4)
    R(WHITE, x + 5, y, 8, 5)


def mountain(x, y, w, h, c=(120, 125, 140)):
    pygame.draw.polygon(LW, c, [(x, y + h), (x + w // 2, y), (x + w, y + h)])
    pygame.draw.polygon(LW, WHITE, [(x + w // 2, y), (x + w // 2 - w // 8, y + h // 4), (x + w // 2 + w // 8, y + h // 4)])


def rock(x, y, c=STONE):
    R(c, x, y + 2, 6, 4)
    R(c, x + 1, y, 4, 3)


def waves(y0, y1, t=0):
    R(SEAC, 0, y0, 240, y1 - y0)
    for y in range(y0 + 2, y1, 7):
        for x in range((y * 3 + t // 20) % 16, 240, 16):
            R(SEAL, x, y, 4, 1)


def ground(c, c2, y0):
    R(c, 0, y0, 240, 160 - y0)
    for y in range(y0 + 3, 160, 6):
        for x in range((y * 5) % 9, 240, 9):
            R(c2, x, y, 2, 1)


def scene(theme, t=0):
    LW.fill(SKY)
    R(SKY2, 0, 30, 240, 26)
    cloud(30, 14)
    cloud(150, 22)
    cloud(205, 8)
    if theme == "shore":
        waves(55, 82, t)
        ground(SAND, SANDD, 80)
        palm(18, 62)
        palm(210, 66)
        rock(100, 130)
        rock(150, 140)
    elif theme == "bridges":
        for x in (8, 70, 130, 200):
            tree(x, 54)
        ground(GRASS, GRASS2, 72)
        waves(90, 108, t)
        for x, c in ((26, WOODC), (170, STONE)):
            R(c, x, 88, 26, 22)
            for yy in range(90, 110, 4):
                R(WOODD if c == WOODC else (110, 110, 120), x, yy, 26, 1)
            R(LEAF if c == WOODC else (130, 130, 140), x, 88, 26, 3)
    elif theme == "tide":
        waves(52, 72, t)
        ground(SAND, SANDD, 70)
        for x, y, w in ((24, 104, 40), (110, 116, 50), (180, 98, 32)):
            pygame.draw.ellipse(LW, SEAC, (x - 2, y - 1, w + 4, 16))
            pygame.draw.ellipse(LW, SEAL, (x, y, w, 12))
        for x, y in ((20, 100), (68, 112), (104, 120), (166, 104), (214, 112)):
            rock(x, y)
    elif theme == "rope":
        for x in (10, 90, 160):
            mountain(x, 26, 80, 46)
        ground(GRASS, GRASS2, 72)
        R(DARKC, 80, 72, 80, 88)
        R((70, 50, 40), 76, 72, 4, 88)
        R((70, 50, 40), 160, 72, 4, 88)
        R(WOODD, 76, 92, 88, 4)
        for x in range(78, 164, 4):
            R(WOODC, x, 92, 2, 4)
        R(TRUNK, 76, 85, 88, 1)
        R(TRUNK, 76, 84, 2, 10)
        R(TRUNK, 162, 84, 2, 10)
    elif theme == "cave":
        mountain(0, 18, 120, 62, (110, 115, 130))
        mountain(110, 26, 130, 54, (130, 135, 150))
        ground(GRASS, GRASS2, 80)
        pygame.draw.circle(LW, DARKC, (118, 78), 20)
        R(GRASS, 98, 78, 40, 4)
        R(DARKC, 98, 66, 40, 14)
        rock(80, 86)
        rock(150, 90)
    elif theme == "jungle":
        ground(GRASS2, LEAFD, 60)
        for x in range(0, 240, 20):
            tree(x, 36 + (x % 3) * 5, LEAFD)
        for x in (50, 100, 170):
            palm(x, 66, True)
    elif theme == "temple":
        mountain(120, 20, 120, 60, (120, 125, 140))
        ground(GRASS, GRASS2, 84)
        R(STONE, 70, 40, 100, 46)
        R((110, 110, 120), 64, 34, 112, 8)
        for x in (76, 98, 136, 156):
            R((190, 190, 200), x, 42, 6, 44)
        R(DARKC, 110, 58, 20, 28)
        for i in range(4):
            R((170, 170, 180), 62 - i * 3, 86 + i * 3, 116 + i * 6, 3)
        R(LEAF, 70, 40, 3, 20)
        R(LEAF, 165, 42, 3, 26)
    elif theme == "marsh":
        LW.fill((150, 170, 170))
        R((175, 195, 195), 0, 20, 240, 40)
        ground((78, 112, 92), (58, 92, 72), 66)
        for x, y, w in ((20, 100, 46), (100, 112, 56), (170, 96, 40)):
            pygame.draw.ellipse(LW, (96, 140, 150), (x, y, w, 12))
        for x in range(6, 240, 20):
            R((54, 92, 60), x, 60 + (x % 7), 1, 18)
            R((54, 92, 60), x + 2, 58 + (x % 5), 1, 18)
        for x in (30, 120, 200):
            R(TRUNK, x, 50, 2, 30)
            R(TRUNK, x - 4, 56, 10, 1)
    elif theme == "dock":
        waves(55, 160, t)
        R(WOODC, 0, 92, 240, 16)
        for x in range(0, 240, 8):
            R(WOODD, x, 92, 1, 16)
        for x in (10, 90, 170, 230):
            R(WOODD, x, 108, 3, 20)
        pygame.draw.polygon(LW, WOODD, [(140, 70), (200, 70), (190, 82), (150, 82)])
        R(TRUNK, 168, 46, 2, 24)
        pygame.draw.polygon(LW, WHITE, [(171, 48), (171, 66), (190, 66)])
    pygame.transform.scale(LW, (W, H), screen)


# ------------------------------------------------------------------ pixel characters
_sp = {}


def sprite(kind, col):
    if (kind, col) in _sp:
        return _sp[(kind, col)]
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    OUT = (45, 28, 20)
    dark = tuple(max(0, v - 60) for v in col)
    light = tuple(min(255, v + 50) for v in col)
    el = lambda c, x, y, w, h, o=0: pygame.draw.ellipse(s, c, (x, y, w, h), o)
    rc = lambda c, x, y, w, h: pygame.draw.rect(s, c, (x, y, w, h))
    pl = lambda c, pts: pygame.draw.polygon(s, c, pts)
    el((0, 0, 0, 70), 6, 28, 20, 3)
    if kind in ("player", "captain"):
        shirt = (200, 60, 60) if kind == "player" else (40, 70, 130)
        rc(shirt, 10, 20, 12, 8)
        rc(OUT, 10, 20, 12, 1)
        rc((90, 60, 40), 11, 28, 4, 2)
        rc((90, 60, 40), 17, 28, 4, 2)
        el(col, 9, 6, 14, 15)
        el(OUT, 9, 6, 14, 15, 1)
        rc(WHITE, 12, 13, 3, 3)
        rc(WHITE, 18, 13, 3, 3)
        rc(OUT, 13, 14, 1, 2)
        rc(OUT, 19, 14, 1, 2)
        rc(OUT, 14, 18, 4, 1)
        if kind == "player":
            el(GOLD, 4, 5, 24, 5)
            el(GOLD, 10, 1, 12, 8)
            rc((190, 60, 40), 10, 6, 12, 1)
        else:
            pl((30, 40, 70), [(5, 8), (16, 0), (27, 8)])
            rc(GOLD, 5, 8, 22, 1)
    else:
        if kind == "crab":
            for cx in (1, 25):
                el(col, cx, 6, 7, 7)
                el(OUT, cx, 6, 7, 7, 1)
        if kind == "fox":
            for sx in (1, -1):
                x0 = 8 if sx == 1 else 24
                pl(col, [(x0, 11), (x0 + 3 * sx, 1), (x0 + 7 * sx, 11)])
        if kind in ("monkey", "gorilla"):
            for cx in (2, 24):
                el(light, cx, 11, 6, 6)
                el(OUT, cx, 11, 6, 6, 1)
        if kind == "turtle":
            el(dark, 3, 14, 26, 15)
            el(OUT, 3, 14, 26, 15, 1)
        if kind == "parrot":
            for dx in (-3, 0, 3):
                pygame.draw.line(s, (220, 50, 50), (16, 8), (16 + dx, 2), 2)
        el(col, 6, 8, 20, 20)
        el(OUT, 6, 8, 20, 20, 1)
        if kind in ("monkey", "gorilla"):
            el(light, 9, 15, 14, 11)
        if kind == "fox":
            el((250, 240, 225), 9, 18, 14, 9)
        if kind == "turtle":
            for x, y in ((9, 21), (15, 19), (21, 21)):
                rc(dark, x, y, 3, 3)
        for ex in (11, 19):
            rc(WHITE, ex, 14, 3, 3)
            rc(OUT, ex + 1, 15, 1, 2)
        if kind == "gorilla":
            rc(OUT, 10, 12, 12, 1)
        if kind in ("gull", "parrot"):
            pl((250, 160, 30), [(14, 19), (18, 19), (16, 24)])
        else:
            rc(OUT, 14, 22, 4, 1)
    _sp[(kind, col)] = s
    return s


def draw_char(cx, feet, kind, col, k=6):
    img = pygame.transform.scale(sprite(kind, col), (32 * k, 32 * k))
    screen.blit(img, (cx - 16 * k, feet - 30 * k))


CHARS = {
    "You": ("player", (240, 190, 140)),
    "Gus the Gull": ("gull", (225, 230, 240)),
    "Penny the Pelican": ("gull", (255, 215, 190)),
    "Tess the Turtle": ("turtle", (90, 170, 100)),
    "Sheldon the Snapper": ("turtle", (80, 120, 165)),
    "Clara the Crab": ("crab", (225, 90, 70)),
    "Pete the Parrot": ("parrot", (70, 170, 90)),
    "Kiki the Kiwi": ("parrot", (150, 100, 200)),
    "Fenwick the Fox": ("fox", (225, 130, 50)),
    "Rusty the Raccoon": ("fox", (150, 150, 165)),
    "Moe the Monkey": ("monkey", (150, 100, 60)),
    "Bongo the Baboon": ("monkey", (190, 130, 90)),
    "Grizelda the Gorilla": ("gorilla", (85, 85, 100)),
    "Gorg the Gorilla": ("gorilla", (60, 110, 75)),
    "Captain Nash": ("captain", (235, 195, 150)),
}


# ------------------------------------------------------------------ game-theory helpers
def nash(pay):
    R_, C_ = len(pay), len(pay[0])
    out = set()
    for r in range(R_):
        for c in range(C_):
            if all(pay[r][c][0] >= pay[r2][c][0] for r2 in range(R_)) and all(pay[r][c][1] >= pay[r][c2][1] for c2 in range(C_)):
                out.add((r, c))
    return out


def cell_rect(x, y, cw, ch, r, c):
    return pygame.Rect(x + c * cw, y + r * ch, cw, ch)


def draw_matrix(pay, rows, cols, x, y, cw, ch, hint=False, last=None, sel=(), dead_r=(), dead_c=()):
    R_, C_ = len(rows), len(cols)
    f = FB if cw >= 120 else getf(20, True)
    lf = FB if cw >= 120 else getf(18, True)
    ar = [r for r in range(R_) if r not in dead_r]
    ac = [c for c in range(C_) if c not in dead_c]
    for c in range(C_):
        text(cols[c], lf, GREY if c in dead_c else INK, x + c * cw + cw // 2, y - 32, center=True)
    for r in range(R_):
        img = lf.render(rows[r], True, GREY if r in dead_r else INK)
        screen.blit(img, img.get_rect(midright=(x - 10, y + r * ch + ch // 2)))
    for r in range(R_):
        for c in range(C_):
            rc = cell_rect(x, y, cw, ch, r, c)
            dead = r in dead_r or c in dead_c
            pygame.draw.rect(screen, (200, 190, 175) if dead else ((255, 225, 140) if (r, c) in sel else (255, 248, 228)), rc)
            pygame.draw.rect(screen, INK, rc, 3)
            a, b = pay[r][c]
            ia, ib = f.render(fmt(a), True, GREY if dead else BLUE), f.render(fmt(b), True, GREY if dead else RED)
            ra = ia.get_rect(center=(rc.centerx - cw // 4, rc.centery))
            rb = ib.get_rect(center=(rc.centerx + cw // 4, rc.centery))
            screen.blit(ia, ra)
            screen.blit(ib, rb)
            screen.blit(f.render(",", True, INK), (rc.centerx - 3, rc.centery - 4))
            if hint and not dead:
                if a == max(pay[rr][c][0] for rr in ar):
                    pygame.draw.line(screen, BLUE, (ra.left - 3, ra.bottom + 3), (ra.right + 3, ra.bottom + 3), 4)
                if b == max(pay[r][cc][1] for cc in ac):
                    pygame.draw.line(screen, RED, (rb.left - 3, rb.bottom + 3), (rb.right + 3, rb.bottom + 3), 4)
            if last == (r, c):
                pygame.draw.rect(screen, GOLD, rc, 6)


def mdims(pay, maxw=520, maxh=190):
    return min(190, maxw // len(pay[0])), min(95, maxh // len(pay))


# ------------------------------------------------------------------ trees (extensive form)
def N(name, mover, acts):
    return {"n": name, "p": mover, "a": acts}


def _norm(n):
    if isinstance(n, tuple):
        return {"u": n}
    if "u" in n:
        return n
    n["a"] = [(l, _norm(c)) for l, c in n["a"]]
    return n


def _nleaves(n):
    return 1 if "u" in n else sum(_nleaves(c) for _, c in n["a"])


def _height(n):
    return 0 if "u" in n else 1 + max(_height(c) for _, c in n["a"])


def layout(root, x0, x1, y0, y1):
    pos, cnt, nl, h = {}, [0], _nleaves(root), _height(root)

    def rec(n, d):
        if "u" in n:
            x, y = x0 + (cnt[0] + 0.5) * (x1 - x0) / nl, y1
            cnt[0] += 1
        else:
            xs = [rec(c, d + 1) for _, c in n["a"]]
            x, y = (xs[0] + xs[-1]) / 2, y0 + d * (y1 - y0) / max(1, h)
        pos[id(n)] = (int(x), int(y))
        return x

    rec(root, 0)
    return pos


def draw_tree(root, names, pos, chosen=None, cur=None):
    chosen = chosen or {}
    lf = getf(14, True)

    def edges(n):
        if "u" in n:
            return
        for j, (lab, c) in enumerate(n["a"]):
            a, b = pos[id(n)], pos[id(c)]
            on = chosen.get(id(n)) == j
            pygame.draw.line(screen, GREEN if on else INK, a, b, 7 if on else 3)
            edges(c)

    edges(root)

    def labels(n):
        if "u" in n:
            return
        for lab, c in n["a"]:
            a, b = pos[id(n)], pos[id(c)]
            img = lf.render(lab, True, INK)
            rc = img.get_rect(center=((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)).inflate(8, 2)
            pygame.draw.rect(screen, CREAM, rc)
            screen.blit(img, img.get_rect(center=rc.center))
            labels(c)

    labels(root)

    def nodes(n):
        x, y = pos[id(n)]
        if "u" in n:
            pygame.draw.rect(screen, GOLD, (x - 8, y - 8, 16, 16))
            pygame.draw.rect(screen, INK, (x - 8, y - 8, 16, 16), 2)
            a, b = n["u"]
            ia, ib = getf(15, True).render(fmt(a), True, BLUE), getf(15, True).render(fmt(b), True, RED)
            comma = getf(15, True).render(",", True, INK)
            tw = ia.get_width() + comma.get_width() + ib.get_width()
            x0 = x - tw // 2
            screen.blit(ia, (x0, y + 11))
            screen.blit(comma, (x0 + ia.get_width(), y + 11))
            screen.blit(ib, (x0 + ia.get_width() + comma.get_width(), y + 11))
            return
        for _, c in n["a"]:
            nodes(c)
        if cur is n:
            pygame.draw.circle(screen, GOLD, (x, y), 25)
        pygame.draw.circle(screen, INK, (x, y), 21)
        pygame.draw.circle(screen, BLUE if n["p"] == 0 else RED, (x, y), 18)
        text(n["n"], getf(16, True), WHITE, x, y - 10, center=True)

    nodes(root)
    text("blue = %s     red = %s" % (names[0], names[1]), FS, INK, 70, 150)


# ------------------------------------------------------------------ scenes
class Dialogue:
    def __init__(s, enemy, theme, lines, links=None):
        s.enemy, s.theme, s.lines, s.i, s.done = enemy, theme, lines, 0, False
        s.lb = []
        if links:
            n = len(links)
            w = min(280, 650 // n - 6)
            s.lb = [(Button((170 + i * (w + 6), 8, w, 36), ("Watch: " if n <= 2 else "") + t, (170, 50, 50)), u) for i, (t, u) in enumerate(links)]

    def event(s, ev):
        for b, u in s.lb:
            if b.hit(ev):
                open_url(u)
                return
        if (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1) or (
                ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_RETURN)):
            s.i += 1
            s.done = s.i >= len(s.lines)

    def draw(s):
        scene(s.theme)
        who, line = s.lines[min(s.i, len(s.lines) - 1)]
        if s.enemy:
            k, c = CHARS[s.enemy]
            draw_char(190, 405, k, c, 7 if who == s.enemy else 6)
        k, c = CHARS["You"]
        draw_char(780, 405, k, c, 7 if who == "You" else 6)
        panel((30, 415, 900, 205))
        text(who, FB, (150, 80, 20), 56, 430)
        fit(line, (56, 465, 848, 118), sizes=(23, 21, 19, 17, 15, 13))
        text("tap / click / SPACE to continue", getf(14), GREY, 690, 590)
        for b, _ in s.lb:
            b.draw()


class Quiz:
    def __init__(s, title, theme, qs, extra=None, optional=False):
        s.title, s.theme, s.qs, s.extra = title, theme, qs, extra
        s.qi, s.state, s.done, s.choose = 0, "ask", False, optional
        s.next = Button((700, 560, 200, 44), "Continue", GREENB)
        s.take = Button((110, 330, 360, 70), "Take the quiz (recommended)", GREENB)
        s.skip = Button((490, 330, 360, 70), "Skip the quiz", PURP)
        s.mk()

    def mk(s):
        q = s.qs[s.qi]
        s.order = list(range(len(q["opts"])))
        random.shuffle(s.order)
        s.btns = [Button((60, 410 + i * 52, 840, 44), q["opts"][j]) for i, j in enumerate(s.order)]

    def event(s, ev):
        if s.choose:
            if s.take.hit(ev):
                s.choose = False
            elif s.skip.hit(ev):
                s.done = True
            return
        if s.state == "ask":
            for i, b in enumerate(s.btns):
                if b.hit(ev):
                    s.state = "right" if s.order[i] == s.qs[s.qi]["ans"] else "wrong"
        elif s.next.hit(ev):
            if s.state == "right":
                s.qi += 1
                if s.qi >= len(s.qs):
                    s.done = True
                    return
            s.mk()
            s.state = "ask"

    def draw(s):
        scene(s.theme)
        panel((30, 12, 900, 616))
        text(s.title, FB, INK, 50, 24)
        if s.choose:
            fit("Quiz time! A few quick questions check what you just learned. The quiz is OPTIONAL: take it to test yourself, or skip it and keep playing.", (80, 120, 800, 160), sizes=(26, 24, 22, 20), center=True)
            s.take.draw()
            s.skip.draw()
            return
        q = s.qs[s.qi]
        fit(f"Q{s.qi + 1}/{len(s.qs)}   " + q["q"], (50, 60, 860, 74), sizes=(22, 20, 18, 16))
        if s.extra:
            s.extra(s.qi, s)
        if s.state == "ask":
            for b in s.btns:
                b.draw()
        else:
            panel((50, 405, 860, 205), WHITE)
            ok = s.state == "right"
            text("Correct!" if ok else "Not quite.", FB, GREEN if ok else RED, 72, 424)
            fit(q["why"] if ok else q["hint"], (72, 460, 816, 96), sizes=(22, 20, 18, 16, 14))
            s.next.label = "Continue" if ok else "Try again"
            s.next.draw()


def Q(q, opts, ans, why, hint):
    return dict(q=q, opts=opts, ans=ans, why=why, hint=hint)


def matrix_extra(pay, rows, cols):
    cw, ch = mdims(pay, 520, 170)

    def f(qi, s):
        x = 480 - cw * len(cols) // 2
        draw_matrix(pay, rows, cols, x, 195, cw, ch, True)
        text("blue = you, red = them. Underlines mark best replies.", FS, INK, 250, 384)
    f.meta = ("matrix", pay, rows, cols)
    return f


def info_extra(*lines_by_q):
    """lines_by_q[qi] = text shown above the options for question qi (last one reused)."""
    def f(qi, s):
        fit(lines_by_q[min(qi, len(lines_by_q) - 1)], (80, 150, 800, 235), sizes=(22, 20, 18, 16))
    f.meta = ("info", list(lines_by_q))
    return f


def tree_extra(treefn, names):
    root = _norm(treefn())
    pos = layout(root, 90, 870, 190, 330)

    def f(qi, s):
        draw_tree(root, names, pos)
    f.meta = ("tree", treefn, names)
    return f


class MatrixPlay:
    def __init__(s, cfg):
        s.c = cfg
        s.total = cfg.get("rounds")
        s.win = cfg.get("win", lambda sc, n: sc[0] >= sc[1])
        R_ = len(cfg["rows"])
        w = min(180, 380 // R_ - 8)
        s.rb = [Button((170 + i * (w + 8), 470, w, 48), "Play " + n) for i, n in enumerate(cfg["rows"])]
        s.hb = Button((170, 548, 370, 40), "Toggle: show best replies", PURP)
        s.cont = Button((170, 470, 370, 50), "Continue", GREENB)
        s.hint, s.done = False, False
        s.reset()

    def reset(s):
        s.hist, s.sc, s.last, s.over = [], [0, 0], None, False

    def event(s, ev):
        if s.hb.hit(ev):
            s.hint = not s.hint
        if s.over:
            if s.cont.hit(ev):
                if s.win(s.sc, len(s.hist)):
                    s.done = True
                else:
                    s.reset()
            return
        for r, b in enumerate(s.rb):
            if b.hit(ev):
                c = s.c["enemy"](s.hist, len(s.hist), s.total)
                a, e = s.c["pay"][r][c]
                s.sc[0] += a
                s.sc[1] += e
                s.hist.append((r, c))
                s.last = (r, c)
                n = len(s.hist)
                s.over = n >= s.total if s.total else (n >= 25 or (n >= 6 and random.random() > 0.9))

    def draw(s):
        c = s.c
        scene(c["theme"])
        panel((30, 12, 900, 616))
        text(c["title"], FB, INK, 50, 24)
        fit(c["tip"], (50, 58, 860, 40), sizes=(18, 16, 14))
        fit(c["goal"], (50, 100, 860, 24), col=GREEN, sizes=(18, 16, 14), bold=True)
        cw, ch = mdims(c["pay"], 400, 190)
        draw_matrix(c["pay"], c["rows"], c["cols"], 170, 195, cw, ch, s.hint, s.last)
        text("blue = YOU        red = " + c["short"], FS, INK, 170, 398)
        n = len(s.hist)
        if s.total:
            text(f"Round {min(n + 1, s.total)} of {s.total}", FB, INK, 610, 140)
        else:
            fit("Round %d  (each round has a 90%% chance of another)" % (n + 1), (610, 140, 290, 40), sizes=(20, 16))
        text(f"You: {fmt(s.sc[0])}      {c['short']}: {fmt(s.sc[1])}", FM, INK, 610, 180)
        if not s.total:
            text(f"Your average: {s.sc[0] / max(1, n):.2f} per round", FM, INK, 610, 210)
        if c.get("mood"):
            m, mc = c["mood"](s.hist)
            fit(c["short"] + " feels: " + m, (610, 240, 290, 40), col=mc, sizes=(20, 16))
        text("Recent rounds:", FS, INK, 610, 290)
        y = 312
        for i, (r, cc) in list(enumerate(s.hist))[-6:]:
            a, e = c["pay"][r][cc]
            text(f"R{i + 1}: you {c['rows'][r]} / they {c['cols'][cc]}  ({fmt(a)} / {fmt(e)})", getf(15), INK, 610, y)
            y += 22
        if s.over:
            ok = s.win(s.sc, n)
            msg = "You win or tie! Well played." if ok else "You lost this match. Think again and retry."
            fit(msg, (170, 420, 400, 40), col=GREEN if ok else RED, sizes=(22, 18), bold=True)
            s.cont.label = "Continue" if ok else "Retry the match"
            s.cont.draw()
        else:
            for b in s.rb:
                b.draw()
        s.hb.draw()


class NashPicker:
    def __init__(s, cfg):
        s.c, s.sel, s.msg, s.ok, s.done, s.hint = cfg, set(), "", False, False, False
        s.chk = Button((250, 500, 200, 46), "Check", GREENB)
        s.hb = Button((470, 500, 200, 46), "Show best replies", PURP)
        s.cw, s.ch = mdims(cfg["pay"], 540, 230)

    def event(s, ev):
        c = s.c
        if s.hb.hit(ev):
            s.hint = not s.hint
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and not s.ok:
            for r in range(len(c["rows"])):
                for cc in range(len(c["cols"])):
                    if cell_rect(250, 200, s.cw, s.ch, r, cc).collidepoint(ev.pos):
                        s.sel ^= {(r, cc)}
        if s.chk.hit(ev):
            if s.ok:
                s.done = True
                return
            N_, p, rows, cols = nash(c["pay"]), c["pay"], c["rows"], c["cols"]
            wrong = sorted(s.sel - N_)
            if not s.sel:
                s.msg = "Click the cell(s) you think are pure-strategy Nash equilibria first."
            elif wrong:
                r, cc = wrong[0]
                better = [r2 for r2 in range(len(rows)) if p[r2][cc][0] > p[r][cc][0]]
                if better:
                    why = f"you'd gain by switching to {rows[better[0]]}"
                else:
                    c2 = [c3 for c3 in range(len(cols)) if p[r][c3][1] > p[r][cc][1]][0]
                    why = f"they'd gain by switching to {cols[c2]}"
                s.msg = f"Not quite. In ({rows[r]}, {cols[cc]}) {why}, so someone wants to deviate."
            elif N_ - s.sel:
                s.msg = f"Right so far, but there are {len(N_)} pure equilibria in total. Keep looking!"
            else:
                s.ok = True
                s.msg = c.get("ok", "Correct! In every selected cell, nobody can gain by changing ONLY their own choice.")
                s.chk.label = "Continue"

    def draw(s):
        c = s.c
        scene(c["theme"])
        panel((30, 12, 900, 616))
        text(c["title"], FB, INK, 50, 24)
        fit("Click every cell that is a pure-strategy Nash equilibrium (each strategy is a best reply to the other), then press Check.", (50, 60, 860, 52), sizes=(22, 20, 18))
        draw_matrix(c["pay"], c["rows"], c["cols"], 250, 200, s.cw, s.ch, s.hint, None, s.sel)
        text("blue = you      red = them", FS, INK, 250, 438)
        fit(s.msg, (250, 458, 620, 36), col=GREEN if s.ok else RED, sizes=(18, 16, 14))
        s.chk.draw()
        s.hb.draw()


def dominated(pay, ar, ac, player, i, weak, mixed):
    mine, opp = (ar, ac) if player == 0 else (ac, ar)

    def u(a, o):
        return pay[a][o][0] if player == 0 else pay[o][a][1]
    others = [j for j in mine if j != i]
    for j in others:
        d = [u(j, o) - u(i, o) for o in opp]
        if (weak and all(x >= 0 for x in d) and any(x > 0 for x in d)) or (not weak and all(x > 0 for x in d)):
            return ("pure", j)
    if mixed:
        for a in others:
            for b in others:
                if a < b:
                    for k in range(1, 10):
                        q = k / 10
                        if all(q * u(a, o) + (1 - q) * u(b, o) - u(i, o) > 0 for o in opp):
                            return ("mix", (a, b, q))
    return None


class Eliminate:
    def __init__(s, cfg):
        s.c = cfg
        s.ar, s.ac = set(range(len(cfg["rows"]))), set(range(len(cfg["cols"])))
        s.msg, s.done, s.hint = "", False, False
        s.cw, s.ch = mdims(cfg["pay"], 540, 230)
        s.hb = Button((600, 548, 300, 40), "Toggle: show best replies", PURP)
        s.fin = Button((600, 490, 300, 46), "Finish", GREENB)

    def any_left(s):
        c = s.c
        for i in s.ar:
            if len(s.ar) > 1 and dominated(c["pay"], s.ar, s.ac, 0, i, c.get("weak", False), c.get("mixed", False)):
                return True
        for j in s.ac:
            if len(s.ac) > 1 and dominated(c["pay"], s.ar, s.ac, 1, j, c.get("weak", False), c.get("mixed", False)):
                return True
        return False

    def event(s, ev):
        c = s.c
        if s.hb.hit(ev):
            s.hint = not s.hint
        if not s.any_left() and s.fin.hit(ev):
            s.done = True
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            x, y = 250, 200
            target = None
            for r in s.ar:
                if pygame.Rect(x - 130, y + r * s.ch, 120, s.ch).collidepoint(ev.pos):
                    target = (0, r)
            for cc in s.ac:
                if pygame.Rect(x + cc * s.cw, y - 40, s.cw, 38).collidepoint(ev.pos):
                    target = (1, cc)
            if target:
                pl, i = target
                names = c["rows"] if pl == 0 else c["cols"]
                alive = s.ar if pl == 0 else s.ac
                if len(alive) < 2:
                    s.msg = "Only one strategy is left for that player."
                    return
                res = dominated(c["pay"], s.ar, s.ac, pl, i, c.get("weak", False), c.get("mixed", False))
                kind = "weakly " if c.get("weak") else "strictly "
                if res:
                    if res[0] == "pure":
                        s.msg = f"Yes! {names[i]} is {kind}dominated by {names[res[1]]}. Deleted."
                    else:
                        a, b, q = res[1]
                        s.msg = f"Yes! A {int(q * 100)}/{int(100 - q * 100)} mix of {names[a]} and {names[b]} strictly beats {names[i]}. Deleted."
                    alive.discard(i)
                    if not s.any_left():
                        s.msg += " " + c.get("stuck", "Nothing else can be deleted.")
                else:
                    s.msg = f"No: {names[i]} is not {kind}dominated by anything left. Look for a strategy that is worse than another one in EVERY remaining column/row."

    def draw(s):
        c = s.c
        scene(c["theme"])
        panel((30, 12, 900, 616))
        text(c["title"], FB, INK, 50, 24)
        fit(c["tip"], (50, 60, 860, 52), sizes=(20, 18, 16))
        dr, dc = set(range(len(c["rows"]))) - s.ar, set(range(len(c["cols"]))) - s.ac
        draw_matrix(c["pay"], c["rows"], c["cols"], 250, 200, s.cw, s.ch, s.hint, None, (), dr, dc)
        text("blue = you      red = them      (click a strategy NAME to delete it)", FS, INK, 150, 440)
        fit(s.msg, (60, 462, 520, 130), col=GREEN if s.msg.startswith("Yes") else RED, sizes=(20, 18, 16, 14))
        if not s.any_left():
            s.fin.draw()
        s.hb.draw()


def _num(sx):
    sx = sx.strip()
    if "/" in sx:
        a, b = sx.split("/", 1)
        return float(a) / float(b)
    return float(sx)


PAD_KEYS = [["7", "8", "9", "<"], ["4", "5", "6", "/"], ["1", "2", "3", "."], ["0", "-", "NEXT", "CLOSE"]]


class Calc:
    """problems: list of dict(prompt, matrix=(pay,rows,cols)|None, fields=[(label, value)], hints=[...], ok=str, wrong=fn|None, throw=(pay,p,q)|None)"""

    def __init__(s, theme, title, problems, pages=()):
        s.theme, s.title, s.P, s.pages = theme, title, problems, list(pages)
        s.phase = "learn" if s.pages else "solve"
        s.pg, s.pi, s.done = 0, 0, False
        s.nextb = Button((700, 545, 200, 44), "Next", GREENB)
        s.sub = Button((700, 400, 200, 44), "Check answer", GREENB)
        s.hintb = Button((700, 452, 200, 44), "Hint", PURP)
        s.padb = Button((580, 452, 110, 44), "Keypad", WOOD)
        s.cont = Button((700, 504, 200, 44), "Continue", GREENB)
        s.padchk = Button((300, 548, 376, 40), "Check answer", GREENB)
        s.start()

    def start(s):
        p = s.P[s.pi]
        s.vals, s.focus, s.msg, s.hints, s.solved, s.net, s.n, s.last, s.pad = [""] * len(p["fields"]), 0, "", 0, False, 0, 0, "", False

    def box(s, i):
        return pygame.Rect(430, 398 + i * 50, 130, 42)

    def padrect(s, r, c):
        return pygame.Rect(300 + c * 96, 330 + r * 54, 90, 48)

    def submit(s):
        p = s.P[s.pi]
        try:
            v = [_num(x) for x in s.vals]
        except (ValueError, ZeroDivisionError):
            s.msg = "Type numbers in every box first (decimals like 0.4 or fractions like 2/5)."
            return
        if all(abs(a - f[1]) <= p.get("tol", 0.012) for a, f in zip(v, p["fields"])):
            s.solved, s.msg, s.pad = True, p.get("ok", "Correct!"), False
        else:
            s.msg = p["wrong"](v) if p.get("wrong") else "Not quite. Re-check your algebra, or use a hint."

    def type_char(s, ch):
        if ch == "<":
            s.vals[s.focus] = s.vals[s.focus][:-1]
        elif len(s.vals[s.focus]) < 8:
            s.vals[s.focus] += ch

    def pad_click(s, pos):
        for r, row in enumerate(PAD_KEYS):
            for c, k in enumerate(row):
                if s.padrect(r, c).collidepoint(pos):
                    if k == "NEXT":
                        s.focus = (s.focus + 1) % len(s.vals)
                    elif k == "CLOSE":
                        s.pad = False
                    else:
                        s.type_char(k)
        if s.padchk.rect.collidepoint(pos):
            s.submit()

    def event(s, ev):
        if s.done or s.pi >= len(s.P):
            return
        p = s.P[s.pi]
        if s.phase == "learn":
            if s.nextb.hit(ev):
                s.pg += 1
                if s.pg >= len(s.pages):
                    s.phase = "solve"
                elif s.pg == len(s.pages) - 1:
                    s.nextb.label = "Let's try!"
            return
        if not s.solved:
            if s.pad and ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                s.pad_click(ev.pos)
                return
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_BACKSPACE:
                    s.type_char("<")
                elif ev.key == pygame.K_TAB:
                    s.focus = (s.focus + 1) % len(s.vals)
                elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    s.submit()
                elif ev.unicode and ev.unicode in "0123456789./-":
                    s.type_char(ev.unicode)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i in range(len(s.vals)):
                    if s.box(i).collidepoint(ev.pos):
                        s.focus = i
                        if EMS:
                            s.pad = True
            if s.padb.hit(ev):
                s.pad = True
            if s.sub.hit(ev):
                s.submit()
            if s.hintb.hit(ev):
                s.hints = min(len(p.get("hints", [])), s.hints + 1)
            return
        gate = True
        if p.get("throw"):
            pay, pp, qq = p["throw"]
            if s.hintb.hit(ev):
                for _ in range(20):
                    r = 0 if random.random() < pp else 1
                    c = 0 if random.random() < qq else 1
                    s.net += pay[r][c][0]
                s.n += 20
                s.last = (f"After {s.n} throws you are at {fmt(round(s.net, 2))}. " +
                          ("You win or tie, so you can move on!" if s.net >= 0 else "You're behind, but the odds favour you. Keep throwing!"))
            gate = s.n >= 20 and s.net >= 0
        if gate and s.cont.hit(ev):
            s.pi += 1
            if s.pi >= len(s.P):
                s.done = True
            else:
                s.start()

    def draw(s):
        scene(s.theme)
        panel((30, 12, 900, 616))
        text(s.title, FB, INK, 50, 24)
        if s.phase == "learn":
            body, mat = s.pages[s.pg]
            fit(body, (50, 80, 520 if mat else 860, 420), sizes=(26, 24, 22, 20, 18))
            if mat:
                pay, rows, cols = mat
                cw, ch = mdims(pay, 300, 190)
                draw_matrix(pay, rows, cols, 650, 190, cw if len(cols) > 2 else 110, ch if len(rows) > 2 else 80)
                text("blue = you, red = them", FS, INK, 640, 400)
            s.nextb.draw()
            return
        p = s.P[s.pi]
        fit(p["prompt"], (50, 58, 860, 76), sizes=(21, 19, 17, 15))
        if p.get("matrix"):
            pay, rows, cols = p["matrix"]
            cw, ch = min(170, 440 // len(cols)), min(90, 190 // len(rows))
            draw_matrix(pay, rows, cols, 150, 190, cw, ch)
        for i, (lab, _) in enumerate(p["fields"]):
            b = s.box(i)
            fit(lab, (50, b.y + 2, 370, 40), sizes=(20, 18, 16, 14))
            pygame.draw.rect(screen, WHITE if not s.solved else (225, 245, 225), b)
            pygame.draw.rect(screen, GOLD if (i == s.focus and not s.solved) else INK, b, 3)
            cur = "|" if (i == s.focus and not s.solved and pygame.time.get_ticks() // 500 % 2) else ""
            text(s.vals[i] + cur, FM, INK, b.x + 8, b.y + 8)
        hs = p.get("hints", [])
        if hs and not s.solved:
            text("Type a number or fraction. TAB switches boxes, ENTER checks.", getf(14), GREY, 640, 140)
            for i in range(s.hints):
                fit(hs[i], (640, 165 + i * 68, 260, 64), sizes=(17, 15, 13))
        if not s.solved:
            s.sub.draw()
            s.padb.draw()
            if hs:
                s.hintb.label = "Hint (%d/%d)" % (s.hints, len(hs))
                s.hintb.draw()
            fit(s.msg, (60, 548, 600, 62), col=RED, sizes=(19, 17, 15))
            if s.pad:
                panel((280, 250, 430, 350))
                fit(s.P[s.pi]["fields"][s.focus][0], (300, 262, 390, 26), sizes=(18, 16, 14), bold=True)
                pygame.draw.rect(screen, WHITE, (300, 292, 376, 32))
                pygame.draw.rect(screen, INK, (300, 292, 376, 32), 3)
                text(s.vals[s.focus], FM, INK, 308, 296)
                for r, row in enumerate(PAD_KEYS):
                    for c, k in enumerate(row):
                        Button(s.padrect(r, c), {"<": "DEL", "NEXT": "Next box", "CLOSE": "Close"}.get(k, k), PURP if k in ("<", "NEXT", "CLOSE") else WOOD).draw()
                s.padchk.draw()
                fit(s.msg, (300, 592, 376, 30), col=RED, sizes=(14, 12))
        else:
            fit(s.msg, (60, 548, 600, 62), col=GREEN, sizes=(19, 17, 15))
            gate = True
            if p.get("throw"):
                s.hintb.label = "Throw 20 pebbles"
                s.hintb.draw()
                fit(s.last, (60, 505, 620, 40), col=GREEN if s.net >= 0 else RED, sizes=(18, 16, 14))
                gate = s.n >= 20 and s.net >= 0
            s.cont.enabled = gate
            s.cont.draw()


class Tree:
    def __init__(s, cfg):
        s.c = cfg
        s.root = _norm(cfg["tree"]())
        s.names = cfg["names"]
        s.pos = layout(s.root, 90, 870, 175, 335)
        s.order = []

        def po(n):
            if "u" in n:
                return
            for _, c in n["a"]:
                po(c)
            s.order.append(n)
        po(s.root)
        s.chosen, s.ci, s.msg, s.done = {}, 0, "", False
        s.cont = Button((700, 560, 200, 44), "Continue", GREENB)
        s.mk()

    def val(s, n):
        return n["u"] if "u" in n else s.val(n["a"][s.chosen[id(n)]][1])

    def mk(s):
        s.btns = []
        if s.ci < len(s.order):
            acts = s.order[s.ci]["a"]
            w = 840 // len(acts) - 10
            s.btns = [Button((60 + i * (w + 10), 450, w, 46), lab) for i, (lab, _) in enumerate(acts)]

    def event(s, ev):
        if s.ci >= len(s.order):
            if s.cont.hit(ev):
                s.done = True
            return
        node = s.order[s.ci]
        for i, b in enumerate(s.btns):
            if b.hit(ev):
                vals = [s.val(c)[node["p"]] for _, c in node["a"]]
                who = s.names[node["p"]]
                if vals[i] == max(vals):
                    s.chosen[id(node)] = i
                    s.msg = f"Correct: {who} picks {node['a'][i][0]} (payoff {fmt(vals[i])})."
                    if vals.count(max(vals)) > 1:
                        s.msg += " Careful: another action ties, so there is another SPE too."
                    s.ci += 1
                    s.mk()
                else:
                    s.msg = f"Not quite. For {who}: " + ", ".join(f"{node['a'][j][0]} gives {fmt(v)}" for j, v in enumerate(vals)) + ". Pick the best one."

    def draw(s):
        c = s.c
        scene(c["theme"])
        panel((30, 12, 900, 616))
        text(c["title"], FB, INK, 50, 24)
        fit(c["prompt"], (50, 58, 860, 64), sizes=(20, 18, 16, 14))
        cur = s.order[s.ci] if s.ci < len(s.order) else None
        draw_tree(s.root, s.names, s.pos, s.chosen, cur)
        if cur:
            text(f"Solve the LOWEST unsolved node first. Node {cur['n']}: {s.names[cur['p']]} chooses...", FM, INK, 60, 412)
            for b in s.btns:
                b.draw()
        else:
            n, path, bits = s.root, [], []
            while "u" not in n:
                lab, ch = n["a"][s.chosen[id(n)]]
                path.append(lab)
                n = ch
            for nd in sorted(s.order, key=lambda z: z["n"]):
                bits.append(f"{nd['n']}: {nd['a'][s.chosen[id(nd)]][0]}")
            s.msg = "SPE (a choice at EVERY node): " + "; ".join(bits) + ".  Path of play: " + ", ".join(path) + f".  Payoffs ({fmt(n['u'][0])}, {fmt(n['u'][1])})."
            s.cont.draw()
        fit(s.msg, (60, 502, 630, 106), col=GREEN if (s.msg.startswith("Correct") or s.msg.startswith("SPE")) else RED, sizes=(18, 16, 14, 12))


class TwoStage:
    def __init__(s, cfg):
        s.c, s.done = cfg, False
        s.cont = Button((600, 520, 300, 50), "Continue", GREENB)
        s.reset()

    def reset(s):
        s.stage, s.o1, s.o2, s.tot = 1, None, None, [0, 0]

    def rb(s, stage):
        c = s.c
        rows = c["rows1"] if stage == 1 else c["rows2"]
        x = 120 if stage == 1 else 580
        return [Button((x + i * 125, 420, 115, 44), "Play " + n) for i, n in enumerate(rows)]

    def event(s, ev):
        c = s.c
        if s.stage in (1, 2):
            for i, b in enumerate(s.rb(s.stage)):
                if b.hit(ev):
                    if s.stage == 1:
                        col = c["e1"]
                        s.o1 = (i, col)
                        a, e = c["m1"][i][col]
                    else:
                        col = c["e2"](s.o1)
                        s.o2 = (i, col)
                        a, e = c["m2"][i][col]
                    s.tot[0] += a
                    s.tot[1] += e
                    s.stage += 1
        elif s.cont.hit(ev):
            if s.tot[0] >= c["goal"]:
                s.done = True
            else:
                s.reset()

    def draw(s):
        c = s.c
        scene(c["theme"])
        panel((30, 12, 900, 616))
        text(c["title"], FB, INK, 50, 24)
        fit(c["tip"], (50, 58, 860, 52), sizes=(19, 17, 15))
        fit(c.get("goal_text") or f"Goal: finish with a combined total of at least {c['goal']} points to move on.", (50, 112, 860, 24), col=GREEN, sizes=(18, 16, 14), bold=True)
        text("STAGE 1" + ("   <- your move" if s.stage == 1 else ""), FM, INK, 120, 152)
        text("STAGE 2" + ("   <- your move" if s.stage == 2 else ""), FM, INK, 580, 152)
        draw_matrix(c["m1"], c["rows1"], c["cols1"], 140, 215, 110, 80, False, s.o1)
        draw_matrix(c["m2"], c["rows2"], c["cols2"], 600, 215, 110, 80, False, s.o2)
        text("blue = you, red = " + c["short"], FS, INK, 140, 385)
        text(f"Your total: {fmt(s.tot[0])}      {c['short']}: {fmt(s.tot[1])}", FM, INK, 140, 500)
        if s.stage in (1, 2):
            for b in s.rb(s.stage):
                b.draw()
        else:
            ok = s.tot[0] >= c["goal"]
            fit("You reached the goal! The threat of punishment kept cooperation alive." if ok else "Short of the goal. Look at what the enemy does in stage 2 after each stage-1 outcome.",
                (140, 535, 440, 70), col=GREEN if ok else RED, sizes=(19, 17, 15))
            s.cont.label = "Continue" if ok else "Retry"
            s.cont.draw()


class Hotelling:
    def __init__(s, theme):
        s.theme, s.pos, s.enemy, s.share, s.msg, s.done, s.tries = theme, None, None, None, "", False, 0
        s.cont = Button((700, 540, 200, 44), "Continue", GREENB)

    def event(s, ev):
        if s.share is not None and s.share >= 50 and s.cont.hit(ev):
            s.done = True
            return
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and pygame.Rect(100, 230, 760, 110).collidepoint(ev.pos):
            x = round((ev.pos[0] - 100) / 7.6)
            e = x + 1 if x < 50 else x - 1 if x > 50 else 50
            s.pos, s.enemy, s.tries = x, e, s.tries + 1
            if e == x:
                s.share = 50
            else:
                m = (x + e) / 2
                s.share = m if x < e else 100 - m
            s.msg = (f"You set up at {x}; Rusty answered at {e}. Customers go to the nearer stand, so your share is {s.share:.1f}%. " +
                     ("You win or tie: you can move on!" if s.share >= 50 else "Rusty squeezed you! Try another spot."))

    def draw(s):
        scene(s.theme)
        panel((30, 12, 900, 616))
        text("Hotelling's Beach - Median Voter", FB, INK, 50, 24)
        fit("Customers are spread evenly along the beach (0 to 100) and walk to the NEAREST ice cream stand. Click to place your stand. Rusty then places his stand wherever is best against you. Win or tie to move on.", (50, 60, 860, 90), sizes=(20, 18, 16))
        pygame.draw.rect(screen, SAND, (100, 270, 760, 30))
        pygame.draw.rect(screen, INK, (100, 270, 760, 30), 3)
        for i in range(0, 101, 10):
            x = 100 + i * 7.6
            pygame.draw.line(screen, INK, (x, 300), (x, 310), 2)
            text(str(i), getf(14), INK, x, 312, center=True)
        for who, x, col in (("YOU", s.pos, BLUE), ("RUSTY", s.enemy, RED)):
            if x is not None:
                px = 100 + x * 7.6
                pygame.draw.rect(screen, col, (px - 10 + (12 if who == "RUSTY" and s.pos == s.enemy else 0), 235, 20, 34))
                text(who, getf(14, True), col, px + (12 if who == "RUSTY" and s.pos == s.enemy else 0), 215, center=True)
        if s.share is not None:
            pygame.draw.rect(screen, BLUE, (100, 360, int(7.6 * s.share), 28))
            pygame.draw.rect(screen, RED, (100 + int(7.6 * s.share), 360, 760 - int(7.6 * s.share), 28))
            pygame.draw.rect(screen, INK, (100, 360, 760, 28), 3)
            text(f"your customers {s.share:.1f}%", getf(16, True), WHITE, 110, 364)
            fit(s.msg, (60, 410, 800, 100), col=GREEN if s.share >= 50 else RED, sizes=(20, 18, 16))
            if s.share >= 50:
                s.cont.draw()


# ------------------------------------------------------------------ level builder + helpers
PRAISE = ["Nicely done! Take your token.", "Impressive. On to the next challenge.", "You're thinking like a strategist now.", "Good play. The island respects you."]


def D(enemy, theme, lines, links=None):
    who = {"E": enemy, "Y": "You", "N": "Narrator"}
    return Dialogue(enemy, theme, [(who[w], t) for w, t in lines], links)


def lvl(name, enemy, theme, intro, acts, lesson, qs, extra=None):
    def build():
        links = [(t, lecture_url(sl)) for t, sl in LINKS.get(name, [])]
        sc = [D(enemy, theme, intro, links)]
        sc += [a() for a in acts]
        if lesson:
            sc.append(D(enemy, theme, [("N", t) for t in (lesson if isinstance(lesson, list) else [lesson])], links))
        if qs:
            sc.append(Quiz(name + " - Quiz", theme, qs, extra, optional=True))
        sc.append(D(enemy, theme, [("E", random.choice(PRAISE))]))
        return sc
    return (name, build)


def e_always(c):
    f = lambda h, i, t: c
    f.meta = ("always", c)
    return f


def e_random(h, i, t):
    return random.randint(0, 1)


GOAL_TIE = "Goal: finish with at least as many points as {} (win or tie) to move on."


# ------------------------------------------------------------------ gamified scenes
class MoneyPump:
    PREF = {("B", "A"), ("C", "B"), ("A", "C")}  # (x, y): Kiki prefers x to y

    def __init__(s, theme, goal=6):
        s.theme, s.goal, s.coins, s.hold, s.msg, s.done = theme, goal, 0, "A", "", False
        s.btns = [(x, Button((90 + i * 280, 440, 250, 56), f"Offer item {x}")) for i, x in enumerate("ABC")]
        s.cont = Button((700, 545, 200, 44), "Continue", GREENB)

    def event(s, ev):
        if s.coins >= s.goal:
            if s.cont.hit(ev):
                s.done = True
            return
        for x, b in s.btns:
            if b.hit(ev):
                if x == s.hold:
                    s.msg = "She already holds that item."
                elif (x, s.hold) in s.PREF:
                    s.coins += 1
                    s.msg = f"She prefers {x} to {s.hold}, so she swaps and pays you a coin!"
                    s.hold = x
                else:
                    s.msg = f"She prefers {s.hold} to {x}, so she refuses the swap."
                if s.coins >= s.goal:
                    s.msg = "A MONEY PUMP! Her preferences cycle (B over A, C over B, A over C), so you can trade her around the loop forever and collect coins. Transitivity matters."

    def draw(s):
        scene(s.theme)
        panel((30, 12, 900, 616))
        text("The Money Pump", FB, INK, 50, 24)
        fit("Kiki prefers B to A, C to B, and A to C (a cycle!). She holds item A and pays you 1 coin for any swap to an item she prefers. Offer items to pump coins out of her. Goal: %d coins." % s.goal, (50, 60, 860, 70), sizes=(21, 19, 17))
        k, c = CHARS["Kiki the Kiwi"]
        draw_char(200, 400, k, c, 5)
        panel((400, 160, 220, 150), WHITE)
        text("Kiki holds", FM, INK, 510, 172, center=True)
        text(s.hold, FT, BLUE, 510, 210, center=True)
        text(f"Coins: {s.coins} / {s.goal}", FB, (150, 80, 20), 660, 200)
        fit(s.msg, (60, 505, 600, 100), col=GREEN if s.coins >= s.goal else INK, sizes=(20, 18, 16))
        if s.coins >= s.goal:
            s.cont.draw()
        else:
            for _, b in s.btns:
                b.draw()


class Unravel:
    R = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(s, theme):
        s.theme, s.nxt, s.msg, s.done = theme, 0, "", False
        s.cont = Button((700, 545, 200, 44), "Continue", GREENB)

    def rect(s, i):
        return pygame.Rect(40 + i * 68, 220, 62, 90)

    def event(s, ev):
        if s.nxt >= 12:
            if s.cont.hit(ev):
                s.done = True
            return
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for i in range(13):
                if s.rect(i).collidepoint(ev.pos):
                    if i == 12:
                        s.msg = "The Ace can never lose, so it always bets. Tap the card that folds NEXT instead."
                    elif i < s.nxt:
                        s.msg = "That card already folded."
                    elif i == s.nxt:
                        s.nxt += 1
                        if i == 0:
                            s.msg = "The 2 loses to every other card, so betting with it only loses money. It folds."
                        else:
                            s.msg = f"Every worse hand already folds, so the {s.R[i]} can only win against hands that fold anyway. Betting just risks money, so it folds too."
                        if s.nxt >= 12:
                            s.msg += "  Only the ACE bets! That chain reaction is called UNRAVELING."
                    else:
                        s.msg = "Not yet! Start from the WORST hand still betting. Which weakest card has no reason to bet?"

    def draw(s):
        scene(s.theme)
        panel((30, 12, 900, 616))
        text("Poker Unraveling", FB, INK, 50, 24)
        fit("Each player draws one card from 2 up to Ace. Both can bet $1 or fold, and the higher card wins. Tap the cards in the order they FOLD, starting with the first hand that should never bet.", (50, 60, 860, 90), sizes=(21, 19, 17))
        for i in range(13):
            r = s.rect(i)
            folded = i < s.nxt
            pygame.draw.rect(screen, (190, 180, 165) if folded else (255, 248, 228), r)
            pygame.draw.rect(screen, INK, r, 3)
            text(s.R[i], FB, GREY if folded else (RED if s.R[i] in "JQKA" else INK), r.centerx, r.y + 14, center=True)
            text("FOLD" if folded else ("BET" if (s.nxt >= 12 and i == 12) else ""), getf(14, True), GREY if folded else GREEN, r.centerx, r.y + 56, center=True)
        fit(s.msg, (60, 340, 840, 150), col=INK, sizes=(22, 20, 18, 16))
        if s.nxt >= 12:
            s.cont.draw()


class Signal:
    BEL = [0.0, 0.5, 1.0]

    def __init__(s, cfg):
        s.c, s.strat, s.off, s.t, s.msg, s.rep, s.done, s.solved = cfg, [0, 0], 0, 0, "", "", False, False
        s.tb = [Button((400, 140 + i * 56, 380, 46), "") for i in range(2)]
        s.ob = Button((50, 258, 730, 46), "", PURP)
        s.test = Button((50, 316, 240, 46), "Test these strategies", GREENB)
        s.cont = Button((700, 560, 200, 44), "Continue", GREENB)
        s.refresh()

    def refresh(s):
        c = s.c
        for i, b in enumerate(s.tb):
            b.label = f"plays: {c['acts'][s.strat[i]]}  (tap to change)"
        s.ob.label = f"Unseen action => receiver believes P({c['types'][0][0]}) = {s.BEL[s.off]:g}  (tap to change)"

    def analyze(s):
        c = s.c
        prior = [t[1] for t in c["types"]]
        info = {}
        for a in range(2):
            mass = sum(prior[t] for t in range(2) if s.strat[t] == a)
            on = mass > 0
            b0 = prior[0] * (s.strat[0] == a) / mass if on else s.BEL[s.off]
            bel = [b0, 1 - b0]
            ev = [sum(bel[t] * c["recv"][t][r] for t in range(2)) for r in range(len(c["resp"]))]
            r = max(range(len(ev)), key=lambda k: ev[k])
            info[a] = (r, b0, on)
        dev = []
        for t in range(2):
            a = s.strat[t]
            u, u2 = c["send"][t][a][info[a][0]], c["send"][t][1 - a][info[1 - a][0]]
            if u2 > u:
                dev.append((t, u, u2))
        return info, dev

    def run(s):
        c = s.c
        task = c["tasks"][s.t]
        info, dev = s.analyze()
        lines = []
        for a in range(2):
            r, b0, on = info[a]
            lines.append(f"After '{c['acts'][a]}': belief P({c['types'][0][0]}) = {b0:.2f}{'' if on else ' (off the path)'}; receiver picks '{c['resp'][r]}'.")
        for t, u, u2 in dev:
            lines.append(f"{c['types'][t][0]} would switch to '{c['acts'][1 - s.strat[t]]}' (payoff {fmt(u2)} instead of {fmt(u)}).")
        s.rep = "\n".join(lines)
        sep = s.strat[0] != s.strat[1]
        kind = task[0]
        ok_kind = (kind == "separating" and sep) or (kind == "pooling" and not sep) or (kind == "pool0" and s.strat == [0, 0]) or (kind == "pool1" and s.strat == [1, 1])
        if dev:
            s.msg = "Not an equilibrium: someone gains by deviating. Change a strategy or the off-path belief and test again."
        elif not ok_kind:
            s.msg = "That is an equilibrium, but not the kind this task asks for. " + task[1]
        else:
            s.t += 1
            s.msg = "Equilibrium found! " + task[2]
            if s.t >= len(c["tasks"]):
                s.solved = True

    def event(s, ev):
        if s.solved:
            if s.cont.hit(ev):
                s.done = True
            return
        for i, b in enumerate(s.tb):
            if b.hit(ev):
                s.strat[i] = 1 - s.strat[i]
                s.refresh()
        if s.ob.hit(ev):
            s.off = (s.off + 1) % 3
            s.refresh()
        if s.test.hit(ev):
            s.run()

    def draw(s):
        c = s.c
        scene(c["theme"])
        panel((30, 12, 900, 616))
        text(c["title"], FB, INK, 50, 24)
        fit(c["intro"], (50, 56, 860, 50), sizes=(18, 16, 14))
        task = c["tasks"][min(s.t, len(c["tasks"]) - 1)]
        fit(f"Task {min(s.t + 1, len(c['tasks']))}/{len(c['tasks'])}: {task[1]}", (50, 106, 860, 30), col=GREEN, sizes=(19, 17, 15), bold=True)
        for i, (nm, pr) in enumerate(c["types"]):
            fit(f"Type {nm} (chance {pr:g})", (50, 148 + i * 56, 340, 36), sizes=(21, 19, 17), bold=True)
            s.tb[i].draw()
        s.ob.draw()
        s.test.draw()
        fit(s.rep, (50, 372, 860, 110), sizes=(18, 16, 14))
        fit(s.msg, (50, 488, 640, 120), col=GREEN if s.msg.startswith("Equilibrium") else RED, sizes=(19, 17, 15))
        if s.solved:
            s.cont.draw()


def _boss_extra(qi, s):
    k, c = CHARS["Captain Nash"]
    draw_char(790, 392, k, c, 4)
    pygame.draw.rect(screen, INK, (620, 150, 280, 24), 3)
    pygame.draw.rect(screen, RED, (623, 153, int(274 * max(0, s.hp) / s.n), 18))
    text(f"Captain Nash HP {max(0, s.hp)}/{s.n}", getf(14, True), INK, 620, 176)
    for i in range(s.maxh):
        pygame.draw.rect(screen, RED if i < s.hearts else GREY, (620 + i * 30, 200, 22, 22))
        pygame.draw.rect(screen, INK, (620 + i * 30, 200, 22, 22), 2)
    fit("BOSS FIGHT! Every correct answer hits Captain Nash. Every wrong answer costs you a heart. Lose all your hearts and you must start the duel over with new questions.", (60, 160, 520, 150), sizes=(24, 22, 20, 18))


class Boss(Quiz):
    def __init__(s, theme, title, pool, n=8, hearts=3):
        s.pool, s.n, s.maxh = pool, n, hearts
        Quiz.__init__(s, title, theme, random.sample(pool, n), _boss_extra)
        s.hp, s.hearts, s.lost = n, hearts, False
        s.retry = Button((330, 375, 300, 56), "Rematch!", GREENB)

    def restart(s):
        s.qs, s.qi, s.state, s.hp, s.hearts, s.lost = random.sample(s.pool, s.n), 0, "ask", s.n, s.maxh, False
        s.mk()

    def event(s, ev):
        if s.lost:
            if s.retry.hit(ev):
                s.restart()
            return
        prev = s.state
        Quiz.event(s, ev)
        if prev == "ask" and s.state == "wrong":
            s.hearts -= 1
            if s.hearts <= 0:
                s.lost = True
        if prev == "ask" and s.state == "right":
            s.hp -= 1

    def draw(s):
        Quiz.draw(s)
        if s.lost:
            panel((200, 250, 560, 200))
            text("The boss wins this round!", FB, RED, 480, 270, center=True)
            fit("You ran out of hearts. Review the lectures (links are on each level's title card) and try again with new questions.", (230, 315, 500, 56), center=True, sizes=(19, 17))
            s.retry.draw()


class TextEntry:
    """On-screen keyboard text box (works with touch). value is uppercase letters/digits (and '-' if dash)."""

    def __init__(s, theme, title, prompt, maxlen=16, dash=False, value=""):
        s.theme, s.title, s.prompt, s.maxlen, s.value, s.done, s.cancel = theme, title, prompt, maxlen, value, False, False
        s.allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" + ("-" if dash else ""))
        rows = ["1234567890", "QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM" + ("-" if dash else "")]
        s.keys = [(ch, Button((480 - len(row) * 34 + ci * 68, 240 + ri * 60, 62, 52), ch)) for ri, row in enumerate(rows) for ci, ch in enumerate(row)]
        s.bk = Button((190, 490, 200, 50), "Backspace", PURP)
        s.ok = Button((410, 490, 140, 50), "OK", GREENB)
        s.cx = Button((570, 490, 200, 50), "Cancel", (170, 50, 50))

    def finish(s):
        if s.value:
            s.done = True

    def event(s, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_BACKSPACE:
                s.value = s.value[:-1]
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                s.finish()
            elif ev.key == pygame.K_ESCAPE:
                s.cancel = True
            elif ev.unicode and ev.unicode.upper() in s.allowed and len(s.value) < s.maxlen:
                s.value += ev.unicode.upper()
        for ch, b in s.keys:
            if b.hit(ev) and len(s.value) < s.maxlen:
                s.value += ch
        if s.bk.hit(ev):
            s.value = s.value[:-1]
        if s.ok.hit(ev):
            s.finish()
        if s.cx.hit(ev):
            s.cancel = True

    def draw(s):
        scene(s.theme)
        panel((30, 12, 900, 616))
        text(s.title, FB, INK, 50, 24)
        fit(s.prompt, (50, 62, 860, 80), sizes=(21, 19, 17))
        pygame.draw.rect(screen, WHITE, (230, 150, 500, 56))
        pygame.draw.rect(screen, INK, (230, 150, 500, 56), 3)
        text(s.value + ("|" if pygame.time.get_ticks() // 500 % 2 else ""), FB, INK, 244, 164)
        for _, b in s.keys:
            b.draw()
        s.bk.draw()
        s.ok.draw()
        s.cx.draw()
