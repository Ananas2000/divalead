"""Verify the two fixed chorus-return damping constants without audio."""
import json,re
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parent
s=json.loads((root/'return_damp_settings.json').read_text());h=(root/'return_damp_settings.h').read_text()
for name,key in [('RETURN_DAMP_FREQ','cutoff_Hz'),('RETURN_DAMP_GAIN','amount')]:
 value=float(re.search(r'(?m)^#define '+name+r' ([^\n]+)$',h)[1]);np.testing.assert_array_equal(value,s[key])
assert s['input_only'] and s['extra_latency_frames']==0
p=(root/'lead_finish.c').read_text();assert '#include "return_damp_settings.h"' in p
for statement in ['s->return_mid_low=0;', 'exp(-2*PI*fmin(RETURN_DAMP_FREQ,s->rate*.45)/s->rate)', 'RETURN_DAMP_GAIN*(return_mid-s->return_mid_low)']:
 assert statement in p,statement
print('PASS: two constant Mid-return damping controls and reset/no-extra-latency verified')
