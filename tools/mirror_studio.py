"""Mirror-direction studio: design what a mirror-like subject reflects (from wonder-minidisc).

For a mirror, foil, chrome, diffraction grating or dark gloss subject the environment IS the material
(knowledge/insights.md). Work from the camera's view reflected in the subject:

    from mirror_studio import mirror_direction, area_light, check_lights, add_flag, add_ring
    mdir = mirror_direction(cam.location, centre, normal=(0, 0, 1))
    check_lights([("Key", key_pos), ("Back", back_pos)], centre, mdir, flag_dist=0.4)   # prints a verdict
    add_flag(scene, centre, mdir, dist=0.4, size=3.0)       # black card only reflections see
    add_ring(scene, centre, mdir, [(15.5, 0), (21, 45)], dist=0.6, span_deg=28, width=0.01, power=40)

- A big light within ~62 deg of the mirror direction and not behind the flag washes the subject white
  (a grating sums every colour band; a satin top mirrors the softbox).
- The flag is a reflection matte: invisible to camera, diffuse, shadow and volume rays.
- Ring lights are short arcs at an angle off the mirror direction, glossy-only, so they can be bright
  without lighting the table. For a grating the angle sets the hue (first order: lambda = d sin(angle)).
"""
import math

import bpy
from mathutils import Matrix, Vector


def mirror_direction(cam_location, point, normal=(0, 0, 1)):
    """Unit vector from `point` along the camera's view reflected in a surface with `normal`: where the
    subject 'looks' in the mirror."""
    n = Vector(normal).normalized()
    v = (Vector(point) - Vector(cam_location)).normalized()          # camera -> point
    return (v - 2 * v.dot(n) * n).normalized()


def area_light(scene, name, power, size, pos, target=(0, 0, 0), glossy=True, transmission=True, diffuse=True,
               up=None, shape="SQUARE"):
    """Area light at pos facing target; size a float or (x, y); `up` sets the light's local Y."""
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = power
    if isinstance(size, (tuple, list)):
        ld.shape, ld.size, ld.size_y = "RECTANGLE", size[0], size[1]
    else:
        ld.shape, ld.size = shape, size
    ob = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(ob)
    ob.location = pos
    if up is None:
        ob.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    else:
        z = (Vector(pos) - Vector(target)).normalized()
        y = (Vector(up) - z * Vector(up).dot(z)).normalized()
        ob.rotation_euler = Matrix((y.cross(z), y, z)).transposed().to_euler()
    ob.visible_glossy, ob.visible_transmission, ob.visible_diffuse = glossy, transmission, diffuse
    return ob


def check_lights(lights, centre, mdir, flag_dist=None, flag_size=None, safe_deg=62.0):
    """lights: [(name, position)]. Prints each light's angle off the mirror direction and whether it is
    safe: hidden behind the flag (further out than the flag and inside its angular size), or more than
    safe_deg off the mirror direction. Returns the names that are not."""
    bad = []
    for name, pos in lights:
        v = Vector(pos) - Vector(centre)
        ang = math.degrees(v.angle(mdir))
        behind = False
        if flag_dist is not None and flag_size is not None and v.dot(mdir) > flag_dist:
            behind = ang < math.degrees(math.atan((flag_size / 2) / flag_dist))
        ok = behind or ang > safe_deg
        print(f"[out] {name}: {ang:.0f} deg off mirror, behind flag {behind}, {'OK' if ok else 'IN THE MIRROR (wash)'}")
        if not ok:
            bad.append(name)
    return bad


def add_flag(scene, centre, mdir, dist, size, name="Flag", value=0.01):
    """Black card on the mirror direction, seen only by glossy and transmission rays."""
    me = bpy.data.meshes.new(name)
    h = size / 2
    me.from_pydata([(-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    ob.location = Vector(centre) + mdir * dist
    ob.rotation_euler = (-mdir).to_track_quat("-Z", "Y").to_euler()
    ob.visible_camera = ob.visible_diffuse = ob.visible_shadow = ob.visible_volume_scatter = False
    m = bpy.data.materials.new(f"{name} Black")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (value, value, value, 1)
    b.inputs["Roughness"].default_value = 0.9
    me.materials.append(m)
    return ob


def add_ring(scene, centre, mdir, wedges, dist, span_deg, width, power, name="Wedge"):
    """Glossy-only arc lights round the mirror direction. wedges: [(degrees off mirror, azimuth)]."""
    perp = mdir.cross(Vector((0, 0, 1)))
    perp = (perp if perp.length > 1e-6 else mdir.cross(Vector((1, 0, 0)))).normalized()
    out = []
    for i, (ang, az) in enumerate(wedges):
        d = Matrix.Rotation(math.radians(az), 3, mdir) @ (Matrix.Rotation(math.radians(ang), 3, perp) @ mdir)
        pos = Vector(centre) + d * dist
        arc = dist * math.sin(math.radians(ang)) * math.radians(span_deg)
        radial = d - mdir * d.dot(mdir)
        out.append(area_light(scene, f"{name}{i}", power, (arc, width), tuple(pos), target=tuple(centre),
                              diffuse=False, up=tuple(radial)))
    return out
