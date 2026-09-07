from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class PerturbationResult:
    stable: bool
    max_abs_diff: float
    baseline: tuple[float, ...]
    perturbed: tuple[float, ...]
    interpretation: str


def future_perturbation_test(
    values: Sequence[float],
    cutoff_index: int,
    predictor: Callable[[Sequence[float], int], Sequence[float]],
    *,
    seed: int = 7,
    scale: float = 10.0,
    atol: float = 1e-12,
) -> PerturbationResult:
    if cutoff_index < 0 or cutoff_index >= len(values):
        raise ValueError("cutoff_index out of range")
    baseline = tuple(float(x) for x in predictor(values, cutoff_index))
    rng = random.Random(seed)
    mutated = list(map(float, values))
    for i in range(cutoff_index + 1, len(mutated)):
        mutated[i] = mutated[i] + scale * (1.0 + rng.random())
    perturbed = tuple(float(x) for x in predictor(mutated, cutoff_index))
    if len(baseline) != len(perturbed):
        raise ValueError("predictor output length changed under perturbation")
    diffs = [abs(a-b) for a,b in zip(baseline, perturbed)]
    maxdiff = max(diffs, default=0.0)
    stable = math.isfinite(maxdiff) and maxdiff <= atol
    interpretation = (
        "No tested pre-cutoff output changed under this future-data perturbation. "
        "This supports this specific invariance check but does not prove absence of all leakage."
        if stable else
        "At least one pre-cutoff output changed after only post-cutoff values were perturbed; inspect the pipeline for future dependence."
    )
    return PerturbationResult(stable, maxdiff, baseline, perturbed, interpretation)
