from pathlib import Path
import json,os,subprocess,sys,time
H=Path(__file__).resolve().parent;N=H.parent/'native-low-latency-effects';state=N/'ORIGINAL_PRIMARY_ANCHORED_AIR_MEAN3_372_STUDY.json';s=json.loads(state.read_text());pid=s['PID'];proc=Path('/proc')/str(pid);root=Path(s['root']);assert root==H/'PRIMARY_ANCHORED_AIR_MEAN3_372'
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
args=[sys.executable,'-B',str(H.parent/'stereo-refinement-20261025/backup_complete_finite_study.py'),'--root',str(root),'--label','original-primary-cumulative-Air-anchor37-on372-negative','--note','Отдельный новыйPRIMARY94 подбор с актуальной372 и фиксированным POST37, sourceDiva281/3длинные/ARP/ADSR/native12/trim неизменны.849предложений, каждый поТРИ COMMONреальных nativeвхода, дваunseen. Здесьnoiseограничен кПОЛНОМУ37,не только предыдущемушагу: trainingAiranchor37+.005, финал требовалоба372И37 first6AND10/cold2/Air+.02. Последняяточкабылявнохуже372 наheldout(mean-.0042696), поэтомунепрошлаscreen иНЕпринята, новыйfull38необъявлялся. Все сохраненные actualnative/control372/anchor37/selectedWAV/state/метрики/код архивированы.372остаётсяпоследнимпринятымnumeric, полного совпадения нет.']
if positive:args.append('--retain-local-audio')
subprocess.run(args,check=True)
