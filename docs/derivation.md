# Derivation

All values here are the illustrative ones in `src/rack_check/profiles.toml`: E = 200 GPa,
yield fy = 355 MPa, sag limit span/200, stress factor 1.5, g = 9.81 m/s². They are not taken
from any manufacturer or standard.

## 1. Simply supported beam

For a beam of span L, stiffness E, second moment of area I and elastic section modulus Wel:

| Load | Mid-span sag | Max moment |
|---|---|---|
| Point P at mid-span | δ = P L³ / (48 E I) | M = P L / 4 |
| Total W spread evenly | δ = 5 W L³ / (384 E I) | M = W L / 8 |

Stress is σ = M / Wel. For the same total load the spread case sags 48·5/384 = 0.625 times
as much as the point case and has half the moment.

**Hand case 1** (`tests/test_euler.py`): P = 10 kN, L = 2.0 m, I = 1e-6 m⁴, Wel = 2e-5 m³.

- δ = 10,000 × 8 / (48 × 200e9 × 1e-6) = 80,000 / 9.6e6 = 8.333 mm
- M = 10,000 × 2 / 4 = 5,000 N·m, σ = 5,000 / 2e-5 = 250 MPa

**Hand case 2**: the same 10 kN spread gives 0.625 × 8.333 = 5.208 mm and 125 MPa.
Doubling L to 4.0 m multiplies either sag by 2³ = 8.

## 2. Capacity of one beam

Set the spread-load sag equal to L/ratio and solve for W:

W_sag = 384 E I / (5 · ratio · L²)

Set σ = W L / (8 Wel) equal to fy / factor:

W_stress = 8 Wel fy / (factor · L)

The beam carries min(W_sag, W_stress). A level has two beams, so the level carries
2 · min / g in kg. Sag falls with 1/L² and stress with 1/L, so stress governs short spans
and sag governs long ones.

**Hand case 3** (`tests/test_capacity.py`): B100, I = 1.2e-6 m⁴, Wel = 2.4e-5 m³, L = 2.7 m.

- W_sag = 384 × 200e9 × 1.2e-6 / (5 × 200 × 7.29) = 9.216e7 / 7,290 = 12,642 N
- W_stress = 8 × 2.4e-5 × 355e6 / (1.5 × 2.7) = 68,160 / 4.05 = 16,830 N
- Sag governs. Level capacity = 2 × 12,642 / 9.81 = 2,577 kg, and at that load the sag is
  exactly 2,700 / 200 = 13.5 mm.

## 3. Pass, fail and the fix

**Hand case 4** (`tests/test_check.py`), B100 at 2.7 m:

- 2 pallets of 1,000 kg: utilisation 2,000 / 2,577 = 78%, pass.
- 3 pallets of 1,000 kg: 116%, fail. B120 (I = 2.0e-6) carries 2,577 × 2.0 / 1.2 = 4,295 kg
  by sag, and its stress limit is higher still, so it passes. Fix cost = 2 beams × 290.00 =
  580.00 BRL.

**Hand case 5**: 3 pallets of 2,000 kg on 3.6 m. The heaviest beam, B140, carries
2 × 384 × 200e9 × 3.1e-6 / (5 × 200 × 12.96) / 9.81 = 3,745 kg, so no catalogue beam fits and
the report says to reduce the load.

## 4. Synthetic site

`synthetic.site(seed)` draws 4 aisles of 12 bays. Each bay gets a span of 1.8, 2.7 or 3.6 m
with the beam an installer would have fitted for two or three pallets of up to about a tonne.
About 15% of bays are given a heavier product (900 to 1,500 kg pallets), which is where the
failures come from.
