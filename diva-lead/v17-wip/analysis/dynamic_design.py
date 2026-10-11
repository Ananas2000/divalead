"""Reproduce general five-band and static Side constants without audio."""
import json,re
from pathlib import Path
import numpy as np
if __name__=='__main__':
 root=Path(__file__).resolve().parent;s=json.loads((root/'dynamic_eq_settings.json').read_text());text=(root/'dynamic_eq.h').read_text();assert '#define DYNAMIC_BANDS 5' in text;body=text.split('DYNAMIC_PARAMETERS[29]={',1)[1].split('}',1)[0];np.testing.assert_array_equal([float(q) for q in body.split(',')],s['parameters']);text=(root/'tuned_settings.h').read_text();count=len(s['post_side_gains_db']);assert f'#define POST_SIDE_COUNT {count}' in text
 for name,key in [('POST_SIDE_GAIN','post_side_gains_db'),('POST_SIDE_FREQ','post_side_centres_Hz')]:
  body=text.split(f'{name}[{count}] = {{',1)[1].split('}',1)[0];np.testing.assert_array_equal([float(q) for q in body.split(',')],s[key])
 print('PASS: 29 dynamic parameters and',count,'Side gains/frequencies reproduce bit-exact without audio')
