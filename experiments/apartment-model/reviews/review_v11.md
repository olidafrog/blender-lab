# Review v11

## 1. Score: 7.7 / 10

Layout 8.0, Windows 8.0, Structure 7.8, Built-ins 6.5.

**Pairwise:** Q is slightly closer. (Q is pixel-identical to `renders/v11.png`, so the pair was not blind.) Both put about 69 % of red pixels on photo edges, but Q has 20 % more edges and lens-corrects photos 2 and 7. P is 5 px tighter on row 1's right jamb.

## 2. Targets

- **Window wall: hit.** Row 1: jamb 5 px, arch top 4, sill 4, pier 5. Row 2: jambs ≤6, arch tops 5, transoms ≤3, mullions ≤5, pier caps 1, beam end 0. Row 5: arch top 3, sill 1, jamb 3.
- **Mezzanine front: hit.** Rows 3 and 6: internal windows ≤6, soffit ≤2, girder ≤3, column ≤3, pilasters ≤5.
- **Ceiling-to-wall lines: missed.** Rows 1, 2, 6, 7 and 8 are within 7 px.
  - Row 3: the side-wall groove is off by 16 px at x=20 and 20 px at x=1000. It is exact at the corners.
  - Row 5: the side-wall ceiling line is 9 px low and the groove 11 px low. The central beam underside is 20 px low (66 vs 46).
- **Kitchen: hit.** Counter tops 3–5 px, island right edge about 12, plinth about 10.

## 3. What works

- In row 2, the segmental arches, transom heights and arch glazing grid all match closely.
- The mezzanine front, internal windows, girder, haunched pilasters and column all land within 6 px.

## 4. Problems, ranked

1. **Camera fit in rows 3 and 5, not geometry.** In row 3 the error grows equally toward both frame edges, which is lens distortion. Row 5 sits about 10 px low, and 20 px at the beam. Fix: lens-correct photos 3 and 5 as you did photos 2 and 7. In row 5, also use the beam underside and the ceiling line as landmarks.
2. **The bookcase is a flat dark slab** (row 6, x 565–725). The photo shows 3 scalloped bays with shelves and a cupboard base about 0.9 m high. Fix: model the bays, shelves and base.
3. **The window steel is too heavy.** It is about 5 px wide in row 2; the photo's is about 3 px. Fix: reduce it to about 40 mm.

Minor: the dining panel heater is missing (row 6, x 455–490).

## 5. Research check

The image contradicts no claim. Arches are segmental, sills and piers match, the beam and girder fit, and the dining area is east and deeper.

## 6. What 8.5 needs

- Lens-correct photos 3 and 5, then refit those cameras.
- Model the bookcase in detail.
- Use slimmer window steel.
