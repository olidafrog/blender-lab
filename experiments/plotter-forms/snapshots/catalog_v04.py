"""plotter-forms: the catalogue. Each entry is one plot: a form (a Geometry Nodes group made by
plot_kit from formulas), its tunable values, a camera and plot options.

Entry keys: name, family, title, make(values) -> T, values (the tunables that go into P as
"<name>.<key>"; angles in degrees are listed in `angles`), cam (azimuth, elevation in degrees),
plot (plot_svg options for this plot), frame (world half-width of the page; None: fit),
sheet ([overrides per copy], columns) for several copies in one plot.
"""
import math

import plot_kit as pk


def P_(name, key, default, lo, hi, tip=None, kind="f"):
    return dict(name=name, key=key, default=default, lo=lo, hi=hi, tip=tip, kind=kind)


def ang(name, key, lo=-360.0, hi=360.0, tip=None):
    return dict(name=name, key=key, default=0.0, lo=math.radians(lo), hi=math.radians(hi), tip=tip, kind="angle")


FORMS = []


def add(name, family, title, make, values=None, angles=(), cam=(30, 25), plot=None, frame=None, sheet=None,
        persp=None):
    FORMS.append(dict(name=name, family=family, title=title, make=make, values=values or {}, angles=angles,
                      cam=cam, plot=plot or {}, frame=frame, sheet=sheet, persp=persp))


# ---------------------------------------------------------------------------------------------- Hopf
HOPF_PARAMS = [
    P_("Rings", "rings", 3, 1, 12, "Circles of latitude on the base sphere: each gives one torus", "i"),
    P_("Fibres", "fibres", 24, 1, 200, "Circles per ring", "i"),
    ang("Latitude From", "lat0", 1, 179, "First ring, as an angle from the top of the base sphere"),
    ang("Latitude To", "lat1", 1, 179, "Last ring. Near 180 the circles grow without limit"),
    P_("Arc", "arc", 1.0, 0.0, 4.0, "Share of the way round each ring that carries fibres. Under 1: open tori"),
    P_("Stagger", "stagger", 0.0, -1.0, 1.0, "Turns each ring's arc against the last"),
    P_("Spiral", "spiral", 0.0, 0.0, 12.0, "Slides the fibres across latitude as they go round: a spiral on the base sphere"),
    ang("Tumble", "tumble", -180, 180, "Rotates the 4D sphere before projection: the tori swell and pass through infinity"),
]
HOPF_LET = [
    ("j", "floor(i / fibres)"), ("k", "mod(i, fibres)"),
    ("th", "lat0 + (lat1 - lat0) * (j + 0.5 + spiral * (k / fibres - 0.5)) / rings"),
    ("ph", "tau * (arc * k / fibres + stagger * j)"),
    ("c", "cos(th)"), ("A", "sqrt((1 + c) / 2)"), ("Bq", "sqrt(max(1 - c, 0) / 2)"), ("w", "tau * t"),
    ("x1", "A * cos(w)"), ("x2", "A * sin(w)"), ("x3", "Bq * cos(w - ph)"), ("x4", "Bq * sin(w - ph)"),
    ("y1", "x1 * cos(tumble) - x4 * sin(tumble)"), ("y4", "x1 * sin(tumble) + x4 * cos(tumble)"),
    ("d", "max(1 - y4, 0.002)"),
]


def hopf(name):
    return lambda v: pk.curve_family(name, "y1 / d", "x2 / d", "x3 / d", "rings * fibres", HOPF_PARAMS,
                                     points=160, values=v, let=HOPF_LET)


HS_PARAMS = [
    ang("Latitude", "lat", 1, 179, "Which circle of the base sphere: each latitude gives one torus. Near 180 it grows without limit"),
    P_("Arc", "arc", 1.0, 0.02, 4.0, "Share of the way round that the torus covers. Under 1: an open torus you can see into"),
    P_("Start", "start", 0.0, -1.0, 1.0, "Turns the open part round"),
    ang("Spiral", "spiral", -179, 179, "Changes the latitude along the arc: the torus becomes a spiral band"),
    ang("Tumble", "tumble", -180, 180, "Rotates the 4D sphere before projection: the torus swells and passes through infinity"),
]
HS_LET = [
    ("th", "lat + spiral * (u01 - 0.5)"), ("ph", "tau * (start + arc * u01)"), ("w", "tau * v01"),
    ("c", "cos(th)"), ("A", "sqrt((1 + c) / 2)"), ("Bq", "sqrt(max(1 - c, 0) / 2)"),
    ("x1", "A * cos(w)"), ("x2", "A * sin(w)"), ("x3", "Bq * cos(w - ph)"), ("x4", "Bq * sin(w - ph)"),
    ("y1", "x1 * cos(tumble) - x4 * sin(tumble)"), ("y4", "x1 * sin(tumble) + x4 * cos(tumble)"),
    ("d", "max(1 - y4, 0.002)"),
]


def hopf_surface(name, res=(200, 160)):
    """One Hopf torus as an opaque surface: its u-lines are the fibres (linked circles)."""
    return lambda v: pk.surface(name, "y1 / d", "x2 / d", "x3 / d", params=HS_PARAMS, u_lines=("Fibres", 30),
                                v_lines=("Rings", 0), closed=(False, True), edges=(True, False), values=v,
                                res=res, let=HS_LET)


H = dict(rings=3, fibres=24, lat0=35.0, lat1=125.0, arc=1.0, stagger=0.0, spiral=0.0, tumble=0.0)
HA = ("lat0", "lat1", "tumble")
S = dict(lat=75.0, arc=1.0, start=0.0, spiral=0.0, tumble=0.0, u_lines=30, v_lines=0)
SA = ("lat", "spiral", "tumble")
add("hopf-links", "hopf", "Hopf: a few linked circles, see-through", hopf("Hopf Links"),
    {**H, "rings": 1, "fibres": 12, "lat0": 80.0, "lat1": 80.0}, HA, cam=(20, 40), plot={"weave": 1.6})
add("hopf-torus", "hopf", "Hopf: one torus of linked circles", hopf_surface("Hopf Torus"),
    {**S, "lat": 78.0, "u_lines": 40}, SA, cam=(20, 34))
add("hopf-nested", "hopf", "Hopf: nested open tori", hopf_surface("Hopf Nested"),
    {**S, "lat": 60.0, "arc": 0.62, "u_lines": 22}, SA, cam=(20, 32),
    sheet=([{"lat": 62.0, "arc": 0.85, "u_lines": 26}, {"lat": 90.0, "arc": 0.66, "u_lines": 22},
            {"lat": 116.0, "arc": 0.46, "u_lines": 18}], 0))
add("hopf-onion", "hopf", "Hopf: four tori cut in half", hopf_surface("Hopf Onion"),
    {**S, "lat": 60.0, "arc": 0.5, "u_lines": 18}, SA, cam=(90, 35),
    sheet=([{"lat": 66.0, "u_lines": 12}, {"lat": 88.0, "u_lines": 14}, {"lat": 108.0, "u_lines": 16}, {"lat": 126.0}], 0))
add("hopf-spiral", "hopf", "Hopf: fibres over a spiral", hopf_surface("Hopf Spiral", res=(360, 160)),
    {**S, "lat": 85.0, "arc": 2.0, "spiral": 90.0, "u_lines": 64}, SA, cam=(25, 30))
add("hopf-meridian", "hopf", "Hopf: fibres over a meridian, see-through", hopf("Hopf Meridian"),
    {**H, "rings": 1, "fibres": 12, "lat0": 55.0, "lat1": 150.0, "arc": 0.0, "spiral": 1.0, "points": 480}, HA, cam=(35, 22), plot={"weave": 1.6})
add("hopf-tumble", "hopf", "Hopf: tumbled in 4D, see-through", hopf("Hopf Tumble"),
    {**H, "rings": 2, "fibres": 16, "lat0": 50.0, "lat1": 115.0, "tumble": 38.0, "points": 700}, HA, cam=(20, 28),
    frame=3.4, plot={"clip": 1, "weave": 1.4})

# ------------------------------------------------------------------------------------- sphere fields
def q(a, b, c):
    """Potential of a unit charge at (a, b, c)."""
    return f"1/sqrt((x - {a})**2 + (y - {b})**2 + (z - {c})**2 + soft)"


SPH = {"outline": 1, "graze": 0.34, "min_length": 4.0}
add("harmonic-tesseral", "sphere", "Spherical harmonic L5 M3", lambda v: pk.sphere_field(
    "Harmonic Tesseral", "harmonic(L, M)", [P_("Degree L", "L", 5, 0, 12, "Total nodal lines", "i"),
                                             P_("Order M", "M", 3, -12, 12, "Nodal lines through the poles", "i")], values=v),
    dict(lines=10, L=5, M=3), cam=(0, 28), plot=SPH)
add("harmonic-sectoral", "sphere", "Spherical harmonic L4 M4", lambda v: pk.sphere_field(
    "Harmonic Sectoral", "harmonic(L, M)", [P_("Degree L", "L", 4, 0, 12, None, "i"), P_("Order M", "M", 4, -12, 12, None, "i")],
    values=v), dict(lines=10, L=4, M=4), cam=(0, 38), plot=SPH)
add("harmonic-fine", "sphere", "Spherical harmonic L9 M5", lambda v: pk.sphere_field(
    "Harmonic Fine", "harmonic(L, M)", [P_("Degree L", "L", 9, 0, 12, None, "i"), P_("Order M", "M", 5, -12, 12, None, "i")],
    values=v), dict(lines=6, L=9, M=5), cam=(0, 24), plot=SPH)
HARM = [P_("Degree L", "L", 5, 0, 12, "Total nodal lines", "i"), P_("Order M", "M", 3, -12, 12, "Nodal lines through the poles", "i")]
LOBE = {"outline": 1, "min_length": 3.0}
add("harmonic-lobes", "sphere", "Harmonic L3 M2 as lobes", lambda v: pk.sphere_field(
    "Harmonic Lobes", "harmonic(L, M)", HARM, values=v, relief=True),
    dict(lines=22, L=3, M=2, relief=0.75), cam=(25, 28), plot=LOBE)
add("harmonic-relief", "sphere", "Harmonic L6 M4 in relief", lambda v: pk.sphere_field(
    "Harmonic Relief", "harmonic(L, M)", HARM, values=v, relief=True),
    dict(lines=22, L=6, M=4, relief=0.3), cam=(20, 32), plot=LOBE)
add("harmonic-pair", "sphere", "Two harmonics mixed", lambda v: pk.sphere_field(
    "Harmonic Pair", "harmonic(L, M) + blend * harmonic(L2, M2, tilt, 0)",
    [P_("Degree L", "L", 6, 0, 12, None, "i"), P_("Order M", "M", 3, -12, 12, None, "i"),
     P_("Second L", "L2", 4, 0, 12, None, "i"), P_("Second M", "M2", 2, -12, 12, None, "i"),
     P_("Blend", "blend", 0.8, 0.0, 2.0, "Strength of the second harmonic"),
     ang("Second Tilt", "tilt", -180, 180, "Tips the second harmonic's pole")], values=v),
    dict(lines=12, L=6, M=3, L2=4, M2=2, blend=0.8, tilt=50.0), ("tilt",), cam=(0, 20), plot=SPH)
add("sphere-charges", "sphere", "Potential of point charges", lambda v: pk.sphere_field(
    "Sphere Charges",
    f"{q(0.55, -0.75, 0.36)} + {q(-0.6, -0.62, -0.5)} + {q(0.1, 0.3, 0.95)}"
    f" - balance*({q(-0.35, -0.85, 0.4)} + {q(0.7, -0.5, -0.5)} + {q(-0.2, 0.9, -0.4)})",
    [P_("Softness", "soft", 0.12, 0.01, 1.0, "Rounds the peak at each charge"),
     P_("Balance", "balance", 1.0, 0.0, 2.0, "Strength of the negative charges")], values=v),
    dict(lines=22, soft=0.12, balance=1.0), cam=(0, 0), plot=SPH)
add("sphere-noise", "sphere", "Noise: a contour-map planet", lambda v: pk.sphere_field(
    "Sphere Noise", "noise(x*scale + seed, y*scale, z*scale, rough)",
    [P_("Scale", "scale", 1.5, 0.1, 10.0), P_("Roughness", "rough", 1.0, 0.0, 6.0), P_("Seed", "seed", 3.0, 0.0, 100.0)],
    values=v), dict(lines=22, scale=1.5, rough=1.0, seed=3.0), cam=(0, 0), plot=SPH)
add("sphere-ripples", "sphere", "Two ripple sources interfering", lambda v: pk.sphere_field(
    "Sphere Ripples", "cos(waves*acos(clamp(x*0.5 - y*0.75 + z*0.433, -1, 1))) + cos(waves*acos(clamp(-x*0.6 - y*0.7 - z*0.39, -1, 1)))",
    [P_("Waves", "waves", 16.0, 1.0, 60.0, "Ripples from each source to its far side")], values=v),
    dict(lines=4, waves=14.0), cam=(0, 0), plot=SPH)
add("sphere-waves", "sphere", "Wavy latitude bands", lambda v: pk.sphere_field(
    "Sphere Waves", "z + amp * sin(lobes*lon + twist*z) * (1 - z*z)",
    [P_("Lobes", "lobes", 6, 0, 30, None, "i"), P_("Amplitude", "amp", 0.22, 0.0, 1.0),
     P_("Twist", "twist", 0.0, -12.0, 12.0, "Shears the waves from pole to pole")], values=v),
    dict(lines=22, lobes=6, amp=0.22, twist=3.0), cam=(0, 38), plot={"outline": 1})
add("sphere-spiral", "sphere", "Barber-pole stripes", lambda v: pk.sphere_field(
    "Sphere Spiral", "sin(arms*lon + turns*lat)",
    [P_("Arms", "arms", 5, 1, 30, None, "i"), P_("Turns", "turns", 7.0, -30.0, 30.0),
     P_("Pole Cap", "cap", 0.93, 0.5, 1.0, "The stripes stop this far towards the poles, where they would all meet")],
    values=v, keep="abs(z) < cap"), dict(lines=1, arms=12, turns=6.0, cap=0.95), cam=(0, 40), plot={"outline": 1})
DIPOLE_LET = [("j", "floor(i / planes)"), ("k", "mod(i, planes)"),
              ("L", "1 / (1/reach + (1/1.25 - 1/reach) * (j + 0.5) / shells)"),
              ("th0", "asin(sqrt(1 / L))"), ("th", "th0 + t * (pi - 2*th0)"), ("r", "L * sin(th)**2"),
              ("ph", "tau * k / planes")]
add("dipole", "sphere", "Magnet field lines round a sphere", lambda v: pk.curve_family(
    "Dipole", "r*sin(th)*cos(ph)", "r*sin(th)*sin(ph)", "r*cos(th)", "shells * planes",
    [P_("Shells", "shells", 5, 1, 30, "Field lines per plane, spaced by equal flux", "i"),
     P_("Planes", "planes", 12, 1, 60, "Planes round the axis", "i"),
     P_("Reach", "reach", 4.0, 1.3, 12.0, "How far the widest line goes, in sphere radii")],
    points=120, cyclic=False, values=v, occluder=1.0, let=DIPOLE_LET),
    dict(shells=5, planes=10, reach=3.2), cam=(36, 16), plot=SPH)

# ------------------------------------------------------------------------------------- sliced solids
TORUS = pk.param_mesh("(1 + 0.42*cos(v))*cos(u)", "(1 + 0.42*cos(v))*sin(u)", "0.42*sin(v)", (0, math.tau), (0, math.tau))
SOL = {"outline": 1}
TILT = [ang("Slice Tilt", "tilt", -180, 180, "Tips the cutting planes")]
add("torus-slices", "sliced", "Torus cut by tilted planes", lambda v: pk.solid(
    "Torus Slices", TORUS, [("Slices", "slices", "z*cos(tilt) + x*sin(tilt)", 26)], TILT, v),
    dict(slices=26, tilt=40.0), ("tilt",), cam=(25, 35), plot=SOL)
add("torus-shells", "sliced", "Torus cut by spheres round a point", lambda v: pk.solid(
    "Torus Shells", TORUS, [("Shells", "shells", "sqrt((x - px)**2 + (y + 0.9)**2 + (z - 0.5)**2)", 30)],
    [P_("Centre X", "px", 0.9, -3.0, 3.0, "Where the shells start from")], v),
    dict(shells=30, px=0.9), cam=(25, 35), plot=SOL)
add("torus-waffle", "sliced", "Torus cut two ways", lambda v: pk.solid(
    "Torus Waffle", TORUS, [("Slices X", "slices_x", "x + 0.3*z", 18), ("Slices Y", "slices_y", "y - 0.3*z", 18)], (), v),
    dict(slices_x=18, slices_y=18), cam=(25, 40), plot=SOL)
BLOB = "+".join(f"exp(-((x-{a})**2 + (y-{b})**2 + (z-{c})**2) / ({s}*size)**2)"
                for a, b, c, s in ((0.0, 0.0, 0.0, 0.55), (0.62, 0.1, 0.38, 0.4), (-0.5, 0.25, -0.35, 0.42),
                                   (0.1, -0.5, 0.6, 0.33), (0.3, 0.45, -0.55, 0.36)))
add("blobs", "sliced", "Metaballs as a stack of slices", lambda v: pk.solid(
    "Blobs", pk.implicit_mesh(BLOB + " - 0.45", bounds=1.5, res=110), [("Slices", "slices", "z*cos(tilt) + x*sin(tilt)", 34)],
    [P_("Size", "size", 1.0, 0.5, 1.5, "Size of every blob: they merge as it grows")] + TILT, v),
    dict(slices=34, size=1.0, tilt=0.0), ("tilt",), cam=(30, 28), plot=SOL)
GYR = "sin(k*x)*cos(k*y) + sin(k*y)*cos(k*z) + sin(k*z)*cos(k*x)"
add("gyroid-ball", "sliced", "Gyroid sheet inside a ball", lambda v: pk.solid(
    "Gyroid Ball", pk.implicit_mesh(f"smin(wall - abs({GYR}), 1 - (x*x + y*y + z*z), 9)", bounds=1.15, res=160),
    [("Slices", "slices", "z", 30)],
    [P_("Cells", "k", 3.6, 1.0, 12.0, "Size of the gyroid pattern: higher is finer"),
     P_("Wall", "wall", 0.42, 0.05, 1.4, "Thickness of the sheet")], v),
    dict(slices=30, k=3.6, wall=0.42), cam=(30, 28), plot=SOL)
add("schwarz-cube", "sliced", "Schwarz P sheet in a block", lambda v: pk.solid(
    "Schwarz Cube", pk.implicit_mesh("smin(wall - abs(cos(k*x) + cos(k*y) + cos(k*z)), 1 - (x**8 + y**8 + z**8), 9)", bounds=1.15, res=160),
    [("Slices", "slices", "z", 30)],
    [P_("Cells", "k", 4.712, 1.0, 12.0), P_("Wall", "wall", 0.45, 0.05, 1.4)], v),
    dict(slices=30, k=4.712, wall=0.5), cam=(28, 30), plot=SOL)
KNOT_LET = [("a", "tau * s"), ("rr", "2 + cos(q*a)")]
add("knot-slices", "sliced", "Trefoil tube in slices", lambda v: pk.solid(
    "Knot Slices", pk.tube_mesh("rr*cos(p*a)", "rr*sin(p*a)", "-1.2*sin(q*a)", "radius", let=KNOT_LET),
    [("Slices", "slices", "z*cos(tilt) + y*sin(tilt)", 40)],
    [P_("P", "p", 2, 1, 9, "Times round the long way", "i"), P_("Q", "q", 3, 1, 9, "Times through the hole", "i"),
     P_("Radius", "radius", 0.5, 0.05, 1.0, "Tube radius")] + TILT, v),
    dict(slices=40, p=2, q=3, radius=0.5, tilt=65.0), ("tilt",), cam=(0, 55), plot=SOL)
add("monkey-slices", "sliced", "Any mesh: Suzanne in slices", lambda v: pk.solid(
    "Monkey Slices", pk.object_mesh(), [("Slices", "slices", "z*cos(tilt) - y*sin(tilt)", 36)], TILT, v),
    dict(slices=36, tilt=25.0), ("tilt",), cam=(-25, 12), plot=SOL)

# ------------------------------------------------------------------- minimal and classic surfaces
ASSOC = dict(x="sin(a)*cosh(v)*cos(u) + cos(a)*sinh(v)*sin(u)", y="sin(a)*cosh(v)*sin(u) - cos(a)*sinh(v)*cos(u)",
             z="v*sin(a) + u*cos(a)")
MORPH = [ang("Morph", "a", 0, 90, "0: helicoid. 90: catenoid. Every step between is also a minimal surface"),
         P_("Turns", "turns", 1.0, 0.25, 4.0, "Length along the axis, in turns"),
         P_("Width", "width", 1.2, 0.2, 2.5)]
add("helicoid-catenoid", "minimal", "Helicoid bending into a catenoid", lambda v: pk.surface(
    "Helicoid to Catenoid", **ASSOC, u=("-pi*turns", "pi*turns"), v=("-width", "width"), params=MORPH,
    u_lines=("Rulings", 20), v_lines=("Spirals", 8), values=v),
    dict(a=0.0, turns=1.0, width=1.2, u_lines=20, v_lines=8), ("a",), cam=(25, 22),
    sheet=([{"a": d} for d in (0.0, 18.0, 36.0, 54.0, 72.0, 90.0)], 3))
add("helicoid", "minimal", "Helicoid: a spiral ramp", lambda v: pk.surface(
    "Helicoid", **ASSOC, u=("-pi*turns", "pi*turns"), v=("-width", "width"), params=MORPH,
    u_lines=("Rulings", 48), v_lines=("Spirals", 6), values=v),
    dict(a=0.0, turns=1.5, width=1.7, u_lines=42, v_lines=7), ("a",), cam=(30, 24))
ENN = dict(x="v*cos(u) - v**(2*n+1)/(2*n+1)*cos((2*n+1)*u)", y="-v*sin(u) - v**(2*n+1)/(2*n+1)*sin((2*n+1)*u)",
           z="2*v**(n+1)/(n+1)*cos((n+1)*u)")
ENN_P = [P_("Order", "n", 1, 1, 6, "Number of saddle folds, less one", "i"), P_("Reach", "rmax", 1.5, 0.3, 2.2, "How far out the disc goes; past about 1.7 (order 1) it passes through itself")]


def enneper(name):
    return lambda v: pk.surface(name, **ENN, u=(0, math.tau), v=(0.0, "rmax"), params=ENN_P,
                                u_lines=("Spokes", 28), v_lines=("Rings", 9), closed=(True, False),
                                edges=(False, "hi"), values=v, res=(240, 90), pole=True)


add("enneper", "minimal", "Enneper surface", enneper("Enneper"), dict(n=1, rmax=1.6, u_lines=32, v_lines=9), cam=(30, 30))
add("enneper-3", "minimal", "Enneper surface, order 3", enneper("Enneper 3"), dict(n=3, rmax=1.12, u_lines=40, v_lines=8), cam=(20, 35))
add("scherk", "minimal", "Scherk's surface, one cell", lambda v: pk.surface(
    "Scherk", "u", "v", "log(cos(v) / cos(u))", u=("-reach", "reach"), v=("-reach", "reach"),
    params=[P_("Reach", "reach", 1.42, 0.5, 1.52, "How near the edge of the cell (pi/2) the patch goes: the wings grow without limit")],
    u_lines=("Lines U", 18), v_lines=("Lines V", 18), values=v),
    dict(reach=1.3, u_lines=16, v_lines=16), cam=(38, 22))
add("henneberg", "minimal", "Henneberg surface", lambda v: pk.surface(
    "Henneberg", "2*sinh(v)*cos(u) - 2/3*sinh(3*v)*cos(3*u)", "2*sinh(v)*sin(u) + 2/3*sinh(3*v)*sin(3*u)",
    "2*cosh(2*v)*cos(2*u)", u=(0, math.tau), v=(0.0, "reach"),
    params=[P_("Reach", "reach", 0.6, 0.1, 1.0)], u_lines=("Spokes", 32), v_lines=("Rings", 8),
    closed=(True, False), edges=(False, "hi"), values=v, res=(260, 80)),
    dict(reach=0.6, u_lines=32, v_lines=8), cam=(25, 30))
add("catalan", "minimal", "Catalan surface", lambda v: pk.surface(
    "Catalan", "u - sin(u)*cosh(v)", "1 - cos(u)*cosh(v)", "4*sin(u/2)*sinh(v/2)", u=("-pi*arches", "pi*arches"),
    v=("-width", "width"), params=[P_("Arches", "arches", 2.0, 0.5, 4.0), P_("Width", "width", 1.3, 0.2, 2.2)],
    u_lines=("Lines U", 36), v_lines=("Lines V", 9), values=v, res=(260, 90)),
    dict(arches=2.0, width=1.3, u_lines=36, v_lines=9), cam=(20, 30))
RICH_LET = [("U", "v*cos(u)"), ("W", "v*sin(u)"), ("q", "U*U + W*W")]
add("richmond", "minimal", "Richmond surface", lambda v: pk.surface(
    "Richmond", "U**3/3 - U*W*W + U/q", "-U*U*W + W**3/3 - W/q", "2*U", u=(0, math.tau), v=("inner", "outer"),
    params=[P_("Inner", "inner", 0.42, 0.2, 0.9, "Size of the hole round the pole"), P_("Outer", "outer", 1.3, 1.0, 1.8)],
    u_lines=("Spokes", 36), v_lines=("Rings", 9), closed=(True, False), edges=(False, True), values=v,
    res=(260, 90), let=RICH_LET), dict(inner=0.42, outer=1.3, u_lines=36, v_lines=9), cam=(20, 30))
add("dini", "minimal", "Dini's surface", lambda v: pk.surface(
    "Dini", "cos(u)*sin(v)", "sin(u)*sin(v)", "cos(v) + log(tan(v/2)) + pitch*u", u=(0, "tau*turns"), v=(0.06, 1.9),
    params=[P_("Turns", "turns", 2.0, 0.5, 5.0), P_("Pitch", "pitch", 0.2, 0.0, 0.6, "Rise per radian: 0 is the pseudosphere")],
    u_lines=("Rulings", 40), v_lines=("Spirals", 8), values=v, res=(300, 90)),
    dict(turns=2.0, pitch=0.2, u_lines=40, v_lines=8), cam=(25, 18))
KUEN_LET = [("dd", "1 + u*u*sin(v)**2")]
add("kuen", "minimal", "Kuen's surface", lambda v: pk.surface(
    "Kuen", "2*(cos(u) + u*sin(u))*sin(v)/dd", "2*(sin(u) - u*cos(u))*sin(v)/dd", "log(tan(v/2)) + 2*cos(v)/dd",
    u=("-reach", "reach"), v=(0.06, math.pi - 0.06), params=[P_("Reach", "reach", 4.5, 1.0, 8.0)],
    u_lines=("Lines U", 36), v_lines=("Lines V", 16), values=v, res=(300, 140), let=KUEN_LET),
    dict(reach=4.5, u_lines=36, v_lines=16), cam=(35, 25))
add("klein-bottle", "minimal", "Klein bottle", lambda v: pk.surface(
    "Klein Bottle",
    "-(2/15)*cos(u)*(3*cos(v) - 30*sin(u) + 90*cos(u)**4*sin(u) - 60*cos(u)**6*sin(u) + 5*cos(u)*cos(v)*sin(u))",
    "(2/15)*(3 + 5*cos(u)*sin(u))*sin(v)",
    "(1/15)*sin(u)*(3*cos(v) - 3*cos(u)**2*cos(v) - 48*cos(u)**4*cos(v) + 48*cos(u)**6*cos(v) - 60*sin(u) + 5*cos(u)*cos(v)*sin(u)"
    " - 5*cos(u)**3*cos(v)*sin(u) - 80*cos(u)**5*cos(v)*sin(u) + 80*cos(u)**7*cos(v)*sin(u))",
    u=(0, math.pi), v=(0, math.tau), u_lines=("Rings", 40), v_lines=("Bands", 14), closed=(False, True),
    edges=(False, False), values=v, res=(280, 96)), dict(u_lines=40, v_lines=14), cam=(15, 12))
add("klein-ghost", "minimal", "Klein bottle, hidden lines kept (2nd pen)", lambda v: pk.surface(
    "Klein Ghost",
    "-(2/15)*cos(u)*(3*cos(v) - 30*sin(u) + 90*cos(u)**4*sin(u) - 60*cos(u)**6*sin(u) + 5*cos(u)*cos(v)*sin(u))",
    "(2/15)*(3 + 5*cos(u)*sin(u))*sin(v)",
    "(1/15)*sin(u)*(3*cos(v) - 3*cos(u)**2*cos(v) - 48*cos(u)**4*cos(v) + 48*cos(u)**6*cos(v) - 60*sin(u) + 5*cos(u)*cos(v)*sin(u)"
    " - 5*cos(u)**3*cos(v)*sin(u) - 80*cos(u)**5*cos(v)*sin(u) + 80*cos(u)**7*cos(v)*sin(u))",
    u=(0, math.pi), v=(0, math.tau), u_lines=("Rings", 40), v_lines=("Bands", 14), closed=(False, True),
    edges=(False, False), values=v, res=(280, 96)), dict(u_lines=28, v_lines=10), cam=(15, 12), plot={"hidden": 2})
add("mobius", "minimal", "Mobius band", lambda v: pk.surface(
    "Mobius", "(1 + v/2*cos(twists*u/2))*cos(u)", "(1 + v/2*cos(twists*u/2))*sin(u)", "v/2*sin(twists*u/2)",
    u=(0, math.tau), v=("-width", "width"),
    params=[P_("Half Twists", "twists", 1, 0, 7, "Odd: one-sided", "i"), P_("Width", "width", 0.8, 0.1, 1.4)],
    u_lines=("Rungs", 60), v_lines=("Bands", 5), closed=(True, False), edges=(False, True), values=v, res=(300, 24)),
    dict(twists=1, width=0.8, u_lines=60, v_lines=5), cam=(160, 33))
add("seashell", "minimal", "Seashell", lambda v: pk.surface(
    "Seashell", "(grow*(1 - v/tau)*(1 + cos(u)) + core)*cos(coils*v)", "(grow*(1 - v/tau)*(1 + cos(u)) + core)*sin(coils*v)",
    "rise*v/tau + grow*(1 - v/tau)*sin(u)", u=(0, math.tau), v=(0, math.tau * 0.97),
    params=[P_("Coils", "coils", 2.5, 0.5, 6.0), P_("Growth", "grow", 1.25, 0.2, 3.0, "Size of the opening"),
            P_("Core", "core", 0.15, 0.0, 2.0, "Radius of the hollow axis"), P_("Rise", "rise", 4.0, 0.0, 12.0, "Height of the spire")],
    u_lines=("Ribs", 16), v_lines=("Growth Lines", 60), closed=(True, False), edges=(False, True), values=v, res=(64, 400)),
    dict(coils=2.5, grow=1.25, core=0.15, rise=4.0, u_lines=16, v_lines=60), cam=(40, 15))
add("monkey-saddle", "minimal", "Monkey saddle", lambda v: pk.surface(
    "Monkey Saddle", "v*cos(u)", "v*sin(u)", "height * v**3 * cos(legs*u)", u=(0, math.tau), v=(0.0, 1.0),
    params=[P_("Legs", "legs", 3, 1, 9, "Number of dips round the rim", "i"), P_("Height", "height", 0.45, 0.0, 2.0)],
    u_lines=("Spokes", 24), v_lines=("Rings", 8), closed=(True, False), edges=(False, "hi"), values=v, res=(240, 60),
    dots=True, pole=True), dict(legs=3, height=0.45, u_lines=24, v_lines=8, dots=True), cam=(25, 30))

# --------------------------------------------------------------------------------------------- terrain
ROWS = dict(u=(-1.0, 1.0), v=(-1.0, 1.0), edges=(False, False))
add("ridgeline-pulsar", "terrain", "Ridgelines: pulsar", lambda v: pk.surface(
    "Ridgeline Pulsar", "u", "v", "height * exp(-(u/width)**2) * max(noise(u*rough + seed, v*9, seed, 3) - 0.35, 0)**1.5 * 4",
    params=[P_("Height", "height", 0.3, 0.0, 2.0), P_("Width", "width", 0.38, 0.05, 2.0, "Width of the active middle part"),
            P_("Roughness", "rough", 6.0, 0.5, 30.0), P_("Seed", "seed", 5.0, 0.0, 100.0)],
    u_lines=("Columns", 0), v_lines=("Rows", 64), values=v, res=(400, 400), **ROWS),
    dict(height=0.3, width=0.38, rough=6.0, seed=5.0, u_lines=0, v_lines=64), cam=(0, 38))
add("ridgeline-ripple", "terrain", "Ridgelines: a drop in water", lambda v: pk.surface(
    "Ridgeline Ripple", "u", "v", "height * cos(waves * sqrt(u*u + v*v)) * exp(-(u*u + v*v) / 0.35)",
    params=[P_("Height", "height", 0.22, 0.0, 2.0), P_("Waves", "waves", 22.0, 0.0, 80.0)],
    u_lines=("Columns", 0), v_lines=("Rows", 56), values=v, res=(300, 300), **ROWS),
    dict(height=0.22, waves=22.0, u_lines=0, v_lines=56), cam=(0, 34))
add("ridgeline-range", "terrain", "Ridgelines: a mountain range", lambda v: pk.surface(
    "Ridgeline Range", "u", "v", "height * exp(-(v/0.55)**2) * exp(-(u/0.9)**4) * noise(u*scale + seed, v*scale, seed, 4)**2 * 2.2",
    params=[P_("Height", "height", 0.75, 0.0, 3.0), P_("Scale", "scale", 2.2, 0.2, 12.0), P_("Seed", "seed", 11.0, 0.0, 100.0)],
    u_lines=("Columns", 0), v_lines=("Rows", 70), values=v, res=(360, 360), **ROWS),
    dict(height=0.75, scale=2.2, seed=11.0, u_lines=0, v_lines=70), cam=(0, 30))
add("mesh-hills", "terrain", "Hills as a square mesh", lambda v: pk.surface(
    "Mesh Hills", "u", "v", "height * (noise(u*scale + seed, v*scale, seed, 2) - 0.5)", u=(-1.0, 1.0), v=(-1.0, 1.0),
    params=[P_("Height", "height", 0.9, 0.0, 3.0), P_("Scale", "scale", 1.3, 0.2, 12.0), P_("Seed", "seed", 2.0, 0.0, 100.0)],
    u_lines=("Columns", 30), v_lines=("Rows", 30), values=v, res=(240, 240)),
    dict(height=0.9, scale=1.3, seed=2.0, u_lines=30, v_lines=30), cam=(35, 30))
WELL = "-(m1/sqrt((u-0.35)**2 + (v-0.2)**2 + soft) + m2/sqrt((u+0.45)**2 + (v+0.3)**2 + soft) + m3/sqrt((u+0.05)**2 + (v-0.55)**2 + soft))"
add("gravity-wells", "terrain", "Gravity wells in a grid", lambda v: pk.surface(
    "Gravity Wells", "u", "v", f"depth * max({WELL}, -floor_at)", u=(-1.0, 1.0), v=(-1.0, 1.0),
    params=[P_("Depth", "depth", 0.07, 0.0, 0.5), P_("Mass 1", "m1", 1.0, 0.0, 3.0), P_("Mass 2", "m2", 0.6, 0.0, 3.0),
            P_("Mass 3", "m3", 0.3, 0.0, 3.0), P_("Softness", "soft", 0.004, 0.0005, 0.1, "Rounds the bottom of each well"),
            P_("Floor", "floor_at", 12.0, 1.0, 40.0, "Cuts the wells off flat at this depth")],
    u_lines=("Columns", 36), v_lines=("Rows", 36), values=v, res=(320, 320)),
    dict(depth=0.07, m1=1.0, m2=0.6, m3=0.4, soft=0.006, floor_at=9.0, u_lines=36, v_lines=36), cam=(30, 38))
add("contour-terrain", "terrain", "Terrain as stacked height contours", lambda v: pk.surface(
    "Contour Terrain", "u", "v", "height * noise(u*scale + seed, v*scale, seed, 1)**1.6", u=(-1.0, 1.0), v=(-1.0, 1.0),
    params=[P_("Height", "height", 1.1, 0.0, 3.0), P_("Scale", "scale", 1.4, 0.2, 12.0), P_("Seed", "seed", 8.0, 0.0, 100.0)],
    u_lines=("Columns", 0), v_lines=("Rows", 0), families=[("Contours", "contours", "z", 26)], values=v, res=(260, 260)),
    dict(height=1.3, scale=1.1, seed=8.0, contours=24, u_lines=0, v_lines=0), cam=(30, 36))
add("flamm", "terrain", "Flamm's paraboloid, in perspective", lambda v: pk.surface(
    "Flamm", "v*cos(u)", "v*sin(u)", "2*sqrt(rs*(v - rs)) - 2*sqrt(rs*(3 - rs))", u=(0, math.tau), v=("rs", 3.0),
    params=[P_("Throat", "rs", 0.3, 0.05, 1.5, "Schwarzschild radius: the size of the hole")],
    u_lines=("Spokes", 36), v_lines=("Rings", 18), closed=(True, False), edges=(False, True), values=v, res=(240, 160),
    pole=True), dict(rs=0.3, u_lines=40, v_lines=18), cam=(0, 32), persp=dict(lens=28.0, distance=5.6, target=(0, 0, -0.7)))
add("wave-field", "terrain", "Two wave sources crossing", lambda v: pk.surface(
    "Wave Field", "u", "v", "height * (sin(waves*sqrt((u-0.5)**2 + (v+0.4)**2)) + sin(waves*sqrt((u+0.5)**2 + (v+0.4)**2)))",
    u=(-1.0, 1.0), v=(-1.0, 1.0), params=[P_("Height", "height", 0.045, 0.0, 0.5), P_("Waves", "waves", 16.0, 0.0, 60.0)],
    u_lines=("Columns", 0), v_lines=("Rows", 60), values=v, res=(320, 320), edges=(False, False)),
    dict(height=0.045, waves=16.0, u_lines=0, v_lines=60), cam=(0, 36))

FAMILIES = [("hopf", "Hopf fibration"), ("sphere", "Fields on a sphere"), ("sliced", "Sliced solids"),
            ("minimal", "Minimal surfaces and other classics"), ("terrain", "Ridgelines and terrain")]
