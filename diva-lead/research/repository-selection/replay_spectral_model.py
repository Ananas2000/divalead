"""Replay a complete saved53-derived spectral model from committed source fixtures.

This checks the spectral fixture. It does not independently rebuild the pre-STFT chain.
"""
from pathlib import Path
import sys,json,os,argparse,hashlib,importlib.util
import numpy as np,soundfile as sf
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2]
sys.path.insert(0,str(HERE));import compare_all as common
def kwargs(cfg):
 kw=dict(sigma=cfg['mask_sigma'],key_quadratic=cfg['key_quadratic'],key_slopes=cfg['key_slopes'],phase_angles=cfg['common_phase_radians'],hf_parameters=cfg['hf_matrix_parameters'],hf_anchors=cfg['hf_matrix_anchors_Hz'],upper_rolloff=cfg['upper_rolloff_Hz'],harmonic_gain=cfg['harmonic_gain_parameters'],gain_orders=cfg['harmonic_gain_orders'],hf_sigma=cfg['hf_mask_sigma'],phase_key_slopes=cfg['common_phase_key_slopes'],phase_key_quadratic=cfg['common_phase_key_quadratic'],core_anchors=cfg['anchors_Hz'],adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance'])
 if cfg.get('fine_phase_harmonic_parameters') is not None:kw['fine_phase']=cfg['fine_phase_harmonic_parameters']
 return kw

def replay(directory,output):
 directory=Path(directory);manifest=json.loads((directory/'source_manifest.json').read_text());cfg=json.loads((directory/'analysis/spectral_model.json').read_text())
 for key in ['source_preset','source_WAV','before_spectral_WAV']:
  file=REPO/manifest[key];assert hashlib.sha256(file.read_bytes()).hexdigest()==manifest[key+'_SHA256'],(key,'source fixture differs')
 source,sr=sf.read(REPO/manifest['source_WAV']);before,rate=sf.read(REPO/manifest['before_spectral_WAV']);assert sr==rate==48000
 implementation=REPO/manifest.get('independent_spectral_implementation','diva-lead/v53-wip/analysis/independent_spectral_ms.py')
 if cfg.get('fine_phase_harmonic_parameters') is not None:assert manifest.get('independent_spectral_implementation_SHA256')==hashlib.sha256(implementation.read_bytes()).hexdigest()
 spec=importlib.util.spec_from_file_location('complete53_independent',implementation);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 y,extra=module.spectral_ms(before,source,sr,manifest['before_latency_frames'],cfg['parameters'],**kwargs(cfg));settings=json.loads((REPO/manifest['settings_path']).read_text())['settings'];edit=common.h.edit_aligned(common.h.align_with_pdc(y,settings,latency=manifest['before_latency_frames']));actual=sf.read(directory/manifest['actual_reference_edit'])[0];np.testing.assert_allclose(edit,actual,rtol=0,atol=2e-7)
 output=Path(output);output.mkdir(parents=True,exist_ok=True);sf.write(output/'replayed-reference-edit.wav',edit,sr,subtype='FLOAT');result=dict(model=directory.name,actual_spectral_edit_reconstruction_max_error=float(np.max(abs(edit-actual))),tolerance=2e-7,extra_STFT_latency_frames=extra,source_hashes_checked=True,full_preSTFT_independent_pipeline_rerun=False,model_audition_claimed=False,match_reached=False);(output/'replay-validation.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
 current=HERE/'CURRENT_RESEARCH_MODEL.json';default_model=HERE/(json.loads(current.read_text())['model_directory'] if current.exists() else 'after-hf-power')
 parser=argparse.ArgumentParser();parser.add_argument('--model',type=Path,default=default_model);parser.add_argument('--output',type=Path,default=Path(os.environ.get('DIVALEAD_SELECTION_WORK',str(Path.home()/'.cache/divalead-repository-selection')))/'full-model-replay');args=parser.parse_args();print(json.dumps(replay(args.model,args.output),indent=2))
