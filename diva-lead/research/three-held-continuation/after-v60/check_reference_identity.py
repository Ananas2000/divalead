from pathlib import Path
import os,sys,json,hashlib
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import soundfile as sf,numpy as np
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');sys.path.insert(0,str(REPO/'diva-lead/research/repository-selection'));import compare_all as a
uploaded=Path('/workspace/attachments/c7279e3d-5fcb-48c4-b77b-f93b2c677f27/Diva_original_lead_reference.wav');x,sr=sf.read(uploaded);p=REPO/'diva-lead/v59-wip/Diva_original_lead_reference.wav';y,yr=sf.read(p)
assert sr==yr==48000 and x.shape==(176064,2);np.testing.assert_array_equal(x,y);np.testing.assert_array_equal(x,a.REF)
report=dict(uploaded_original_decoded_exact_to_published_reference=True,actual_metric_target_decoded_exact_to_uploaded_original=True,frames=len(x),channels=2,sample_rate=48000,reference_decoded_float64_SHA256=hashlib.sha256(x.astype('<f8').tobytes()).hexdigest(),MistaTowa_used=False,target_not_previous_version=True)
(R/'reference-identity-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
