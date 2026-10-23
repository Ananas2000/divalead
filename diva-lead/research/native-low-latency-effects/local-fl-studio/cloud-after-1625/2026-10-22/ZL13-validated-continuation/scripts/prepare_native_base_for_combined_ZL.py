"""Build a NEW native base for a validated combined native+ZL refit.
Never overwrite the prior supported base. The internal FLP filename is kept
compatible with the proven ZL builder; public kits get their own new ZL label.
"""
from pathlib import Path
import argparse,json,os,shutil,subprocess,sys
D=Path(__file__).resolve().parent;B=D.parent
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--destination',required=True);a=p.parse_args()
choice=json.loads(Path(a.candidate).read_text());out=Path(a.destination);assert not out.exists()
assert choice['native_base']['source_manifest']['source_preset_SHA256']=='bdf6be524002bd7d98c5e0fe7cf2e249ae451efea5b7e3dc53ec4b0c89f7d0b2'
candidate=out.with_name(out.name+'-native-candidate.json');candidate.write_text(json.dumps(choice['native_base'],indent=2)+'\n')
subprocess.run([sys.executable,'-B',str(B/'export_fl20_checkpoint.py'),str(candidate),str(out)],check=True)
subprocess.run([sys.executable,'-B',str(B/'verify_fl20_latency.py'),str(out/'verification/candidate.json'),str(out/'verification/NATIVE_LATENCY_AND_BLOCKS.json')],check=True)
# Only the actual FLP-construction section is needed for this internal base.
# It preserves all six long note blocks, routes and actual Diva chunk bytes.
script=B/'finalize_fl20_kit.py';prefix=script.read_text().split('\nref,_=sf.read')[0];sys.argv=[str(script),str(out),'Diva_NATIVE_17_WIP'];exec(compile(prefix,str(script)+'-project-only','exec'),{})
for name in ['README_RU.md','FL_STUDIO_RU.md','SHA256SUMS.txt']:(out/name).write_text('Internal native base for the actual combined ZL chain; public kit guide replaces this file.\n')
subprocess.run([sys.executable,'-B','/tmp/divalead-native-effects/verify_fst_with_pyflp.py',str(out)],check=True)
choice.update(native_base=json.loads((out/'verification/candidate.json').read_text()),native_base_export_directory=str(out),native_parameters_changed=True,not_compatible_with_standard_x95_exporter=True,native_base_prepared_for_actual_combined_export=True)
ready=out.with_name(out.name+'-COMBINED_CANDIDATE_READY.json');ready.write_text(json.dumps(choice,indent=2)+'\n');print('NEW_NATIVE_BASE_FOR_COMBINED_ZL_READY',ready,flush=True)
