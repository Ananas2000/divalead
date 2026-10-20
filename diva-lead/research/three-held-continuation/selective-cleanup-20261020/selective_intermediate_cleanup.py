"""User-authorized selective cleanup; preserve every numbered release and current proofs."""
from pathlib import Path
import collections,datetime,fcntl,hashlib,json,os,shutil,subprocess
R=Path(__file__).resolve().parent; B=R.parent; P=Path('/workspace/divalead')
OWNER='user-authorized-selective-cleanup-20261020'
assert json.loads((R/'auto-backup.pause').read_text())['owner']==OWNER
lock=(R/'auto-backup-Git.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert not subprocess.check_output(['git','status','--porcelain'],cwd=P,text=True)
HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
 return h.hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),authorization='User explicitly requested only unnecessary intermediate variants, not all versions.',prior_commit=HEAD,all_numbered_releases_preserved=True,subjective_audition_performed=False,match_reached=False,root_free_before=shutil.disk_usage(P).free,actions=[],pruned_already_published_private_proof_names=[])
protected=[P/'Diva_lead_v69_WIP_checkpoint.zip',P/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json',R/'baseline/validation.json',R/'source-pw5190-basis/Diva_source.wav',R/'pw5190-verified-live-main-0005-hf/validation.json']
protected_hashes={str(p):sha(p) for p in protected}
out=P/'diva-lead/research/three-held-continuation/selective-cleanup-20261020';out.mkdir(exist_ok=False)
# Repeated publication of exactly the same winner: keep the latest snapshot.
auto=P/'diva-lead/research/three-held-continuation/after-v64/auto-checkpoints'
groups=collections.defaultdict(list)
for f in sorted(auto.glob('*/checkpoint.json')):
 d=json.loads(f.read_text());groups[(d['source_family'],d['private_full_proof'])].append(f.parent)
for paths in groups.values():
 for old in paths[:-1]:
  newest=paths[-1]
  assert (old/'proof/analysis/spectral_model.json').read_bytes()==(newest/'proof/analysis/spectral_model.json').read_bytes()
  for f in old.rglob('validation.json'):
   if (f.parent/'arbitrary-input-verification.json').exists():
    try:report['pruned_already_published_private_proof_names'].append(Path(json.loads(f.read_text())['core_model']).parent.parent.name)
    except KeyError:pass
  files=[p for p in old.rglob('*') if p.is_file() and not p.is_symlink()]
  report['actions'].append(dict(path=str(old),reason='Repeated backup of the exact same winning model; newer complete snapshot retained.',retained=str(newest),logical_bytes=sum(p.stat().st_size for p in files),files=len(files)))
  shutil.rmtree(old)
# Build verification scratch is redundant with the retained complete release.
for old in sorted(R.glob('v*-build')):
 version=old.name.removesuffix('-build');kit=P/'diva-lead'/(version+'-wip')
 assert kit.is_dir()
 archive=P/('Diva_lead_'+version+'_WIP_checkpoint.zip')
 assert archive.exists()
 local=old/(version+'-wip')
 for f in local.rglob('*'):
  if f.is_file():assert sha(f)==sha(kit/f.relative_to(local)),str(f)
 logdir=out/'retained-build-receipts'/version;logdir.mkdir(parents=True)
 for f in old.iterdir():
  if f.is_file() and f.suffix in ['.json','.log']:shutil.copyfile(f,logdir/f.name)
 files=[p for p in old.rglob('*') if p.is_file() and not p.is_symlink()]
 report['actions'].append(dict(path=str(old),reason='Completed build scratch; byte-identical numbered kit and ZIP retained, verification receipts copied.',retained=str(kit),logical_bytes=sum(p.stat().st_size for p in files),files=len(files)))
 shutil.rmtree(old)
# Historical sixteen-note selection cache: only the worst score tier (>=0.9)
# is pruned; keep the best 780-ish controls, every model and every score receipt.
cache=B/'all-repository-selection/validated-snapshots'
for f in sorted(cache.glob('*/validation.json')):
 d=json.loads(f.read_text());score=d.get('fresh_carrier_score',d.get('score'))
 if score is None or score<.9:continue
 removed=[]
 for p in f.parent.rglob('*'):
  if p.is_file() and not p.is_symlink() and p.suffix.lower() in ['.wav','.so','.dll','.exe']:
   removed.append(dict(relative_path=str(p.relative_to(f.parent)),bytes=p.stat().st_size,SHA256=sha(p)));p.unlink()
 if removed:report['actions'].append(dict(path=str(f.parent),reason='Obsolete low-ranked sixteen-note render cache; models, source code, validation and score metadata retained.',historical_standard_score=score,logical_bytes=sum(x['bytes'] for x in removed),removed_generated_files=removed))
report['pruned_already_published_private_proof_names']=sorted(set(report['pruned_already_published_private_proof_names']))
report['root_free_after']=shutil.disk_usage(P).free;report['actual_root_bytes_recovered']=report['root_free_after']-report['root_free_before']
assert all(sha(Path(p))==s for p,s in protected_hashes.items())
report['protected_hashes_unchanged']=protected_hashes
save(out/'manifest.json',report);save(R/'selective-cleanup-result.json',report)
rows=['| Снимок | Источник | Ошибка тембра ↓ |','|---|---|---:|']
for f in sorted(auto.glob('*/checkpoint.json'),reverse=True):
 d=json.loads(f.read_text());n=f.parent.name;rows.append(f"| [{n}]({n}/README.md) | {d['source_family']} | {d['tone_score']:.10f} |")
(auto/'README.md').write_text('# Проверенные промежуточные трёхнотные варианты\n\nПовторные бэкапы идентичного победителя удалены по просьбе пользователя; сохранён последний полный снимок каждого такого варианта. Все номерные комплекты сохранены. Старые снимки доступны в истории Git.\n\nТочное совпадение не достигнуто.\n\n'+'\n'.join(rows)+'\n')
(out/'README_RU.md').write_text('# Выборочная очистка промежуточных данных\n\nСохранены все номерные версии, исходный трёхнотный вариант, лучший полный v69, референс, исходники, все текущие физические проверки и альтернативы с меньшим внегармоническим остатком.\n\nУдалены только повторные исследовательские снимки одного победителя, проверочные каталоги завершённых сборок с сохранёнными полными комплектами и тяжёлые рендеры худшего слоя старого шестнадцатинотного кэша. Модели и оценки этого кэша сохранены. История Git не переписывалась.\n\nФактический объём освобождённого места на основном диске: '+str(report['actual_root_bytes_recovered'])+' байт. Размеры отдельных файлов в manifest.json логические; при жёстких ссылках они не равны освобождённому месту.\n\nТочное совпадение звука ещё не достигнуто; подбор продолжается только на трёх удерживаемых нотах.\n')
print(json.dumps(dict(actions=len(report['actions']),duplicate_snapshots=sum('Repeated backup' in x['reason'] for x in report['actions']),build_scratch=sum('Completed build' in x['reason'] for x in report['actions']),old_weak_render_caches=sum('Obsolete low' in x['reason'] for x in report['actions']),actual_root_bytes_recovered=report['actual_root_bytes_recovered'],free_bytes=report['root_free_after']),indent=2))
