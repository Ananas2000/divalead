"""Continue real audio work after the finite94 fit; preserve all completed evidence."""
from pathlib import Path
import datetime,json,os,shutil,subprocess,sys,time
H=Path(__file__).resolve().parent;R=H/'PRIMARY_MEAN3_THREE_SWEEPS_CURRENT404';N=H.parent/'native-low-latency-effects';s=json.loads((N/'ORIGINAL_PRIMARY_MEAN3_THREE_SWEEPS_CURRENT404_STUDY.json').read_text());pid=s['PID'];proc=Path('/proc')/str(pid);start=(proc/'stat').read_text().split()[21];deadline=time.monotonic()+7200
while proc.exists():
 try:
  st=(proc/'stat').read_text().split()
  if st[21]!=start or st[2]=='Z':break
 except FileNotFoundError:break
 if time.monotonic()>deadline:raise TimeoutError('Actual finite94 fit still active; no fake completion')
 time.sleep(.5)
done=json.loads((R/'completion.json').read_text());positive=bool(done.get('robust_improvement'));next_started=False
if not positive:
 assert all((R/f'TRAINING_NATIVE_{k}.wav').is_file()for k in range(5))
 with(H/'PRIMARY106_DETECTOR_JOINT_THREE_SWEEPS404.log').open('w')as log:child=subprocess.Popen([sys.executable,'-B',str(H/'study_PRIMARY106_detector_joint_three_sweeps404.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 nextR=H/'PRIMARY106_DETECTOR_JOINT_THREE_SWEEPS404';limit=time.monotonic()+180
 while not(nextR/'BOTH_HOSTS_NEUTRAL_IDENTITY.json').exists():
  if child.poll()is not None:raise RuntimeError('Next actual106 study ended before neutral proof; preserve previous five native WAVs')
  if time.monotonic()>limit:raise TimeoutError('Next actual106 neutral identity not yet proven; do not evict previous native inputs')
  time.sleep(.5)
 for k in range(5):assert os.path.samefile(R/f'TRAINING_NATIVE_{k}.wav',nextR/f'TRAINING_NATIVE_{k}.wav')
 next_started=True;proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual106_PID=child.pid,exact_same_five_native_inputs_hardlinked=True,both_actual_primary_hosts_neutral_identity=json.loads((nextR/'BOTH_HOSTS_NEUTRAL_IDENTITY.json').read_text()),previous_finite94_closed_negative=True,not_adopted=True,reference_match_reached=False);(H/'ACTUAL106_DETECTOR_JOINT_START_20261028.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
scripts=R/'scripts';scripts.mkdir()
for name in ['study_PRIMARY_mean3_three_sweeps_current404.py','Primary_mean3_three_sweeps_current404_support.py','checked_mean_three_real_primary_fit.py','normal_staged_primary_fit.py','after_mean3_404_launch_detector106_and_backup.py']:shutil.copyfile(H/name,scripts/name)
args=[sys.executable,'-B',str(H.parent/'stereo-refinement-20261025/backup_complete_finite_study.py'),'--root',str(R),'--label','original-primary-mean-three-three-sweeps404','--note','Полный конечный поиск94 PRIMARY-параметров по трём ОБЩИМ реальным native-входам, три прохода, два unseen; звук не усреднялся. Обучающий Air<=контроль, абсолютные stereo148/abs16/lowmid325 и новые first6AND10+2cold гейты сохранены. Перед подбором оба хоста доказали neutral configure против load 0/0; baseline загружается в каждом измерении. Это исследование не принимает состояние автоматически. Все сохранённые реальные WAV/состояния/оценки/код включены. При положительном полном12тесте ещё обязательны latest-context проверка, полный экспорт и независимый replay перед принятием.']
if positive:args.append('--retain-local-audio')
limit=time.monotonic()+1800
while shutil.disk_usage('/workspace').free<96*2**20:
 if time.monotonic()>limit:raise TimeoutError('Preserve completed finite94 study; Git staging reserve not restored')
 time.sleep(.5)
subprocess.run(args,check=True)
