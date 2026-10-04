"""Swyft Model 03 three-seater in Pumice, with its ottoman pushed against the window-end seat as a chaise.

Sizes from Swyft's product pages (3-seater 254 x 92 x 71, seat 70 wide, seat height 45, arm 56 high and
22 wide, ottoman 70 x 70 x 45); placement from the scan (arm end, module seams, seat front) and photos 1-3.
The sofa runs along x against the west wall; its front faces +y.
Modules: arm | seat | seat | seat | arm. A seat is a base block with a domed top and a back block on its rear;
the seats stand proud of the arms. Every block edge carries a self-fabric flange.
"""
import math

import bpy
import numpy as np

import upholstery as U


def foot(name, x, y, P, mat, coll):
    """Short dark round foot under a block."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=P["sofa_foot_d"] / 2, depth=P["sofa_foot_h"],
                                        location=(x, y, P["sofa_foot_h"] / 2))
    ob = bpy.context.active_object
    ob.name = name
    for c in ob.users_collection:
        c.objects.unlink(ob)
    coll.objects.link(ob)
    ob.data.materials.append(mat)
    m = ob.modifiers.new("Bevel", "BEVEL")
    m.width, m.segments = 0.004, 2
    return ob


def build(P, fabric, feet, coll, flange_mat=None):
    x_end = P["sofa_x_end"]                 # outer face of the arm at the room end (+x)
    y_back = P["sofa_y_front"] - P["sofa_d"]
    z0, r, fl = P["sofa_foot_h"], P["sofa_r"], P["sofa_flange"]
    seat_w, arm_w = P["sofa_seat_w"], P["sofa_arm_w"]
    gap = P["sofa_gap"]
    puff_side = P["sofa_puff_side"]
    blocks = []                              # (name, lo, hi, puff, loop axis, span, field)

    def add(name, lo, hi, puff, axis, span=None, field=None):
        blocks.append((name, lo, hi, puff, axis, span, field))

    # x positions, from the room end toward the windows
    xs = [x_end]
    for w in (arm_w, seat_w, seat_w, seat_w, arm_w):
        xs.append(xs[-1] - w)
    arm_front = P["sofa_y_front"] - P["sofa_arm_setback"]
    for i, (xa, xb) in enumerate(((xs[1], xs[0]), (xs[5], xs[4]))):
        add(f"Sofa_Arm_{i + 1}", (xa + gap, y_back, z0), (xb - gap, arm_front, P["sofa_arm_h"]),
            {"+z": puff_side, "+x": puff_side, "-x": puff_side, "+y": puff_side}, "x")
    seat_edge = P["sofa_seat_edge"]                   # the seam height at the front of the seat (Swyft: 39)
    puff_top = P["sofa_seat_h"] - seat_edge           # the dome rises to the seat height (45)
    wob, wl = P["sofa_wobble"], P["sofa_wobble_len"]
    yf = P["sofa_y_front"]
    for i in range(3):
        xa, xb = xs[i + 2], xs[i + 1]
        lo, hi = (xa + gap, y_back, z0), (xb - gap, yf, seat_edge)
        # sat in: a dip a little in front of the seat's middle, the front rolling forward over its seam
        cy = yf - P["sofa_sag_at"]
        fld = U.slump_field(lo, hi, seed=10 + i, wobble=wob, wavelength=wl,
                            dips=[((xa + xb) / 2, cy, seat_w * 0.3, 0.2, P["sofa_sag"])],
                            roll=(yf, 0.25, P["sofa_roll"]), tuck=P["sofa_tuck"])
        add(f"Sofa_Seat_{i + 1}", lo, hi, {"+z": puff_top, "+y": P["sofa_puff_front"], "+x": puff_side * 0.5, "-x": puff_side * 0.5}, "z",
            {"+z": {"y": (y_back + P["sofa_back_t"] - 0.04, yf)}}, fld)
        top = P["sofa_back_h"] - P["sofa_back_crown"]          # the back's side edges; its top bows up to back_h
        lo, hi = (xa + gap, y_back, seat_edge), (xb - gap, y_back + P["sofa_back_t"], top)
        rake = None
        if P["sofa_back_t_top"] < P["sofa_back_t"]:
            rake = U.rake_field(y_back, seat_edge, top, P["sofa_back_t"], P["sofa_back_t_top"])
        add(f"Sofa_Back_{i + 1}", lo, hi, {"+y": P["sofa_puff_back"], "+z": P["sofa_back_crown"], "-y": puff_side * 0.5}, "y",
            None, U.chain(rake, U.slump_field(lo, hi, seed=20 + i, wobble=wob * P["sofa_back_wobble"], wavelength=wl,
                                              roll=(y_back + P["sofa_back_t"], 0.2, P["sofa_back_roll"]),
                                              ripple=(y_back + P["sofa_back_t"], 0.08, P["sofa_ripple"], P["sofa_ripple_len"]))))
    # the ottoman: a free block in front of the window-end seat
    ox, oy = P["sofa_ottoman_xy"]
    ow = P["sofa_ottoman_w"]
    lo, hi = (ox - ow / 2, oy - ow / 2, z0), (ox + ow / 2, oy + ow / 2, seat_edge)
    po = P["sofa_puff_ottoman"]
    add("Sofa_Ottoman", lo, hi, {"+z": puff_top, "+x": po, "-x": po, "+y": po, "-y": po}, "z",
        None, U.slump_field(lo, hi, seed=30, wobble=wob, wavelength=wl,
                            dips=[(ox, oy, ow * 0.3, ow * 0.3, P["sofa_sag"] * 0.5)],
                            roll=(oy + ow / 2, 0.2, P["sofa_roll"]), tuck=P["sofa_tuck"]))
    for j, b in enumerate(list(blocks)):           # the arms get the wobble only
        if b[0].startswith("Sofa_Arm") and b[6] is None:
            blocks[j] = b[:6] + (U.slump_field(b[1], b[2], seed=40 + j, wobble=wob * 0.6, wavelength=wl),)

    out = []
    for k, (name, lo, hi, puff, axis, span, fld) in enumerate(blocks):
        rb = P["sofa_r_square"] if name.startswith(("Sofa_Arm", "Sofa_Back")) else r   # arms and backs stay square
        ob = U.block(name, lo, hi, r=rb, puff=puff, span=span, step=P["sofa_mesh_step"], shape=P["sofa_puff_shape"],
                     collection=coll, mat=fabric, field=fld)
        out.append(ob)
        out.append(U.flange(name + "_Flange", U.seam_paths(lo, hi, rb, axis, ear=P["sofa_ear"]), width=fl, thick=P["sofa_flange_t"],
                            seed=k, collection=coll, mat=flange_mat or fabric, field=fld))
        if hi[2] - lo[2] > 0.2 and lo[2] <= z0 + 1e-6:             # floor-standing blocks get four feet
            inset = P["sofa_foot_inset"]
            for j, (fx, fy) in enumerate(((lo[0] + inset, lo[1] + inset), (hi[0] - inset, lo[1] + inset),
                                          (lo[0] + inset, hi[1] - inset), (hi[0] - inset, hi[1] - inset))):
                out.append(foot(f"{name}_Foot_{j}", fx, fy, P, feet, coll))
    return out
