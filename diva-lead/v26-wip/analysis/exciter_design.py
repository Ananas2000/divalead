"""Verify the fixed excitation constants without reading any audio."""
import json,re
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parent;cfg=json.loads((root/'exciter_settings.json').read_text());text=(root/'exciter.h').read_text();body=text.split('EXCITER_PARAMETERS[6]={',1)[1].split('}',1)[0];np.testing.assert_array_equal([float(v) for v in body.split(',')],cfg['parameters']);assert cfg['highpass_Hz']==10;assert '3.14159265358979323846*10/sr' in text;print('PASS: six excitation constants reproduce bit-exact without audio; highpass 10 Hz')
