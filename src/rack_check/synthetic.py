"""Seeded synthetic racking: bays, levels and pallet weights. Invented, not a real site."""

import random

from rack_check.check import Level

# span in metres -> (beam fitted when the rack was installed, pallets per level)
FITTED = {1.8: ("B80", 2), 2.7: ("B100", 2), 3.6: ("B140", 3)}


def site(seed: int, aisles: str = "ABCD", bays: int = 12, levels: int = 4) -> list[Level]:
    rng = random.Random(seed)
    out = []
    for a in aisles:
        for b in range(1, bays + 1):
            span = rng.choice(list(FITTED))
            profile, pallets = FITTED[span]
            heavy = rng.random() < 0.15  # a heavier product line moved into this bay
            for lv in range(1, levels + 1):
                kg = rng.uniform(900, 1500) if heavy else rng.uniform(350, 1050)
                out.append(Level(f"{a}{b:02d}", lv, span, profile, pallets, round(kg, 0)))
    return out
