"""Wilson score interval for a binomial proportion.

Chosen over the normal approximation because advisory samples are small
(13-40 pairs) and rates sit near 0 and 1, exactly where Wald intervals lie.
"""

from __future__ import annotations

import math

Z95 = 1.959963984540054


def wilson(successes: int, n: int, z: float = Z95) -> tuple[float, float]:
    if n <= 0:
        raise ValueError("wilson interval needs n > 0")
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, center - half), min(1.0, center + half))
