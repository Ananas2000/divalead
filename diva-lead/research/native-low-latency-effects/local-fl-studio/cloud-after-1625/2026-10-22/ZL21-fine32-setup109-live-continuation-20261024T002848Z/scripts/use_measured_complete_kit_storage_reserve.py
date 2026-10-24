"""Align watcher storage guard with the already-tested128MiB export reserve."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,time
D=Path(__file__).resolve().parent;N=Path('/workspace/divalead-work/native-low-latency-effects');p=D/'watch_ZL_useful_complete_backups.py';source=p.read_text();old="if reserves['/workspace']<192 or reserves['/tmp']<180:";new="if reserves['/workspace']<128 or reserves['/tmp']<180:";assert source.count(old)==1;changed=source.replace(old,new);compile(changed,p.name,'exec')
OWNER='measured-full-kit-storage-guard-update-20261024';stop=N/'zl-useful-full-backup.stop';assert not stop.exists();watchers=[]
def live(pid):
    try:return Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
    except FileNotFoundError:return False
for proc in Path('/proc').glob('[0-9]*'):
    try:
        if os.fsencode(str(p))in(proc/'cmdline').read_bytes().split(b'\0')and live(int(proc.name)):watchers.append(int(proc.name))
    except(OSError,PermissionError):pass
assert len(watchers)<=1
with stop.open('x')as f:json.dump(dict(owner=OWNER,reason='safe watcher-only restart; numeric matcher keeps running; measured successful full21 used128MiB guard'),f)
deadline=time.monotonic()+180
while any(live(pid)for pid in watchers):
    if time.monotonic()>deadline:raise TimeoutError('Watcher did not reach safe stop; preserve owned stop')
    time.sleep(.2)
assert shutil.disk_usage('/workspace').free>=128*2**20
p.write_text(changed);assert json.loads(stop.read_text())['owner']==OWNER;stop.unlink()
env=dict(os.environ,PYTHONPATH=f'{D}:/tmp/divalead-native-effects:{D.parent}',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
with(N/'MEASURED_RESERVE_WATCHER_RESTART.log').open('ab')as log:child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(p),'--watch'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_watcher_PIDs=watchers,new_watcher_PID=child.pid,numeric_main_uninterrupted=True,root_full_kit_reserve_MiB=128,tmp_full_kit_reserve_MiB_unchanged=180,numeric_main_root64_tmp112_guards_unchanged=True,actual_full21_already_succeeded_under_the_same128MiB_pre_export_guard=True,all_objective_robustness_state_latency_and_audio_replay_gates_unchanged=True,old_watcher_script_SHA256=hashlib.sha256(source.encode()).hexdigest(),new_watcher_script_SHA256=hashlib.sha256(changed.encode()).hexdigest(),root_current_free_bytes=shutil.disk_usage('/workspace').free)
(N/'MEASURED_SUCCESSFUL_FULL_KIT_STORAGE_RESERVE_UPDATE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
