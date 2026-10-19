"""Back up fully proved THREE-held WIP research on main; never claim a match.

Does not fit or publish a new DLL release. The existing numeric controllers run
independently. A pause file and an exclusive lock allow coordinated manual Git
work. Unknown source families, dirty worktrees and remote advances stop writes.
"""
from pathlib import Path
import os,sys,json,hashlib,subprocess,shutil,datetime,time,fcntl,re,urllib.request,traceback,gzip
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ROOT=REPO/'diva-lead/research/three-held-continuation';AUTO=ROOT/'after-v64/auto-checkpoints'
B0=R/'baseline';STATE=R/'auto-backup-state.json';PAUSE=R/'auto-backup.pause';MIN_FREE_MIB=int(os.environ.get('DIVALEAD_BACKUP_MIN_FREE_MIB','192'))
ANCHOR=json.loads((B0/'validation.json').read_text());LIMITS=dict(H24=1.001,upper_harm=1.001,upper_off=1.001,low_harm=1.002,ERB=1.001,relative_phase=1.002,whole=1.001,envelope=1.001,body=1.002,stereo_phase=1.002,stereo_balance=1.002)
TONE=dict(H24=.30,upper_harm=.25,ERB=.20,low_harm=.10,upper_off=.10,relative_phase=.05)
expected_events=json.loads((B0/'MIDI_events_48k.json').read_text());assert len(expected_events)==12 and sum(e[1]==144 for e in expected_events)==6
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.atomic-tmp');q.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');q.replace(p)
def state(phase,**kw):write(STATE,dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),publisher_PID=os.getpid(),phase=phase,only_three_held=True,match_reached=False,**kw))
def git(*args):return subprocess.check_output(['git','-c','gc.auto=0',*args],cwd=REPO,text=True).strip()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source_basis(d):
    if d.get('same_user_selected_Diva_preset_raw_and_all281'):
        return 'original-user-selected-three',B0
    families={'TuneSlop0':('source-tslop0-basis',{'OPT:TSlop':0.0}),
              'PulseWidth51.90':('source-pw5190-basis',{'OSC:PW':51.90})}
    assert d.get('source_family') in families and d.get('same_checked_source_family_raw_and_all281')
    basis,changes=families[d['source_family']]
    assert d['changed_source_fields']==changes
    return d['source_family'],R/basis
def checked(p):
    d=json.loads(p.read_text());family,b=source_basis(d)
    assert d['all_chosen_three_guards_passed'] and d['original_three_held_MIDI_events_unchanged'] and d['all281_source_verified']
    assert d['guard_limits']==LIMITS and not d['match_reached']
    assert d['Windows_native_max_error']<2e-7 and d['full_NEW_SOURCE_independent_max_error']<3e-7 and d['spectral_fixture_max_error']<2e-7
    assert all(d['metrics'][k]<=ANCHOR['metrics'][k]*v for k,v in LIMITS.items())
    assert d['crest_RMS_dB']<=ANCHOR['crest_RMS_dB']*1.001 and d['score']<=ANCHOR['score']*1.0001
    assert Path(d['source_preset']).resolve().is_relative_to(R) and Path(d['new_source_raw']).resolve().is_relative_to(R)
    assert sha(d['source_preset'])==sha(b/'Diva_THREE_HELD_BASELINE.h2p')
    assert sha(d['new_source_raw'])==sha(b/'Diva_source.wav')
    assert sha(d['NEW_independent_prebase'])==sha(b/'NEW-independent-base-pdc.wav')
    assert sha(d['new_source_before_fixture'])==sha(b/'Diva_before_spectral.wav')
    assert (p.parent/'Diva_all281.tsv').read_bytes()==(b/'Diva_all281.tsv').read_bytes()
    events=[list(map(int,s.split()[1:])) for s in (p.parent/'Diva.log').read_text().splitlines() if s.startswith('NOTE ')]
    assert events==expected_events
    cases=json.loads((p.parent/'arbitrary-input-verification.json').read_text())['arbitrary_input_no_MIDI_cases']
    assert len(cases)==12 and {c['sample_rate'] for c in cases}=={44100,48000,96000,192000}
    assert all(c['causal_prefix_equal'] and c['independent_max_error']<2e-10 for c in cases)
    assert np.max(np.abs(sf.read(p.parent/'actual-Windows.wav',dtype='float32')[0]))<.99
    return d,family,b
def choices():
    paths=list(R.glob('verified-*/validation.json'))+list(R.glob('tslop0-verified-*/validation.json'))+list(R.glob('pw5190-verified-*/validation.json'))
    assert paths
    rows=[]
    for p in paths:
        try:rows.append((p,*checked(p)))
        except json.JSONDecodeError:
            if time.time()-p.stat().st_mtime<2:continue
            raise
    return rows
def best_choice():return min(choices(),key=lambda x:x[1]['tone_score'])
def unpublished(rows):
    seen=set()
    for p in ROOT.rglob('validation.json'):
        if not (p.parent/'arbitrary-input-verification.json').exists():continue
        try:seen.add(Path(json.loads(p.read_text())['core_model']).parent.parent.name)
        except (KeyError,ValueError):continue
    return [v for v in rows if v[0].parent.name not in seen]
def copy_immutable(a,b):
    b=Path(b);b.parent.mkdir(parents=True,exist_ok=True)
    try:os.link(a,b)
    except OSError:shutil.copyfile(a,b)
    assert sha(a)==sha(b)
    return str(b)
def snapshot(a,b):
    shutil.copytree(a,b,copy_function=copy_immutable,ignore=lambda d,ns:[n for n in ns if n=='__pycache__' or Path(n).suffix in ['.so','.dll','.exe','.pyc','.tmp','.lock']])
def mirror_temporary_vectors():
    # Numeric-only mirrors remain PRIVATE and are never accepted without proof.
    locations=[]
    for p in (R/'balance-power-continuation').glob('round-*/numeric-location.json'):
        d=json.loads(p.read_text());locations.append((Path(d['numeric_scratch']),p.parent/'numeric-scratch-mirror'))
    locations.append((Path('/tmp/divalead-tslop0-gains'),R/'tslop0-research/numeric-scratch-mirror'))
    for p in (R/'pw5190-research').glob('**/numeric-location.json'):
        d=json.loads(p.read_text());locations.append((Path(d['numeric_scratch']),p.parent/'numeric-scratch-mirror'))
    for p in (R/'pw5190-gain-research').glob('**/numeric-location.json'):
        d=json.loads(p.read_text());locations.append((Path(d['numeric_scratch']),p.parent/'numeric-scratch-mirror'))
    for p in (R/'pw5190-coupled135-research').glob('**/numeric-location.json'):
        d=json.loads(p.read_text());locations.append((Path(d['numeric_scratch']),p.parent/'numeric-scratch-mirror'))
    for p in (R/'pw5190-gain-interior-allguards').glob('**/numeric-location.json'):
        d=json.loads(p.read_text());locations.append((Path(d['numeric_scratch']),p.parent/'numeric-scratch-mirror'))
    for scratch,dest in locations:
        if not scratch.exists():continue
        for name in ['best.json','latest_center.json','optimizer.json','cache_checks.json']:
            for p in scratch.glob('*/'+name):
                try:content=p.read_text();json.loads(content)
                except (FileNotFoundError,json.JSONDecodeError):continue
                out=dest/p.parent.name/p.name;out.parent.mkdir(parents=True,exist_ok=True)
                if out.exists() and out.read_text()==content:continue
                q=out.with_suffix('.mirror-tmp');q.write_text(content);q.replace(out)
def numeric_run(p):
    name=p.parent.name
    if name.startswith('tslop0-verified-gain-'):return R/'tslop0-research'
    if name=='pw5190-verified-balance-0001':return R/'pw5190-research'
    if name=='pw5190-verified-gain-0001':return R/'pw5190-gain-research'
    if name=='pw5190-verified-coupled135-0001':return R/'pw5190-coupled135-research'
    if name=='pw5190-verified-gain-interior-0001':return R/'pw5190-gain-interior-allguards'
    for pattern,folder in [(r'verified-cont-(\d+)-(hf|gain)$','continuation'),(r'verified-joint-phase-(\d+)-(phase18|fine55)$','joint-phase-continuation'),(r'verified-balance-power-(\d+)-(balance42|power69)$','balance-power-continuation')]:
        m=re.fullmatch(pattern,name)
        if m:return R/folder/('round-'+m[1]+'-'+m[2])
    return None
def export_numeric(p,dest):
    run=numeric_run(p)
    if run is None:return
    scratch=Path('/tmp/divalead-tslop0-gains') if run.name=='tslop0-research' else (Path(json.loads((run/'numeric-location.json').read_text())['numeric_scratch']) if (run/'numeric-location.json').exists() else run/'numeric')
    assert any(scratch.rglob('optimizer.json'))
    snapshot(run,dest)
    if not scratch.is_relative_to(run):snapshot(scratch,dest/'numeric')
    archived=[]
    for row in json.loads((R.parent/'history-lossless-archive.json').read_text())['files']:
        old=Path(row['path'])
        if old.exists():continue
        for source,out in [(run,dest),(scratch,dest/'numeric')]:
            if old.is_relative_to(source):
                data=gzip.decompress(Path(row['gzip']).read_bytes());assert hashlib.sha256(data).hexdigest()==row['SHA256']
                q=out/(str(old.relative_to(source))+'.gz')
                if not q.exists():copy_immutable(Path(row['gzip']),q)
                archived.append(dict(path=str(q.relative_to(dest))[:-3],gzip=str(q.relative_to(dest)),SHA256=row['SHA256']));break
    # Compress only this NEW export; the private fitting data and keeper ledger
    # remain untouched. Verify the original JSON bytes before dropping its alias.
    for h in dest.rglob('history.json'):
        if h.stat().st_size<65536:continue
        data=h.read_bytes();q=h.with_name(h.name+'.gz')
        if not q.exists():q.write_bytes(gzip.compress(data,compresslevel=6,mtime=0))
        assert gzip.decompress(q.read_bytes())==data
        archived.append(dict(path=str(h.relative_to(dest)),gzip=str(q.relative_to(dest)),SHA256=hashlib.sha256(data).hexdigest()))
        h.unlink()
    write(dest/'archived-numeric-journals.json',archived)
PORTABLE_VERIFY='''from pathlib import Path
import sys,json,numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;A=R/'proof/analysis';sys.path.insert(0,str(A))
from independent_spectral_ms import spectral_ms
c=json.loads((A/'spectral_model.json').read_text());actual=sf.read(R/'proof/actual-Windows.wav')[0];raw=sf.read(R/'source-base/Diva_source.wav')[0]
kw=dict(sigma=c['mask_sigma'],key_quadratic=c['key_quadratic'],key_slopes=c['key_slopes'],phase_angles=c['common_phase_radians'],hf_parameters=c['hf_matrix_parameters'],hf_anchors=c['hf_matrix_anchors_Hz'],upper_rolloff=c['upper_rolloff_Hz'],harmonic_gain=c['harmonic_gain_parameters'],gain_orders=c['harmonic_gain_orders'],hf_sigma=c['hf_mask_sigma'],phase_key_slopes=c['common_phase_key_slopes'],phase_key_quadratic=c['common_phase_key_quadratic'],core_anchors=c['anchors_Hz'],adaptive_dynamic=c['dynamic_harmonic_parameters'],adaptive_stereo=c['stereo_harmonic_parameters'],final_stereo_balance=c['final_stereo_balance'],fine_phase=c['fine_phase_harmonic_parameters'])
errors={}
for n,tol in [('NEW-independent-base-pdc.wav',3e-7),('Diva_before_spectral.wav',2e-7)]:
 y,extra=spectral_ms(sf.read(R/'source-base'/n)[0],raw,48000,8320,c['parameters'],**kw);error=float(np.max(np.abs(actual[extra:]-y[:-extra])));assert error<tol;errors[n]=error
for line in (R/'SHA256SUMS.txt').read_text().splitlines():
 import hashlib
 sha,name=line.split('  ',1);assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,name
print(json.dumps(dict(full_matching_own_NEW_and_fixture_pass=True,errors=errors,match_reached=False)))
'''
def publish(p,d,family,b,extra_proofs=()):
    assert not git('status','--porcelain'), 'Manual changes/untracked files present; preserve and pause publisher'
    parent=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent,'Remote main advanced; preserve local state'
    old_tree=git('rev-parse','HEAD:diva-lead/v64-wip');old_zip=git('rev-parse','HEAD:Diva_lead_v64_WIP_checkpoint.zip')
    complete=json.loads((REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
    complete_version=complete['version'].split('-')[0]
    complete_paths=[complete['release_directory'],complete['ZIP']]
    complete_objects={path:git('rev-parse','HEAD:'+path) for path in complete_paths}
    name=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');C=AUTO/name;C.mkdir(parents=True,exist_ok=False)
    snapshot(p.parent,C/'proof');(C/'source-base').mkdir()
    (C/'automation').mkdir();shutil.copyfile(Path(__file__),C/'automation/auto_backup_three.py')
    for n in ['Diva_THREE_HELD_BASELINE.h2p','Diva_source.wav','Diva_before_spectral.wav','NEW-independent-base-pdc.wav','Diva_all281.tsv']:
        copy_immutable(b/n,C/'source-base'/n)
    copy_immutable(REPO/'diva-lead/v64-wip/Diva_THREE_HELD_180BPM.mid',C/'Diva_THREE_HELD_180BPM.mid')
    export_numeric(p,C/'numeric-run')
    # Preserve weaker completed trials too, without calling them the best sound.
    saved=[]
    for q,qd,qfamily,qbase in extra_proofs:
        if q==p:continue
        target=C/'other-completed-proofs'/q.parent.name;snapshot(q.parent,target)
        sourcebase=C/'source-base' if qfamily==family else C/'other-source-bases'/qfamily
        if not sourcebase.exists():
            sourcebase.mkdir(parents=True)
            for n in ['Diva_THREE_HELD_BASELINE.h2p','Diva_source.wav','Diva_before_spectral.wav','NEW-independent-base-pdc.wav','Diva_all281.tsv']:copy_immutable(qbase/n,sourcebase/n)
        write(target/'portable-source.json',dict(source_family=qfamily,source_base_relative=os.path.relpath(sourcebase,target),is_selected_best=False,match_reached=False))
        export_numeric(q,C/'other-numeric-runs'/q.parent.name)
        saved.append(dict(model=q.parent.name,source_family=qfamily,tone_score=qd['tone_score'],score=qd['score']))
    write(C/'other-completed-proofs.json',saved)
    ref,sr=sf.read(REPO/'diva-lead/v64-wip/Diva_original_lead_reference.wav');previous,psr=sf.read(REPO/'diva-lead/v64-wip/Diva_Lead_v64_REFERENCE_EDIT.wav');edit,esr=sf.read(p.parent/'REFERENCE_EDIT_WIP.wav')
    assert sr==psr==esr==48000 and ref.shape==previous.shape==edit.shape==(176064,2)
    assert hashlib.sha256(ref.astype('float64').tobytes()).hexdigest()=='450ab495963c48a8a3c5e94e64475a59ffdd04db4e7d4b5ad0d595e137ce512c'
    gain=float(np.sqrt(np.mean(ref*ref)/np.mean(edit*edit)));sf.write(C/'READY_THREE_HELD_RESEARCH_WIP.wav',edit*gain,sr,subtype='PCM_24');ready=sf.read(C/'READY_THREE_HELD_RESEARCH_WIP.wav')[0];gap=np.zeros((24000,2));ab=np.concatenate([ref,gap,previous,gap,ready]);assert np.max(np.abs(ab))<1
    wav=C/'AB_ORIGINAL_V64_CURRENT_THREE_HELD_WIP.wav';sf.write(wav,ab,sr,subtype='PCM_24');decoded=sf.read(wav)[0]
    np.testing.assert_array_equal(decoded[:176064],ref);np.testing.assert_array_equal(decoded[200064:376128],previous);np.testing.assert_array_equal(decoded[400128:],ready);assert not np.any(decoded[176064:200064]) and not np.any(decoded[376128:400128])
    subprocess.run(['ffmpeg','-v','error','-i',str(wav),'-codec:a','libmp3lame','-q:a','2',str(wav.with_suffix('.mp3'))],check=True)
    write(C/'checkpoint.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),private_full_proof=str(p),source_family=family,tone_score=d['tone_score'],score=d['score'],all_fixed_original_three_guards_passed=True,source_notes_per_phrase=3,total_note_on=6,Diva_ARP=True,single_global_stereo_RMS_gain=gain,per_note_or_per_channel_normalization=False,source_changes=d.get('changed_source_fields',{}),full_v64_contains_this_new_research=False,FL_GUI_tested=False,subjective_audition_performed=False,match_reached=False))
    (C/'FL_STUDIO_WAV_RU.md').write_text('''# Загрузить проверенный исследовательский WAV в FL Studio

Проект 180 BPM, желательно48kHz. Перетащить `READY_THREE_HELD_RESEARCH_WIP.wav` в Playlist: Normalize выключен, Pitch0, Time stretching Resample, Time Reset, канальный и микшерный уровни0dB, панорама по центру, Master без лимитера и дополнительной обработки. WAV уже обработан, Finish повторно не добавлять.

`AB_ORIGINAL_V64_CURRENT_THREE_HELD_WIP.wav` / MP3: оригинал с0с → полныйv64 с4,168с → этот исследовательский вариант с8,336с. Каждый вариант выровнен одним общим RMS-множителем для всего стерео. Входящие ноты — три удержания на фразу, два прохода, внутренний ARP Diva.

Это исследование новее DLL полногоv64. Для игры MIDI пользоваться полным комплектомv64 и его собственной инструкцией. Сохранённые здесь пресет/исходники служат воспроизводимым данным исследования; DLL другой версии не воспроизводит автоматически новые коэффициенты. Точное совпадение не достигнуто. GUI FL Studio здесь не проверялся.
'''.replace('желательно48','желательно 48').replace('Pitch0','Pitch 0').replace('уровни0','уровни 0').replace('с0с','с 0 с').replace('полныйv64','полный v64').replace('с4,','с 4,').replace('с8,','с 8,').replace('комплектомv64','комплектом v64'))
    guide=C/'FL_STUDIO_WAV_RU.md'
    guide.write_text(guide.read_text().replace('DLL полногоv64','DLL полного '+complete_version).replace('полным комплектом v64','полным комплектом '+complete_version))
    (C/'README.md').write_text(f'''# Трёхнотный WIP: {name}

[A/B оригинал → v64 → этот шаг](AB_ORIGINAL_V64_CURRENT_THREE_HELD_WIP.mp3), [WAV](AB_ORIGINAL_V64_CURRENT_THREE_HELD_WIP.wav), [FL Studio](FL_STUDIO_WAV_RU.md).

Источник: `{family}`. Ошибка тембра **{d['tone_score']:.10f}**, общая ошибка **{d['score']:.10f}**. Это ошибки измерений, не проценты сходства. Три длинные ноты на фразу, два прохода, внутренний ARP. Источник сравнения — загруженный оригинал. Точного совпадения нет; новые расчёты продолжаются.

`proof/` содержит завершённый свежий Diva/Windows/native/полную собственную NEW-базу/fixture/12 причинных случаев четырёх частот. `source-base/` — точно соответствующие этому источнику данные. Изменения источника и исходный отчёт явно указаны в `checkpoint.json`. Все ограничения привязаны к первоначальному выбранному трёхнотному варианту; небольшие регрессии отдельных критериев возможны в пределах прежних ограничений. GUI FL Studio и прослушивание ассистентом не выполнялись.

`verify_saved_checkpoint.py` независимо повторяет полный сохранённый путь NEW и отдельный fixture и проверяет SHA файлов. Нужны numpy/scipy/soundfile; исходная Diva не включена. Это исследовательский WAV и исходники, а не новый полный DLL-релиз. Полный v64 сохранён отдельно. Численные журналы, сжатые как gzip, перед историческим повторным запуском распаковать по `numeric-run/archived-numeric-journals.json`, если он существует.
''')
    (C/'verify_saved_checkpoint.py').write_text(PORTABLE_VERIFY)
    (C/'SHA256SUMS.txt').write_text(''.join(sha(x)+'  '+str(x.relative_to(C))+'\n' for x in sorted(C.rglob('*')) if x.is_file()))
    with (R/'auto-backup-last-portable-verification.json').open('w') as log:subprocess.run([sys.executable,'-B',str(C/'verify_saved_checkpoint.py')],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdout=log,check=True,timeout=300)
    pointer=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text());pointer.update(research_validation=str((C/'proof/validation.json').relative_to(ROOT)),tone_score=d['tone_score'],score=d['score'],latest_research_is_not_a_new_complete_DLL_release=True,source_preset_SHA256=sha(b/'Diva_THREE_HELD_BASELINE.h2p'),source_decoded_float32_SHA256=hashlib.sha256(sf.read(b/'Diva_source.wav',dtype='float32')[0].tobytes()).hexdigest(),research_source_family=family,research_source_changes=d.get('changed_source_fields',{}),research_source_is_user_selected_preset=family=='original-user-selected-three')
    write(ROOT/'CURRENT_THREE_NOTE_MODEL.json',pointer)
    checkpoints=[]
    for q in AUTO.glob('*/checkpoint.json'):
        v=json.loads(q.read_text());checkpoints.append((q.parent.name,v))
    rows=['| Снимок | Источник | Ошибка тембра ↓ |','|---|---|---:|']
    rows += [f"| [{n}]({n}/README.md) | {v['source_family']} | {v['tone_score']:.10f} |" for n,v in sorted(checkpoints,reverse=True)]
    (AUTO/'README.md').write_text('''# Автоматические бэкапы проверенного трёхнотного исследования

Только завершённые проверки настоящей Diva/Windows/собственной NEW-базы/12 причинных случаев. Каждый снимок содержит готовый WAV, A/B с загруженным оригиналом и инструкцию FL Studio. Это WIP: точное совпадение не достигнуто. Более свежие коэффициенты не входят автоматически в полный DLL-комплект v64. Программа не публикует непроверенные численные точки и не заявляет прослушивание или GUI-тест FL Studio.

'''+ '\n'.join(rows)+'\n')
    targets=[str(C.relative_to(REPO)),str((AUTO/'README.md').relative_to(REPO)),str((ROOT/'CURRENT_THREE_NOTE_MODEL.json').relative_to(REPO))]
    subprocess.run(['git','add','--',*targets],cwd=REPO,check=True)
    allowed=set(git('diff','--cached','--name-only').splitlines());assert all(x.startswith(str(C.relative_to(REPO))+'/') or x in targets[1:] for x in allowed)
    subprocess.run(['git','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--','.',':!*.tsv',':!*.log'],cwd=REPO,check=True)
    subprocess.run(['git','-c','gc.auto=0','commit','-q','-m',f'Back up verified three-held WIP {name}; tone error {d["tone_score"]:.9f}'],cwd=REPO,check=True)
    commit=git('rev-parse','HEAD');assert git('rev-parse','HEAD:diva-lead/v64-wip')==old_tree and git('rev-parse','HEAD:Diva_lead_v64_WIP_checkpoint.zip')==old_zip
    assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in complete_objects.items())
    subprocess.run(['git','-c','gc.auto=0','push','origin','HEAD:main'],cwd=REPO,check=True,timeout=180)
    assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
    public=[]
    for path in [AUTO/'README.md',C/'READY_THREE_HELD_RESEARCH_WIP.wav',C/'FL_STUDIO_WAV_RU.md',ROOT/'CURRENT_THREE_NOTE_MODEL.json']:
        relative=str(path.relative_to(REPO))
        with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+relative,timeout=60) as response:content=response.read();status=response.status
        assert status==200 and content==path.read_bytes();public.append(dict(path=relative,HTTP=status,SHA256=sha(path),byte_exact=True))
    assert not git('status','--porcelain')
    write(R/'auto-backup-last-public-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,remote_main_exact=True,HTTP_files=public,full_v64_tree_and_ZIP_immutable=True,current_complete_release=complete['version'],current_complete_tree_and_ZIP_immutable=True,checkpoint=str(C),tone_score=d['tone_score'],source_family=family,other_completed_trials_preserved=len(saved),match_reached=False))
    state('published_full_proved_research_and_HTTP_bytes_verified',commit=commit,checkpoint=str(C),tone_score=d['tone_score'],score=d['score'],source_family=family)
    print('AUTO_THREE_HELD_CHECKPOINT_PUSHED_AND_HTTP_BYTE_VERIFIED',commit,name,d['tone_score'],flush=True)

if '--check-only' in sys.argv:
    p,d,family,b=best_choice();print(json.dumps(dict(full_source_hashes_all281_12events_all12causal_cases_and_original_limits_checked=True,fully_proved_total=len(choices()),best=str(p),source_family=family,tone_score=d['tone_score'],score=d['score'],match_reached=False),indent=2));raise SystemExit(0)
lock=(R/'auto-backup-instance.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:
    while True:
        mirror_temporary_vectors()
        if PAUSE.exists():state('paused_for_manual_Git_work',pause_file=str(PAUSE))
        elif shutil.disk_usage(REPO).free<MIN_FREE_MIB*1024**2:state('paused_low_workspace_space',minimum_free_MiB=MIN_FREE_MIB)
        else:
            rows=choices();p,d,family,b=min(rows,key=lambda x:x[1]['tone_score']);last=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text());extra=unpublished(rows)
            previous=R/'auto-backup-last-public-verification.json';age=time.time()-previous.stat().st_mtime if previous.exists() else 600
            if '--force' in sys.argv or d['tone_score']<last['tone_score']-1e-5 or len(extra)>=3 or (extra and age>=600):
                with (R/'auto-backup-Git.lock').open('a') as gitlock:
                    try:fcntl.flock(gitlock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                    except BlockingIOError:state('waiting_for_manual_Git_lock')
                    else:
                        if PAUSE.exists():state('paused_for_manual_Git_work',pause_file=str(PAUSE))
                        else:
                            state('freezing_and_verifying_completed_research_before_Git',validation=str(p),tone_score=d['tone_score'],source_family=family,new_completed_trials=len(extra));publish(p,d,family,b,extra)
            else:state('waiting_for_next_full_proved_tone_improvement',latest_proved_validation=str(p),tone_score=d['tone_score'],score=d['score'],source_family=family,unpublished_completed_trials=len(extra))
        if '--once' in sys.argv:break
        time.sleep(30)
except Exception:state('failed_preserve_all_data_and_diagnose',error=traceback.format_exc());raise
