"""Keep numerical stage constraints inside the unchanged original53 acceptance caps.

Search uses fixed carriers for some metrics. A numerical candidate still requires
fresh Diva/Windows, matching independent source, arbitrary inputs and fresh-carrier
checks by the controller. This helper never widens a stage or acceptance limit.
"""
import math

ORIGINAL53_LIMITS = dict(
    H24=1., upper_harm=1.01, upper_off=1.01, low_harm=1.01,
    ERB=1.01, relative_phase=1.005, whole=1.01, envelope=1.01,
    body=1.03, stereo_phase=1.03, stereo_balance=1.03,
)

def cap_with_original53(stage_limits, original53, baseline):
    limits = dict(stage_limits)
    for key, absolute_ratio in ORIGINAL53_LIMITS.items():
        original, current = float(original53[key]), float(baseline[key])
        assert math.isfinite(original) and math.isfinite(current)
        assert original > 0 and current > 0
        cap = absolute_ratio * original / current
        limits[key] = min(limits.get(key, math.inf), cap)
    return limits


def repair_near_feasible_rows(rows, best_score, initial, offsets_field, compute, probe):
    """Re-evaluate smaller steps from an actual feasible origin; never widen limits.

    SLSQP can stop just outside a hard boundary. Only re-evaluated, fully feasible
    points can reach probe() and its normal best-model checkpoint.
    """
    import numpy as np
    eligible = [row for row in rows if row['weighted_score'] < best_score
                and -1e-4 <= row['minimum_constraint'] < 0]
    trials = []
    selected_score = float(best_score)
    if eligible:
        candidate = min(eligible, key=lambda row: row['weighted_score'])
        offsets = np.asarray(candidate[offsets_field], dtype=float)
        origin = np.asarray(initial, dtype=float)
        assert offsets.shape == origin.shape
        for fraction in [.999, .995, .99, .98, .95, .9, .8, .5]:
            point = origin + fraction * (offsets - origin)
            _, row, constraints = compute(point)
            minimum = float(np.min(constraints))
            feasible = minimum >= -1e-12
            trials.append(dict(fraction=fraction, score=row['weighted_score'],
                               minimum_constraint=minimum, feasible=feasible))
            if feasible and row['weighted_score'] < selected_score:
                probe(point)
                selected_score = row['weighted_score']
    return dict(probes=trials, selected_best_score=selected_score,
                guard_limits_unchanged=True, feasibility_tolerance_unchanged=True,
                requires_fresh_actual_validation=True)
