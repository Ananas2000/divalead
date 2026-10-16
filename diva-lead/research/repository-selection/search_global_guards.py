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
