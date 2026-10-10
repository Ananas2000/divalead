"""Check the general signal-driven EQ constants against their JSON recipe."""
import json,re
from pathlib import Path
import numpy as np
if __name__=='__main__':
 root=Path(__file__).resolve().parent;s=json.loads((root/'dynamic_eq_settings.json').read_text());text=(root/'dynamic_eq.h').read_text();body=text.split('DYNAMIC_PARAMETERS[19]={',1)[1].split('}',1)[0];p=np.array([float(x) for x in body.split(',')]);np.testing.assert_array_equal(p,s['parameters']);text=(root/'tuned_settings.h').read_text();body=text.split('POST_SIDE_GAIN[5] = {',1)[1].split('}',1)[0];np.testing.assert_array_equal([float(x) for x in body.split(',')],s['post_side_gains_db']);print('PASS: 19 dynamic EQ parameters and 5 post-side gains reproduce bit-exact without audio')
