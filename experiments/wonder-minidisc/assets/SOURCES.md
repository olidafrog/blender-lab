# Asset sources

All assets are CC0 (public domain). Downloaded 2026-09-27. ambientCG zips unzipped; DirectX normals, sample .blend/.usdc/.mtlx/.tres removed (Blender uses the NormalGL maps). All grey maps are white = feature, black = clean.

## HDRIs (Poly Haven, CC0 — https://polyhaven.com/license)

| File | Source | Notes |
|---|---|---|
| `hdri/studio_small_09_4k.exr` | https://polyhaven.com/a/studio_small_09 | Small studio, umbrella + softbox, infinity cove. Main product HDRI. |
| `hdri/white_studio_05_4k.hdr` | https://polyhaven.com/a/white_studio_05 | Large white cyclorama studio, soft, low contrast. Brightest / most neutral. |
| `hdri/studio_kontrast_04_2k.hdr` | https://polyhaven.com/a/studio_kontrast_04 | White studio, rectangular softboxes, low contrast. Good for crisp rectangular reflections. |

## Surface imperfections (ambientCG, CC0 — https://docs.ambientcg.com/license/)

| Folder | Source | Use | Map to use |
|---|---|---|---|
| `imperfections/Scratches001/` | https://ambientcg.com/view?id=Scratches001 | Fine parallel (directional) hairline scratches | `_Opacity.jpg` (= `_Color.jpg`) as mask |
| `imperfections/Scratches005/` | https://ambientcg.com/view?id=Scratches005 | Sparse random curly scratches over faint directional wipe | `_Opacity.jpg` as mask |
| `imperfections/SurfaceImperfections003/` | https://ambientcg.com/view?id=SurfaceImperfections003 | Vertical wipe smudges / streaks (heavy — use low strength) | `_Opacity.jpg` as mask |
| `imperfections/SurfaceImperfections015/` | https://ambientcg.com/view?id=SurfaceImperfections015 | Dust / fine speckle with blotches | `_Roughness.jpg`, `_Opacity.jpg`, `_Displacement.jpg` |
| `imperfections/Fingerprints002/` | https://ambientcg.com/view?id=Fingerprints002 | Scattered fingerprint smudges | `_Roughness.jpg` or `_Opacity.jpg` |
| `imperfections/Smear001/` | https://ambientcg.com/view?id=Smear001 | One large wiped smear (2048x1882) | `_Roughness.jpg` |
