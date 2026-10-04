# Roadmap

What is left, as of 2026-10-04 (after v26, the sofa). The user decides the order. Update this file at the end of each round.

## Furniture

Each piece replaces its grey block in `build_furniture` ([adding-furniture.md](adding-furniture.md)). The blocks come from the scan, so they give each piece's position and footprint.

| Block | Where (model frame) |
|---|---|
| `Rug`, `Coffee_Table` | In front of the sofa |
| `Chair_1`, `Chair_2` (with backs), `Footstool` | Mid-room, between the rug and the island |
| `Desk` | Against the east wall of the living room |
| `Stool`, `Speaker_Unit` | Under the east window |
| `Bookshelf` | Free-standing, against the west wall in front of the pilaster |
| `Media_Unit` | Against the east wall, by the mezzanine front |
| `Trolley` | By the island |
| `Dining_Table` | Dining area, under the mezzanine |

Anything else in the photos (small items, soft furnishings, lights) has no block yet. Ask the user which ones they want.

Done: the sofa and its ottoman (round three; the scan's `Pouf` block was the ottoman, moved). Next biggest in the main views: the rug, the coffee table (its 0.48 m solid block hides the sofa front in photos 1 and 3) and the dining table.

## The rest of the flat

These rooms are grey boxes from the plan. Each needs references before detailed work, and a scan is best.

- **Stairs:** 10 steps in two flights, in the hallway. Waiting for the user's photos.
- **Hallway, shower room, stores:** the plan is the only source. The listing has one shower-room photo.
- **Upper floor:** two bedrooms and a hallway on the mezzanine. The floor level (2.08) is inferred from the riser count, not measured. The listing has three photos.

A new Polycam scan has its own origin. Align it to the model frame before measuring: use `scan_tools.py`'s yaw and floor fit, then line up a surface that both scans share (the hallway door, the mezzanine front).

## Carried over from earlier rounds

Details and reasons are in the [decision record](../../../knowledge/decisions/apartment-model.md), under each round's Open items.

- **Shell:** the lower glazing rail and the right-window mullion spacing. The radiator is 10–15 cm too high and about 15 cm too far from the window wall. Ceiling lines drift at the frame corners of photos 3 and 5.
- **Brick:** texture contrast is about half the photos'. Lit reveals read mauve-grey; in the photos they glow orange-red. Reviewers split on how visible the mortar should be.
- **Floor:** cleaner than the real one, which has knots, cracks and dark streaks. Plank size is not measured.
- **Glass:** reads black from view 1.

- **Sofa (v26, 6.7):** the flanges read as thin piping, not a 1 cm wavy lip with soft pinched ears. The fabric's hue and slub level are a trade-off between photos (Colour, Slub on `Sofa_Fabric`). The tops are lit a little differently from the photos (the room's light, not the fabric). No sat-in creases or wear beyond a 2 cm sag. Loose cushions and throws are not modelled.
- **Lighting:** the stand-in blocks (0.45 grey) bounce more light than the real dark furniture; replacing them piece by piece will change the fill on everything near them.

## Waiting on the user

- A tape measurement of one floor plank.
- A close, straight-on photo of the brick wall.
- Stair photos.
- Was photo 4 edited after it was taken? (It fits no camera.)
