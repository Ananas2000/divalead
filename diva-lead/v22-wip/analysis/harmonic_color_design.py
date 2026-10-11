"""Verify the four input-tracked harmonic filters from their saved constants."""
from pathlib import Path
import json,re
import numpy as np
root=Path(__file__).resolve().parent
s=json.loads((root/'harmonic_color_settings.json').read_text());h=(root/'harmonic_color.h').read_text()
for name,key in [('COLOR_ORDERS','harmonic_orders'),('COLOR_GAINS','gains_db')]:
    body=h.split(name+'[4]={',1)[1].split('}',1)[0]
    np.testing.assert_array_equal([float(v) for v in body.split(',')],s[key])
for name,key in [('COLOR_Q_PER_ORDER','q_per_harmonic_order'),('COLOR_LOOKAHEAD_MS','lookahead_ms_from_existing_fir')]:
    assert float(re.search(r'#define '+name+r' ([0-9.]+)',h)[1])==s[key]
p=(root/'pitch_tracker.h').read_text()
for statement in ['pitch_pass(&s->highpass,rate,35,','pitch_pass(s->lowpass,rate,200,','pitch_pass(s->lowpass+1,rate,200,','f>45&&f<220','s->raw=s->tracked=100','s->count<3','rate*.005']:
    assert statement in p,statement
assert '(t->frame&15)==0' in h
print('PASS: four harmonic orders/gains and Q/lookahead (10 constants); input-only detector settings verified')
