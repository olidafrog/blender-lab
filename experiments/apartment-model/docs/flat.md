# The flat

Flat 233, Manhattan Building, Bow Quarter, 60 Fairfield Road, London E3 2UG. Lat 51°31′54″ N, lon 0°1′12″ W.

The building is a Grade II listed match factory (Bryant & May), built 1909–11 with a reinforced-concrete frame and brick walls. It became flats in 1988. The mezzanines were added then as separate structures inside the old frame.

## Levels

The flat is a duplex. The plan names its levels after the building's floors:

| Plan name | What it is | Height (floor = 0) |
|---|---|---|
| Second Floor | The living level: living room and kitchen (double height), hallway, shower room, two stores, stair up | 0 |
| Third Floor | The upper level: two bedrooms and a hallway. It is the **mezzanine** over the back of the flat. Its front wall looks into the living room through the internal windows | 2.08 (inferred: 10 risers × 0.208; not measured) |

The living room is double height to the ceiling (4.08). Under the mezzanine (soffit 1.93) are the kitchen (plan-west) and the dining area (plan-east).

## Directions

**All compass words in the code and notes are plan directions, not compass directions.** Read the plan with the window wall at the top. Plan-left is "west" (−y), plan-right is "east" (+y), the window wall is "north".

The real bearing: the windows face **142° (SE)** (`references/scans/…/compass.png`). So in the model frame:

| Model axis | Points to | True bearing |
|---|---|---|
| −x | out of the windows | 142° (SE) |
| +x | into the flat, toward the hallway | 322° (NW) |
| −y ("west" wall) | plan-left | 52° (NE) |
| +y ("east" wall) | plan-right | 232° (SW) |

Use the true bearing for any sun study. Units are metres. The origin is the scan's: z = 0 is the living-room floor, and the window wall's inner face is x = −4.40.

## Headline measurements

These are measured facts. The values the model uses live in `P` in `scripts/build.py`. Where this table and `P` differ, `P` is the fitted value.

| What | Scan | User's tape | Plan |
|---|---|---|---|
| Living room, window wall to dining back wall | 8.74 m | | 9.0 m |
| Living room, wall to wall | 5.63 m | | 5.68 m |
| Floor to ceiling | 4.08–4.09 | 4.05 | |
| Floor to mezzanine soffit (kitchen ceiling) | 1.93–1.94 | 1.91 | |
| Floor to underside of the mezzanine girder | 3.69 | 3.55 | |

The Polycam plan says 9.00 × 5.82 m. It measures into the window reveals, so do not use it.

## Terms and their names in the model

Collections in the `.blend`: `Shell`, `Windows`, `Mezzanine`, `Kitchen`, `Flat`, `Furniture`, `Cameras`, `Outside`.

| Term | What it is | In `build.py` |
|---|---|---|
| Window wall | The brick outer wall with two arched factory windows | `Window_Wall_*`; `win_x` |
| Factory windows | Painted steel, segmental-arched, closed | `build_window`; `win_*`, `frame_*` |
| Reveal | The splayed brick sides of each window opening. They are wider at the room face, and shifted toward the central pier | `Reveal_<i>`; `win_w`, `win_w_frame`, `reveal_shift` |
| Piers | Three brick blocks standing proud of the window wall to about 1.6 m | `Pier_<i>`; `piers`, `pier_*` |
| Brick returns | A strip of brick on each side wall next to the window wall | `Brick_Return_*` |
| Central beam | The downstand beam along the room, from the central pier to the girder | `Beam_Central`; `beam_*` |
| Girder | The cross beam over the mezzanine front | `Girder`; `girder_*` |
| Pilasters | The concrete frame columns on the side walls, with small splayed heads under the girder | `Pilaster_*`; `pilaster_*`, `haunch` |
| Cove | Where the side walls curve in to meet the ceiling (not edge beams) | `Cove_*`; `cove_z`, `cove_in` |
| Mezzanine front | The white wall over the kitchen and dining area | `Mezz_Front`; `mezz_x`, `mezz_t` |
| Internal windows | Two black steel windows in the mezzanine front (the bedrooms' windows) | `Internal_Window_<i>`; `iwin*` |
| Soffit | The underside of the mezzanine: the kitchen and dining ceiling | `soffit_z` |
| Column | The slim post under the mezzanine front, at the kitchen and dining split | `Column`; `col_*` |
| Bookcase | The built-in dining bookcase with scalloped (wavy) bays | `Bookcase`; `bookcase*` |
| Radiator | The column radiator on the west wall of the living room | `Rad_*`; `radiator` |
| Panel heater | On the dining area's east wall | `Panel_Heater` |
| Grey boxes | Rooms the scan did not reach, drawn from the plan | collection `Flat`; `PX()`, `PY()` map plan pixels to metres |
| Furniture blocks | Rough boxes from the scan, there so the photos' occlusion reads | `build_furniture` |

## Materials

| Material | Real surface |
|---|---|
| `Brick` | Old cleaned factory brick, plum-maroon in shade, redder in daylight. Courses about 85 mm. Mortar close to the brick tone |
| `Oak_Floor` | Rustic oak-look herringbone, spine along the room (x). Planks 600 × 120 in the model; real size not yet measured |
| `Paint` | Matt white walls, ceiling and beams |
| `Steel_White`, `Steel_Black` | The factory windows (off-white) and the internal windows (black) |
