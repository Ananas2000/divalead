"""Verify real progress, remote backup, immutable full kit and saved readiness."""
from pathlib import Path
import os,json,time,subprocess,fcntl,hashlib,datetime
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead')
def snapshot():
    table={}
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            st=(p/'stat').read_text().rsplit(')',1)[1].split();table[int(p.name)]=dict(state=st[0],ppid=int(st[1]),ticks=int(st[11])+int(st[12]),starttime=st[19],cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
        except (FileNotFoundError,ProcessLookupError):pass
    rows={}
    for name in ['continuation-state.json','joint-phase-continuation-state.json','balance-power-continuation-state.json']:
        d=json.loads((R/name).read_text());pid=d['controller_PID']
        if name=='balance-power-continuation-state.json' and table[pid]['state']=='T':
            owners=[q for q,v in table.items() if v['state'] not in ['Z','T'] and v['cmd'].startswith('/workspace/.venvs/divalead/bin/python ') and str(R/'run_pw5190_gain_research.py') in v['cmd']]
            assert len(owners)==1,owners
            owned=json.loads((R/'source-pw5190-gain-control/paused-balance-power.json').read_text())
            assert any(row['PID']==pid and row['starttime_ticks']==table[pid]['starttime'] for row in owned['processes']) and 'resumed_UTC' not in owned
            pid=owners[0];d=dict(d,phase='PW51.90_gain_refinement_in_owned_third_CPU_slot',fit_log=str(R/'pw5190-gain-research/fit.log'))
        assert pid in table and table[pid]['state'] not in ['Z','T'],(name,d)
        ids=[pid]
        for parent in ids:
            ids.extend(p for p,v in table.items() if v['ppid']==parent and p not in ids)
        log=Path(d['fit_log']) if 'fit_log' in d else None
        rows[name]=dict(PID=pid,phase=d['phase'],fit_log=str(log) if log else None,log_bytes=log.stat().st_size if log and log.exists() else 0,subtree_CPU_ticks=sum(table[p]['ticks'] for p in ids if table[p]['state']!='Z'))
    p=json.loads((R/'auto-backup-state.json').read_text());assert p['publisher_PID'] in table and table[p['publisher_PID']]['state'] not in ['Z','T']
    assert not (R/'auto-backup.pause').exists() and p['phase'] not in ['paused_for_manual_Git_work','failed_preserve_all_data_and_diagnose']
    return rows,p
first,p=snapshot();time.sleep(12);second,p=snapshot();progress={}
for name,a in first.items():
    b=second[name];progress[name]=bool(b['subtree_CPU_ticks']>a['subtree_CPU_ticks'] or b['log_bytes']!=a['log_bytes'] or b['fit_log']!=a['fit_log'] or b['phase']!=a['phase'])
    assert progress[name],(name,a,b)
for _ in range(30):
    with (R/'auto-backup-Git.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:pass
        else:
            assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
            head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=REPO,text=True).split()[0]==head
            for path in ['diva-lead/v64-wip','Diva_lead_v64_WIP_checkpoint.zip','diva-lead/v65-wip','Diva_lead_v65_WIP_checkpoint.zip']:
                assert subprocess.check_output(['git','rev-parse','HEAD:'+path],cwd=REPO)==subprocess.check_output(['git','rev-parse','e99d6eaaa9a89207dfef549dd30703bffff0919b:'+path],cwd=REPO)
            break
    time.sleep(2)
else:raise RuntimeError('Could not acquire a stable read interval from publisher')
latest=json.loads((R/'auto-backup-last-public-verification.json').read_text());config=json.loads((R/'config-v65-save-readback.json').read_text());assert config['save_confirmed'] and config['readback_start_skill_exact'] and config['install_script_network_secrets_runtime_requirements_unchanged_exact']
products=[R.parent/'analysis/native_finish.so',R.parent/'analysis/tunable/native_finish.so',R.parent/'analysis/v12-native_finish.so',R.parent/'v17-phase-validation/analysis/native_finish.so'];assert all(x.is_file() and not x.is_symlink() for x in products)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),main=head,clean_worktree_and_remote_main_match=True,full_v64_tree_and_ZIP_immutable=True,full_v65_tree_and_ZIP_immutable=True,actual_numeric_progress=progress,live_services=second,publisher_live_and_resumed=p,latest_real_HTTP_verified_publication=latest,configuration=config,persistent_runtime_libraries_regular=True,match_reached=False)
(R/'LIVE_V65_CONTINUATION_VERIFIED.json').write_text(json.dumps(report,indent=2)+'\n');print('ALL_THREE_NUMERIC_SLOTS_ACTUALLY_ADVANCING_V64_V65_IMMUTABLE_AND_PUBLIC_BACKUPS_VERIFIED',head,latest['tone_score'],flush=True)
