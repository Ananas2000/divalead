from pathlib import Path
import json,os,subprocess,sys,time
H=Path(__file__).resolve().parent;N=H.parent/'native-low-latency-effects';state=N/'ORIGINAL_DIVA_SYNC_TUNE2_MEAN3_COADAPT36_STUDY.json';s=json.loads(state.read_text());pid=s['PID'];proc=Path('/proc')/str(pid);root=Path(s['root']);assert root==H/'DIVA_SYNC_TUNE2_MEAN3_COADAPT36'
try:start=(proc/'stat').read_text().split()[21]
except FileNotFoundError:start=None
deadline=time.monotonic()+7200
while start is not None:
 try:
  v=(proc/'stat').read_text().split()
  if v[21]!=start or v[2]=='Z':break
 except FileNotFoundError:break
 if time.monotonic()>deadline:raise TimeoutError('Still actual DSP; no false completed archive')
 time.sleep(.5)
done=root/'completion.json';positive=False
if done.exists():positive=json.loads(done.read_text()).get('robust_improvement',False)
else:(root/'INCOMPLETE_FINITE_STUDY_BACKUP.json').write_text(json.dumps(dict(job_ended_without_completion=True,last_controller=json.loads(state.read_text()),not_adopted=True),indent=2)+'\n')
args=[sys.executable,'-B',str(H.parent/'stereo-refinement-20261025/backup_complete_finite_study.py'),'--root',str(root),'--label','original-Diva-sync-Tune2-mean-three-coadapt36','--note','Пять тонких настроек hard-sync slave Tune2, уровень заранее выровнен только к синтетическому исходнику. Каждый вариант PRIMARY94 оценивается на трех отдельных настоящих native/ZL/trim рендерах, без усреднения звука; еще два входа отложены. Три длинные ноты, ARP/ADSR и остальные279 параметров Diva сохранены. Два законченных отрицательных варианта при исправлении записи validationWAV повторно не подбирались; третий перезапущен на тех же пяти frozenWAV, SHA и marker приложены. Только новый first6AND10/cold2/stereo/air может принять точку; требуется полный source/FLP экспорт, до него не принят. Все сохраненные WAV/state/281/MIDI/протоколы и код архивированы.']
if positive:args.append('--retain-local-audio')
subprocess.run(args,check=True)
