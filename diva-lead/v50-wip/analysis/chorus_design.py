"""Verify fixed Mid/Side chorus scales without reading recordings."""
import json,re
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    c=json.loads((ROOT/'mid_side_chorus_settings.json').read_text());text=(ROOT/'tuned_settings.h').read_text()
    for name,key in [('MID_CHORUS_SCALE','mid_scale'),('SIDE_CHORUS_SCALE','side_scale')]:
        value=float(re.search(r'(?m)^#define '+name+r' ([^\n]+)$',text).group(1));np.testing.assert_array_equal(value,c[key])
    assert c['stage']=='core chorus before existing Side EQ'
    print('PASS: two fixed Mid/Side chorus scales reproduced without audio')
