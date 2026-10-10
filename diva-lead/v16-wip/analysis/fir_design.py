"""Reproduce v16's unchanged v15 FIR coefficients without audio."""
import re
from pathlib import Path
import numpy as np
from v15_fir_design import make_v15_kernels
if __name__=='__main__':
 root=Path(__file__).resolve().parent;h=make_v15_kernels(root);body=(root/'fir_kernels.h').read_text().split(' = {',1)[1];header=np.array([float(z) for z in re.findall(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?',body)]).reshape(h.shape);np.testing.assert_array_equal(h,header);print('PASS: all',h.size,'FIR coefficients reproduced bit-exact without audio; shape',h.shape)
