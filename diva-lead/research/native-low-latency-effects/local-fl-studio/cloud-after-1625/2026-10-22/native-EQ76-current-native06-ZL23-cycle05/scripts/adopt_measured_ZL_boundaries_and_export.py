"""Publish a complete tested kit before adopting the expanded physical ranges."""
from pathlib import Path
import ast,datetime,json,os,runpy,shutil,struct,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent;N=Path('/workspace/divalead-work/native-low-latency-effects');STUDY=D/'ZL-measured-boundary-expansion-after21-01';ROOT=D/'ZL-measured-boundary-supported-adoption-01';ROOT.mkdir(exist_ok=False)
OWNER='ZL-measured-boundary-finite-study-20261024'
def read(p):return json.loads(Path(p).read_text())
for name in ['zl-continuation.stop','zl-useful-full-backup.stop']:assert read(N/name)['owner']==OWNER
pid=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json')['owner']['PID'];proc=Path('/proc')/str(pid);assert not proc.exists()or(proc/'stat').read_text().split()[2]=='Z'
summary=read(STUDY/'completion.json');assert summary['robust_improvement']and len(summary['captures'])==12
prior=read(D/'ZL-continuous65/BEST_CANDIDATE.json');assert Path(prior['native_ZL_component_state']).read_bytes()==(STUDY/'INITIAL_COMPONENT.bin').read_bytes()
proposal=read(STUDY/'CANDIDATE_RESEARCH_ONLY.json');main=D/'continue_ZL_matching.py';old=main.read_text();updated=old.replace('.12,.15,8,True','.12,.15,25,True').replace("('Gain','gain',.25,-15,15,False)","('Gain','gain',.25,-30,30,False)").replace("('Target Gain','target_gain',.4,-20,15,False)","('Target Gain','target_gain',.4,-30,30,False)")
assert updated!=old;compile(updated,main.name,'exec');(ROOT/'original_main_search_bounds.py').write_text(old);(ROOT/'proposed_main_measured_bounds.py').write_text(updated)
tree=ast.parse(updated);function=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='specs_from_component');namespace=dict(Path=Path,ET=ET,struct=struct);exec(compile(ast.Module(body=[function],type_ignores=[]),'actual_measured_parameter_specs','exec'),namespace);specs,dynamic=namespace['specs_from_component'](proposal['native_ZL_component_state']);assert len(specs)==87 and len(dynamic)==6
assert all(p['lo']-1e-5<=p['value']<=p['hi']+1e-5 for p in specs)
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='publish_measured_real_plugin_boundaries');code=f"{max(int(p.name[-2:])for p in h['PUBLIC'].glob('ZL-WIP[0-9][0-9]'))+1:02}"
h['build'](code,candidate=str(STUDY/'CANDIDATE_RESEARCH_ONLY.json'));kit=D.parent/f'FL20_ZL_{code}_WIP';report=read(kit/'verification/ZL_FULL_VERIFICATION.json');proof=read(kit/'verification/ZIP_ACTUAL_REPLAY_PROOF.json')
assert report['mean_original_objective']<summary['current_control_mean']-.0005
assert proof['six_fresh_whole_chain_mean']<summary['current_control_mean']-.0005
main.write_text(updated)
try:h['publish'](code)
except BaseException:main.write_text(old);raise
chosen=read(D/f'ZL-auto-export-input-{code}/candidate-research-only.json');chosen.update(accepted_full_public_kit='ZL'+code,measured_Q25_gain_target30_search_space=True,physical_UI_boundaries_measured_before_search=True,all_original_quality_and_state_replay_gates_unchanged=True)
tmp=D/'ZL-continuous65/BEST_CANDIDATE.partial';tmp.write_text(json.dumps(chosen,indent=2)+'\n');tmp.replace(D/'ZL-continuous65/BEST_CANDIDATE.json')
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),full_user_kit='ZL'+code,native_base='05 unchanged',paired12_control=summary['current_control_mean'],paired12_candidate=summary['candidate_mean'],paired12_SEM=summary['paired_difference_SEM'],full_export_mean=report['mean_original_objective'],ZIP_mean=proof['six_fresh_whole_chain_mean'],search_Q_max=25,search_dynamic_gain_and_target_bounds=[-30,30],all_original_audio_objective_and_robustness_gates_unchanged=True,source_Diva_and_three_held_notes_unchanged=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
(ROOT/'ADOPTED_AFTER_ACTUAL_FULL_ZIP_AND_PUSH.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'ZL_MEASURED_BOUNDARIES_FULL_KIT_ADOPTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('MEASURED_PHYSICAL_RANGES_ADOPTED_AFTER_FULL_EXPORT',json.dumps(receipt),flush=True)
