"""Preserve full negative NEW12, reusing only exact WAVs in verified fixed snapshot."""
from pathlib import Path
import hashlib,json,runpy,shutil,subprocess
V=Path(__file__).resolve().parent;R=Path('/tmp/divalead-native12-Diva-cutoff144p04-primary94-20261104');O=V.parent/'stereo-refinement-20261025';P=Path('/workspace/divalead');receipt=json.loads((V/'SOURCE_CUTOFF_FIXED_LIVE_PUBLICATION.json').read_text());assert receipt['all_retained_study_files_and_WAVs_remote_Git_verified'];fixed=P/receipt['public_path'];manifest=fixed/'ARCHIVE_MEMBER_SHA256.json';h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='exact_fixed_source_cutoff_WAV_reuse');assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+receipt['commit']+'/'+manifest.relative_to(P).as_posix())==manifest.read_bytes();lookup={r['name']:r for r in json.loads(manifest.read_text())};reused=[]
for p in R.rglob('*.wav'):
 name=p.relative_to(R).as_posix()
 if name in lookup:
  row=lookup[name];assert p.stat().st_size==row['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256'];reused.append(dict(name=name,bytes=row['bytes'],SHA256=row['SHA256']))
assert len(reused)>=20;s=json.loads((R/'completion.json').read_text());assert not s['robust_improvement']and s['training_cases']==849 and len(s['archive_members'])==60
proof=dict(fixed_publication_commit=receipt['commit'],fixed_public_path=receipt['public_path'],all_reused_actual_WAVs_remote_already_verified=True,rows=reused,restore_fixed_snapshot_and_completed_archive_into_same_original_study_root=True,all60_NEW12_native_control_anchor_candidate_WAVs_in_completed_archive=True,source_input_f32_recreate_from_fixed_source_padding_recipe=True)
(R/'REUSED_REMOTE_FIXED_TRAINING_WAVS.json').write_text(json.dumps(proof,indent=2)+'\n');(V/'SOURCE_CUTOFF_COMPLETED_REUSE_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
for row in reused:(R/row['name']).unlink()
code=R/'replay-code';code.mkdir()
for name in ['study_source_cutoff_primary94_native12.py','source_cutoff_primary94_support.py','prepare_source_cutoff_primary94_study.py','fl20_curve.py','backup_completed_source_cutoff94.py']:shutil.copyfile(V/name,code/name)
for name in ['checked_mean_three_real_primary_fit.py','normal_staged_primary_fit.py']:shutil.copyfile(V.parent/'stereo-refinement-20261026'/name,code/name)
shutil.copyfile(V.parent/'pc-stereo-20261024/native_post_trim.py',code/'native_post_trim.py')
label='original-native12-source-cutoff-primary94-849cases-NEW12-negative-20261104';subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(O/'backup_complete_finite_study.py'),'--root',str(R),'--label',label,'--note','Source only VCF144.04 plus refitted PRIMARY94,849 cases/2547 actual DSP; unseen barely+.0003746, full NEW12 worsened mean and Air, rejected. All60 NEW WAVs here; all20 fixed training/control/anchor/source WAVs reused only after exact memberSHA in snapshot384a7d54; all data lossless ordinaryGit, not adopted'],check=True);out=json.loads((O/(label+'_PUBLICATION.json')).read_text());assert out['all_retained_study_files_and_WAVs_remote_Git_verified'];(V/'SOURCE_CUTOFF_COMPLETE_PUBLICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='evicted_private_copies'}),flush=True)
