"""Facade layout traced from references/ref_main.png, in reference pixels (no bpy).

Coordinates: u to the right, v down, on the facade plane of the 1400x979 reference.
The facade is mirror-symmetric about u = AXIS; elements with mirror=True are traced on the
right half and copied. build.py turns px into metres with P["ppm"].

Depth d (metres) is toward the street from the red wall face (d = 0).
Each element: pts (outer loop), holes (loops), mat, d0, d1, bev (m).
"""
import math

AXIS = 727.0
GROUND = 882.0          # v of the pavement line at the facade
TOP = 147.0             # v of the parapet coping

# ---------------------------------------------------------------- shapes (px)


def rect(u0, v0, u1, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def cham(u0, v0, u1, v1, c, corners="tl tr br bl"):
    """Rectangle with 45-degree chamfers of c px on the named corners."""
    pts = []
    for name, (u, v), a, b in (("tl", (u0, v0), (0, c), (c, 0)), ("tr", (u1, v0), (-c, 0), (0, c)),
                               ("br", (u1, v1), (0, -c), (-c, 0)), ("bl", (u0, v1), (c, 0), (0, -c))):
        if name in corners.split():
            pts += [(u + a[0], v + a[1]), (u + b[0], v + b[1])]
        else:
            pts.append((u, v))
    return pts


def rrect(u0, v0, u1, v1, r, corners="tl tr br bl", n=8):
    """Rectangle with round corners of r px on the named corners."""
    pts = []
    spec = (("tl", u0 + r, v0 + r, 180), ("tr", u1 - r, v0 + r, 270), ("br", u1 - r, v1 - r, 0), ("bl", u0 + r, v1 - r, 90))
    for name, cu, cv, a0 in spec:
        corner = {"tl": (u0, v0), "tr": (u1, v0), "br": (u1, v1), "bl": (u0, v1)}[name]
        if name in corners.split():
            for i in range(n + 1):
                a = math.radians(a0 + 90 * i / n)
                pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
        else:
            pts.append(corner)
    return pts


def circle(cu, cv, r, n=40):
    return [(cu + r * math.cos(2 * math.pi * i / n), cv + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def area(pts):
    return 0.5 * sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))


def offset(pts, k):
    """Miter offset of a simple polygon by k px (positive grows it), whatever its winding. Orthogonal and
    45-degree shapes only need k below half the shortest edge."""
    if k == 0:
        return list(pts)
    out = _offset(pts, k, 1)
    if (abs(area(out)) > abs(area(pts))) != (k > 0):     # went the wrong way for this winding
        out = _offset(pts, k, -1)
    return out


def _offset(pts, k, s):
    out, n = [], len(pts)
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]

        def nrm(a, b):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1.0
            return (-dy / L * s, dx / L * s)
        n0, n1 = nrm(p0, p1), nrm(p1, p2)
        bx, by = n0[0] + n1[0], n0[1] + n1[1]
        bl = math.hypot(bx, by)
        if bl < 1e-6:
            out.append((p1[0] + n0[0] * k, p1[1] + n0[1] * k))
            continue
        bx, by = bx / bl, by / bl
        cosh = bx * n0[0] + by * n0[1]
        m = k / max(cosh, 0.3)
        out.append((p1[0] - bx * m, p1[1] - by * m))
    return out


def simple_polygon(pts):
    """True if no two non-adjacent edges cross (a crossing polygon fills as triangles)."""
    n = len(pts)

    def cross(a, b, c, d):
        def o(p, q, r):
            return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if cross(pts[i], pts[(i + 1) % n], pts[j], pts[(j + 1) % n]):
                return False
    return True


def mirror_pts(pts):
    return [(2 * AXIS - u, v) for u, v in reversed(pts)]


# ---------------------------------------------------------------- elements

EL = []          # every element
GLASS = []       # glazed openings: pts, d (glass plane), mullion pitch (px) u, v, mirror
DISCS = []       # porthole discs: cu, cv, r_glass, r_ring, ring mat, band depth, mirror


def add(pts, mat, d0, d1, holes=(), bev=0.015, mirror=True, name="", line=False, core=None, rank=0):
    EL.append(dict(pts=pts, holes=list(holes), mat=mat, d0=d0, d1=d1, bev=bev, mirror=mirror, name=name, line=line,
                   core=core, rank=rank))


def line(pts, inset, width, mat, d, mirror=True, name="line"):
    """A hand-painted stripe following an outline, inset px from it, on a face at depth d (a 5 mm
    paint film, so it catches no shadow of its own)."""
    add(offset(pts, -inset), mat, d, d, holes=[offset(pts, -inset - width)], bev=0.0, mirror=mirror, name=name,
        line=True)


def outlined(pts, layers, holes=(), mirror=True, name=""):
    """Stacked moulding: layers = [(grow_px, mat, d1)], outermost first. The core (last layer) sets the
    depth; build.py puts each outer layer a small step (P["layer_step"]) behind the one inside it, so the
    outline strips stay in the sun like the reference's, and the whole moulding casts the shadow."""
    core = layers[-1][2]
    n = len(layers)
    for i, (grow, mat, d1) in enumerate(layers):
        hl = [offset(h, -grow) for h in holes]
        add(offset(pts, grow) if grow else pts, mat, 0.0, d1, holes=hl, mirror=mirror, name=name, core=core,
            rank=n - 1 - i)


def glass(pts, mull_u=0, mull_v=0, d=-0.14, mirror=True, name="", frame="gold"):
    GLASS.append(dict(pts=pts, mull_u=mull_u, mull_v=mull_v, d=d, mirror=mirror, name=name, frame=frame))
    return pts


def portholes(centres, r=8.0, ring=3.0, mat="orange", d=0.16, mirror=True):
    for cu, cv in centres:
        DISCS.append(dict(cu=cu, cv=cv, r=r, ring=ring, mat=mat, d=d, mirror=mirror))


# --- window openings in the red wall (holes), right half; mirrored
OPEN = []


def opening(pts, mirror=True, **kw):
    OPEN.append(dict(pts=pts, mirror=mirror))
    glass(pts, mirror=mirror, **kw)


# floor 4 (v 185-250) and floor 3 (v 292-360): three bays each side
opening(rect(823, 186, 941, 250), mull_u=29.5, name="f4a", frame="grey")
opening(rect(969, 186, 1091, 250), mull_u=30.5, name="f4b", frame="grey")
opening(rect(1119, 186, 1146, 250), name="f4c", frame="grey")
opening([(823, 292), (941, 292), (941, 360), (871, 360), (871, 353), (858, 353), (858, 346), (845, 346), (845, 339),
         (823, 339)], mull_u=29.5, mull_v=0, name="f3a", frame="grey")
opening(rect(969, 292, 1091, 360), mull_u=30.5, name="f3b", frame="grey")
opening(rect(1119, 292, 1146, 360), name="f3c", frame="grey")
# corner tower window, octagon top
opening(cham(1174, 161, 1238, 375, 16, "tl tr"), mull_u=0, mull_v=0, name="tower", frame="grey")
# floor 2 (v 400-478)
opening(rect(978, 400, 1097, 478), mull_u=30, name="f2b", frame="grey")
opening(rect(1122, 400, 1243, 478), mull_u=30, name="f2c", frame="grey")
# floor 1 (double height hall)
opening(rrect(978, 522, 1097, 731, 22, "tr"), mull_u=30, mull_v=27, name="f1b")
opening(rect(1142, 522, 1243, 702), mull_u=33, mull_v=30, name="f1c")
opening([(860, 400), (935, 400), (935, 722), (895, 722), (880, 707), (836, 707), (836, 440), (842, 440), (842, 430),
         (848, 430), (848, 420), (854, 420), (854, 410), (860, 410)], mull_u=25.0, mull_v=18.8, name="f1step")
# central glazing behind the column and around the tower's portholes
opening(rect(657, 398, 797, 736), mull_v=0, mirror=False, name="centre")
opening(cham(668, 158, 786, 372, 18), mirror=False, name="tower_glass", frame="dark")
# ground floor clerestory strip under the first-floor band (cut in the ground-floor wall, not the red wall)
CLER = [rect(u0, 770, u1, 781) for u0, u1 in ((690, 760), (830, 905), (970, 1050), (1113, 1190), (275, 345),
                                              (405, 480), (520, 590))]
for q in CLER:
    glass(q, d=-0.08, mirror=False, name="clerestory", frame="dark")

# --- mouldings (right half, mirrored)
CREAM, ORANGE, YELLOW, RED, WHITE = "cream", "orange", "yellow", "red", "white"

# big inverted-L arch band with portholes (horizontal v 362-392, vertical u 800-830)
arch = [(800, 400), (812, 372), (830, 362), (1152, 362), (1152, 392), (848, 392), (835, 397), (830, 410), (830, 742),
        (800, 742)]
outlined(arch, [(4, YELLOW, 0.10), (2, ORANGE, 0.13), (0, CREAM, 0.16)], name="arch_main")
line(arch, 4, 1.6, ORANGE, 0.16, name="arch_line")
portholes([(850 + 38.6 * i, 377) for i in range(8)])
portholes([(815, 412 + 36.8 * i) for i in range(9)])
# right arch (vertical u 1105-1140, horizontal v 480-520), big outer curve
arch_r = [(1105, 742), (1105, 548)] + [(1105 + 40 - 40 * math.cos(math.radians(a)), 548 - 60 * math.sin(math.radians(a)))
                                       for a in range(15, 90, 15)] + \
         [(1145, 488), (1150, 480), (1262, 480), (1262, 520), (1175, 520)] + \
         [(1140 + 35 - 35 * math.sin(math.radians(a)), 520 + 35 - 35 * math.cos(math.radians(a))) for a in range(15, 90, 15)] + \
         [(1140, 560), (1140, 742)]
outlined(arch_r, [(4, YELLOW, 0.10), (2, ORANGE, 0.13), (0, CREAM, 0.16)], name="arch_right")
line(arch_r, 4, 1.6, ORANGE, 0.16, name="arch_r_line")
portholes([(1133, 520), (1168, 501), (1203, 493), (1238, 493)])
# orange pier with square windows
sq = [rect(945, cv - 9, 967, cv + 9) for cv in (422, 462, 504, 545, 586, 629, 670)]
outlined(rect(938, 398, 976, 748), [(3, CREAM, 0.08), (0, ORANGE, 0.12)], holes=sq, name="pier_sq")
for h in sq:
    add(offset(h, 3), CREAM, 0.0, 0.14, holes=[h], name="pier_sq_frame")
for h in sq:
    glass(h, d=0.04, name="pier_win", frame="cream")
# central column (orange frame, cream lining, dark slot)
col = cham(680, 380, 775, 736, 14, "tl tr")
slot = cham(701, 390, 753, 726, 10, "tl tr")
outlined(col, [(3, CREAM, 0.10), (0, ORANGE, 0.14)], holes=[offset(slot, 4)], mirror=False, name="column")
line(col, 3, 1.4, CREAM, 0.14, mirror=False, name="column_line")
add(offset(slot, 4), CREAM, 0.0, 0.10, holes=[slot], mirror=False, name="column_lining")
glass(slot, mull_u=8.7, d=0.02, mirror=False, name="slot")

# central tower (Granser close-up): narrow yellow octagon frame with cream lips round dark glass,
# a cream crest box holding two small windows, rings of yellow with two painted orange lines
TG = cham(668, 158, 786, 372, 18)
tower = cham(652, 145, 802, 388, 26)
outlined(tower, [(3, CREAM, 0.10), (0, YELLOW, 0.15)], holes=[offset(TG, 4)], mirror=False, name="tower")
add(offset(TG, 4), CREAM, 0.0, 0.12, holes=[TG], mirror=False, name="tower_lip")
line(tower, 5, 1.4, ORANGE, 0.15, mirror=False, name="tower_line")
CB = rect(684, 112, 770, 147)
CW = [rect(690, 119, 721, 142), rect(733, 119, 764, 142)]
outlined(CB, [(2.5, YELLOW, 0.10), (0, CREAM, 0.13)], holes=CW, mirror=False, name="crest_box")
for q in CW:
    glass(q, d=0.12, mirror=False, name="crest_win")
for cv in (210, 322):
    add(circle(727, cv, 46), YELLOW, 0.0, 0.22, holes=[circle(727, cv, 37)], mirror=False, name="ring")
    add(circle(727, cv, 37), CREAM, 0.0, 0.25, holes=[circle(727, cv, 33.5)], mirror=False, name="ring_in")
    add(circle(727, cv, 48.5), CREAM, 0.0, 0.19, holes=[circle(727, cv, 45)], mirror=False, name="ring_out")
    for rr in (40.0, 43.0):
        add(circle(727, cv, rr + 0.7), ORANGE, 0.22, 0.22, holes=[circle(727, cv, rr - 0.7)], bev=0.0, mirror=False,
            name="ring_line", line=True)
add(rect(722, 255, 732, 278), YELLOW, 0.0, 0.2, mirror=False, name="ring_link")
add(rect(722, 87, 732, 112), YELLOW, 0.0, 0.18, mirror=False, name="finial")
add(rect(722, 119, 733, 147), YELLOW, 0.0, 0.16, mirror=False, name="crest_mullion")
add(rect(712, 97, 742, 103), YELLOW, 0.0, 0.18, mirror=False, name="finial_bar")
# stepped orange crest behind the tower top
crest = [(672, 97), (782, 97), (782, 110), (800, 110), (800, 124), (815, 124), (815, 137), (832, 137), (832, 152),
         (622, 152), (622, 137), (639, 137), (639, 124), (654, 124), (654, 110), (672, 110)]
add(crest, ORANGE, -0.05, 0.06, mirror=False, name="crest")

# corner towers (yellow frame round the tall window) with base band
ctower = rect(1143, 148, 1262, 395)
TWIN = cham(1174, 161, 1238, 375, 16, "tl tr")
add(ctower, CREAM, 0.0, 0.08, holes=[offset(TWIN, 7)], name="ctower")
add(offset(TWIN, 19), YELLOW, 0.0, 0.14, holes=[offset(TWIN, 7)], name="ctower_yellow")
add(offset(TWIN, 7), CREAM, 0.0, 0.11, holes=[offset(TWIN, 3)], name="ctower_lip")
add(offset(TWIN, 3), "dark", 0.0, 0.07, holes=[TWIN], name="ctower_liner")
add(rect(1140, 378, 1265, 398), RED, 0.0, 0.2, name="ctower_base")
add(rect(1140, 385, 1265, 392), YELLOW, 0.0, 0.22, name="ctower_base_line")

# roof caps: slab on a short post (proud), traced on the right
for u0, u1, p0, p1 in ((925, 980, 938, 967), (1085, 1135, 1098, 1122), (1136, 1268, 1180, 1225)):
    add(rect(p0, 138, p1, 150), RED, -0.3, 0.1, name="cap_post")
    add([(u0, 124), (u1, 124), (u1 - 4, 140), (u0 + 4, 140)], YELLOW, -0.6, 0.35, bev=0.02, name="cap")
    add([(u0 + 2, 132), (u1 - 2, 132), (u1 - 5, 140), (u0 + 5, 140)], ORANGE, -0.6, 0.37, bev=0.01, name="cap_edge")

# parapet and floor bands (right of the tower)
add(rect(802, 145, 1143, 150), YELLOW, 0.0, 0.12, name="coping")
outlined(rect(802, 173, 1143, 180), [(1.5, CREAM, 0.04), (0, YELLOW, 0.06)], name="band_172")
outlined(rect(815, 247, 1146, 255), [(1.5, CREAM, 0.05), (0, YELLOW, 0.08)], name="sill_f4")
outlined(rect(815, 284, 1146, 291), [(1.5, CREAM, 0.04), (0, YELLOW, 0.06)], name="band_283")
outlined(rect(963, 475, 1103, 485), [(1.5, CREAM, 0.05), (0, YELLOW, 0.08)], name="sill_f2")
# pier edge lines between bays
for u in (942, 968, 1091, 1119):
    add(rect(u - 2, 186, u + 2, 360), CREAM, 0.0, 0.03, name="pier_line")
# first-floor band (v 725-768): cream/yellow ledge over a red fascia
fascia = [(657, 736), (800, 736), (800, 742), (905, 742), (920, 725), (1105, 725), (1105, 742), (1262, 742),
          (1262, 768), (657, 768)]
add(fascia, RED, 0.0, 0.22, bev=0.015, name="fascia")
ledge = [(657, 736), (800, 736), (800, 742), (905, 742), (920, 725), (1105, 725), (1105, 742), (1262, 742),
         (1262, 750), (1100, 750), (1100, 733), (924, 733), (909, 750), (657, 750)]
add(ledge, YELLOW, 0.0, 0.26, bev=0.012, name="ledge")
add(rect(657, 750, 800, 756), CREAM, 0.0, 0.24, name="ledge_c")
# right edge pier
add(rect(1243, 398, 1263, 742), RED, 0.0, 0.1, name="edge_pier")

# --- ground floor (not symmetric)
SHUTTERS = [(275, 336), (405, 466), (518, 580), (689, 751), (830, 891), (972, 1036)]
SHOP = (1113, 1190)
DOOR = (604, 646)
GF_TOP = 769.0          # v of the ground-floor wall top (under the first-floor fascia)
GF_OPEN_TOP = 792.0     # v of the shutter and door heads


def ground_floor():
    """Holes in the ground-floor wall: openings (to 1 px above its bottom edge) and the clerestory.
    A hole that touches or crosses its outline breaks the curve fill."""
    return [rect(u0, GF_OPEN_TOP, u1, GROUND + 1) for u0, u1 in SHUTTERS + [SHOP, DOOR]] + CLER


def between(u_lo, u_hi, v0, v1):
    """Rectangles of the band v0..v1 between the ground-floor openings."""
    cuts = sorted(SHUTTERS + [SHOP, DOOR])
    out, u = [], u_lo
    for a, b in cuts:
        if a > u:
            out.append(rect(u, v0, a, v1))
        u = max(u, b)
    if u < u_hi:
        out.append(rect(u, v0, u_hi, v1))
    return out
