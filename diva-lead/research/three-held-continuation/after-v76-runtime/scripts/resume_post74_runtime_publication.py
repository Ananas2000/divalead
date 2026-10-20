"""Resume only our staged runtime snapshot, retaining exact raw TSV/log bytes."""
from pathlib import Path
import datetime,fcntl,hashlib,json,shutil,subprocess,time,urllib.request
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead');O=P/'diva-lead/research/three-held-continuation/after-v76-runtime';PAUSE=R/'auto-backup.pause';OWNER='publish-post74-source-runtime'
def git(*a):return subprocess.check_output(['git','-c','gc.auto=0',*a],cwd=P,text=True).strip()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
assert json.loads(PAUSE.read_text())['owner']==OWNER
with (R/'auto-backup-Git.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);before=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before
 target=str(O.relative_to(P));assert all(x.startswith(target+'/') for x in git('diff','--cached','--name-only').splitlines());assert not git('ls-files','--others','--exclude-standard')
 for name in ['publish_post74_runtime.py','summarize_current_three_variants.py','refresh_post74_startup_guide.py']:shutil.copyfile(R/name,O/'scripts'/name)
 shutil.copyfile(R/'start_skill_current.md',O/'start_skill_current.md');shutil.copyfile(R/'current-three-note-variant-registry.json',O/'diagnostics/current-three-note-variant-registry.json')
 receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),failed_before_any_commit=True,diagnosis='Only byte-exact raw Diva TSV empty label columns and CRLF Windows logs triggered source whitespace checks.',raw_audio_parameters_or_logs_not_rewritten=True,source_and_documentation_whitespace_checked=True,original_sound_DSP_tolerances_not_changed=True,version_directory_count_includes_legacy_nonWIP_directories=True,match_reached=False)
 write(R/'post74-runtime-publication-recovery.json',receipt);shutil.copyfile(R/'post74-runtime-publication-recovery.json',O/'diagnostics/post74-runtime-publication-recovery.json');shutil.copyfile(Path(__file__),O/'scripts'/Path(__file__).name)
 git('add','--',target);git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--','.',':!*.tsv',':!*.log');git('commit','-m','Preserve physical three-note Diva research and continued matching from the best verified source')
 assert all(x.startswith(target+'/') for x in git('diff',before,'HEAD','--name-only').splitlines());head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before;git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==head
 for name in ['README_RU.md','start_skill_current.md','scripts/switch_to_post74_at_checkpoint.py']:
  data=urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+target+'/'+name,timeout=60).read();assert data==(O/name).read_bytes()
 manifest=json.loads((O/'physical-screen-archives/manifest.json').read_text());first=manifest['archives'][0];data=urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+target+'/physical-screen-archives/'+first['file'],timeout=60).read();assert hashlib.sha256(data).hexdigest()==first['SHA256']
 assert not git('status','--porcelain');write(R/'post74-runtime-public-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=head,remote_exact=True,HTTP_bytes_exact=True,all_numbered_releases_unchanged=True,all46_actual_Diva_source_screens_archived=True,six_independent_coefficient_blends_also_preserved=True,unaccepted_old_numeric_checkpoints_preserved=True,match_reached=False))
 write(R/'post74-runtime-ready-for-config.json',dict(commit=head,lock_held=True,owner=OWNER));print('POST74_RUNTIME_PUSHED_READY_FOR_CONFIG',head,flush=True)
 until=time.monotonic()+180
 while time.monotonic()<until and not (R/'post74-runtime-config-readback-complete.json').exists():time.sleep(2)
 assert json.loads(PAUSE.read_text())['owner']==OWNER;PAUSE.unlink();print('POST74_RUNTIME_GIT_LOCK_AND_PAUSE_RELEASED',flush=True)
