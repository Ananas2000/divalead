from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
P=Path('/workspace/divalead');N=Path('/workspace/divalead-work/native-low-latency-effects');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');W=Path('/tmp/divalead-native-effects');pub=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip();assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=P,text=True).split()[0]==head
open_paths=set()
for p in Path('/proc').glob('[0-9]*'):
 try:
  for f in(p/'fd').iterdir():
   try:open_paths.add(os.readlink(f))
   except OSError:pass
 except OSError:pass
before={p:shutil.disk_usage(p).free for p in ['/workspace','/tmp']};removed=[]
for local,remote in [('ZL-native-EQ76-after-ZL08-01','native-EQ76-with-ZL-after08'),('ZL-native-WS16-after-EQ76-01','native-WS16-with-ZL-afterEQ76')]:
 root=D/local;assert json.loads((root/'completion.json').read_text())['robust_improvement']
 for p in [root/'TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz',*root.glob('prefix-*.wav')]:
  q=pub/remote/p.name
  if not p.exists():continue
  assert str(p)not in open_paths and q.is_file()and p.read_bytes()==q.read_bytes();digest=hashlib.sha256(p.read_bytes()).hexdigest();removed.append(dict(path=str(p),reason='byte-exact committed remote-backed duplicate',git_path=q.relative_to(P).as_posix(),SHA256=digest));p.unlink()
 # These are disposable score-edit files, not frozen training inputs or selected WAVs.
 for p in(root/'assessment').glob('fl20-worker-*.wav'):
  assert str(p)not in open_paths;removed.append(dict(path=str(p),reason='completed analysis edit scratch, scores and full native render proofs retained',bytes=p.stat().st_size));p.unlink()
for prefix in ['ZL-native-EQ76-real-VST3-','ZL-native-WS16-real-VST3-']:
 for p in D.glob(prefix+'*.f32'):
  assert str(p)not in open_paths;removed.append(dict(path=str(p),reason='closed completed study real-plugin IO scratch',bytes=p.stat().st_size));p.unlink()
for prefix in ['ZL-native-EQ76-worker-','ZL-native-WS16-worker-']:
 for p in W.glob(prefix+'*-render.wav'):
  assert str(p)not in open_paths;removed.append(dict(path=str(p),reason='completed render IO scratch; selected WAVs and all paired captures remain on Git',bytes=p.stat().st_size));p.unlink()
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),remote_commit=head,before=before,after={p:shutil.disk_usage(p).free for p in before},removed=removed,latest_kit_Diva_source_current_native_base_component_and_selected_WAVs_preserved=True,restore='git show <remote_commit>:<git_path> > <path> for byte-exact archived study inputs and WAVs')
(N/'COMPLETED_NATIVE_STUDY_DUPLICATE_CLEANUP.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(removed=len(removed),before=before,after=receipt['after']),indent=2))
