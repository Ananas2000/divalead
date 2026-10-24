"""Finalize the tested kit's current metadata and add a real-GUI-input A/B."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,zipfile
import numpy as np,soundfile as sf
A=Path(__file__).resolve().parent;ROOT=A/'FL20_ZL24_STEREO_WIP';V=A/'frozen-stereo-validation01';verification=ROOT/'verification'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(A/'final-kit24-assessment')
from fl20_objective import a
source=sf.read(V/'NEW_NATIVE_CANDIDATE_00.wav',dtype='float32',always_2d=True)[0];sf.write(verification/'NATIVE_WITH_TAIL_WIP.wav',source,48000,subtype='FLOAT')
prior=json.loads((A/'cloud476-GUI-recheck/CLOUD476_PRIOR_VALIDATION.json').read_text());summary=json.loads((V/'NEW_NATIVE_SUMMARY.json').read_text());reg=float(np.sum(np.array(prior['native_base']['x'])[:28]**2))*.00000025
candidate=dict(prior,native_ZL_component_state=str(verification/'ZL24_PRIMARY_COMPONENT.bin'),primary_ZL_component_state=str(verification/'ZL24_PRIMARY_COMPONENT.bin'),post_ZL_component_state=str(verification/'ZL24_POST_COMPONENT.bin'),requires_two_ZL_instances=True,not_compatible_with_single_ZL_pipeline=True,topology='native12 -> primary ZL -> post ZL Side-AllPass10000Hz/Q2 and2200Hz/Q4',loss=float(np.mean([r['candidate']['loss']for r in summary['pairs'][:6]]))+reg,recorded_audio=str(ROOT/'ZL24_STEREO_FULL_WIP.wav'),native_base_export_directory='/tmp/divalead-local-1625/FL20_NATIVE_ZL_REBASED_06',actual_FL_GUI_validation_pending=True,reference_match_reached=False,not_adopted_until_publication=True)
p=verification/'candidate.json'
if p.exists():p.rename(verification/'historical_single_ZL_candidate.json')
p.write_text(json.dumps(candidate,indent=2)+'\n')
ref,sr=sf.read(ROOT/'Diva_original_lead_reference.wav',always_2d=True);old,_=sf.read(V/'ARCHIVAL_GUI_CONTROL_00.wav',always_2d=True);new,_=sf.read(V/'ARCHIVAL_GUI_CANDIDATE_00.wav',always_2d=True)
edit=lambda y:a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));old=edit(old);new_edit=edit(new);rms=lambda y:float(np.sqrt(np.mean(y*y)));gains=[1.,rms(ref)/rms(old),rms(ref)/rms(new_edit)];gap=np.zeros((24000,2));ab=np.concatenate([ref,gap,old*gains[1],gap,new_edit*gains[2]]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
sf.write(ROOT/'GUI_INPUT_PROCESSED_STEREO24_WIP.wav',new,48000,subtype='FLOAT');sf.write(ROOT/'AB_ORIGINAL_GUI_INPUT_ZL23_ZL24_STEREO_WIP.flac',ab,48000,subtype='PCM_24');working=A/'AB_GUI24_working.wav';sf.write(working,ab,48000,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(working),'-codec:a','libmp3lame','-b:a','320k',str(ROOT/'AB_ORIGINAL_GUI_INPUT_ZL23_ZL24_STEREO_WIP.mp3')],check=True);working.unlink()
(verification/'GUI_INPUT_AB_LEVELS.json').write_text(json.dumps(dict(order=['original','previous_confirmed_ZL23_on_archival_GUI_input00','new_ZL24_on_the_same_GUI_input00'],starts_seconds=[0,4.168,8.336],RMS_gains=gains,common_peak_safety_gain=safety,no_new_GUI_project_export_claim=True,only_AB_level_normalized=True),indent=2)+'\n')
addition='''
Дополнительно AB_ORIGINAL_GUI_INPUT_ZL23_ZL24_STEREO_WIP.mp3/FLAC сравнивает
варианты на ОДНОМ реальном архивном GUIвходе FL26: оригинал0с → ZL23 с4,168с
→ новый с8,336с. Это тот же исходный Diva/native дубль для обоих вариантов;
новый выход получен настоящими ZL VST3. GUI_INPUT_PROCESSED_STEREO24_WIP.wav
содержит полный ненормализованный результат этого входа. Основной6-секундный
WAV отдельно получен из нового nativeрендера на сохранённом Divaисточнике.
Все варианты промежуточные, нового GUIэкспорта проекта ещё нет.
'''
for name in ['FL_STUDIO_RU.md','README_RU.md']:
 p=ROOT/name;p.write_text(p.read_text()+addition)
zip_path=A/'Diva_ZL24_STEREO_WIP_complete.zip'
def pack():
 (ROOT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n'for p in sorted(ROOT.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
 with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(ROOT.rglob('*')):
   if p.is_file():z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
pack()
with zipfile.ZipFile(zip_path)as z:
 assert z.testzip()is None
 for p in ROOT.rglob('*'):
  if p.is_file():assert z.read(ROOT.name+'/'+p.relative_to(ROOT).as_posix())==p.read_bytes()
 for name in ['ZL24_PRIMARY_COMPONENT.bin','ZL24_POST_COMPONENT.bin']:
  assert z.read(ROOT.name+'/verification/'+name)==(verification/name).read_bytes()
 old_proof=json.loads(z.read(ROOT.name+'/verification/ZIP_ACTUAL_REPLAY_PROOF.json'));assert max(old_proof['whole_chain_fixed_native_input_replay_max_abs_errors'])==0
completion=dict(root=str(ROOT),ZIP=str(zip_path),ZIP_bytes=zip_path.stat().st_size,ZIP_SHA256=hashlib.sha256(zip_path.read_bytes()).hexdigest(),final_ZIP_all_member_bytes_CRC_and_SHA_verified=True,tested_actual_DSP_states_unchanged_after_metadata_finalization=True,mean_new_native_original_objective_with_regularizer=candidate['loss'],constant_native_EQ_regularizer=reg,only_three_held_notes=True,requires_two_ZL_instances=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
(A/'ZL24_FINAL_BUILD_COMPLETION.json').write_text(json.dumps(completion,indent=2)+'\n');print(json.dumps(completion),flush=True)
