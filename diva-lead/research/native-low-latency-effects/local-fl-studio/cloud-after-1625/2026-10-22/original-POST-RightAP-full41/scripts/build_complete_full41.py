"""Complete FL20 kit for exact NEW12-passed Right-AP point; independently replay ZIP."""
from pathlib import Path
import copy,csv,datetime,gzip,hashlib,io,json,os,shutil,struct,subprocess,zipfile
import xml.etree.ElementTree as ET
import numpy as np,soundfile as sf
from native_fst import parse,event,container
from fl20_vst3_state import component_from_wrapper,vstpreset,read_vstpreset
from stereo_artifact_helpers import replace_primary
from native_chain import NativeChain
from fl20_curve import apply_candidate,native_dsp_settings_SHA256
from native_post_trim import NativePostTrim
from win_vst3 import WinVST3
J=Path(__file__).resolve().parent;P=Path('/workspace/divalead');A=J.parent/'pc-stereo-20261024';N=J.parent/'native-low-latency-effects';Q=Path('/tmp/divalead-native12-POST-single-AP97-current620-20261107');PUBLIC=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22';SOURCE=PUBLIC/'stereo-cascade87-cohort-0620/FL20_STEREO_WIP';ROOT=Path('/tmp/divalead-full41-build/FL20_ZL41_STEREO_WIP');V=ROOT/'verification'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=read(Q/'completion.json');prior=read(Q/'PRIOR_COMBINED_CANDIDATE.json');latest=read(A/'stereo-continuous87/BEST_CANDIDATE.json')
assert s['robust_improvement']and s['all12_stereo_pairedlowmid']and latest['source_accepted_cohort']==prior['source_accepted_cohort']==620
primary=(Q/'CANDIDATE_PRIMARY.bin').read_bytes();post=(Q/'CANDIDATE_POST.bin').read_bytes();trim=(Q/'CANDIDATE_TRIM.bin').read_bytes();old_post=(Q/'POST.bin').read_bytes()
assert primary==Path(latest['native_ZL_component_state']).read_bytes()and old_post==Path(latest['post_ZL_component_state']).read_bytes()and post!=old_post and trim==Path(latest['post_native_trim_state']).read_bytes()
ROOT.parent.mkdir(exist_ok=True);assert not ROOT.exists();shutil.copytree(SOURCE,ROOT,ignore=shutil.ignore_patterns('*.wav','SHA256SUMS.txt'));V.mkdir()
old_layout=read(PUBLIC/'ZL-WIP40/artifact_layout.json');layout={k:v.replace('ZL40','ZL41')for k,v in old_layout.items()};layout['project']='Diva_ZL41_STEREO_WIP.flp'
changes={}
for file in [ROOT/'Diva_STEREO_CONTINUED_WIP.flp',*(ROOT/'presets').glob('*.fst')]:
    before=file.read_bytes();parsed=parse(before);has_post=any(i==213 and old_post in b for i,b in parsed['events']);data=replace_primary(before,old_post,post)if has_post else before
    parsed=parse(data);events=[(i,b.replace('ZL40'.encode('utf-16-le'),'ZL41'.encode('utf-16-le'))if i==203 else b)for i,b in parsed['events']];data=container(parsed['format'],b''.join(event(i,b)for i,b in events),parsed['channels'])
    destination=ROOT/(layout['project']if file.suffix=='.flp'else file.relative_to(ROOT).as_posix().replace('ZL40','ZL41'));file.unlink();destination.write_bytes(data);changes[destination.relative_to(ROOT).as_posix()]=dict(POST_replaced=has_post)
for file in list((ROOT/'presets').glob('*.vstpreset')):
    data=file.read_bytes();component=read_vstpreset(data);data=vstpreset(post)if component==old_post else data;dest=file.with_name(file.name.replace('ZL40','ZL41'));file.unlink();dest.write_bytes(data)
before=parse((SOURCE/'Diva_STEREO_CONTINUED_WIP.flp').read_bytes());after=parse((ROOT/layout['project']).read_bytes());bs=[b for i,b in before['events']if i==213];aa=[b for i,b in after['events']if i==213]
assert len(bs)==len(aa)and sum(x!=y for x,y in zip(bs,aa))==1 and component_from_wrapper(aa[-3],8)==primary and component_from_wrapper(aa[-2],8)==post and aa[-1]==trim
assert[b for i,b in before['events']if i in[224,235]]==[b for i,b in after['events']if i in[224,235]]
seed=copy.deepcopy(prior['native_base']);bundle=seed['native_saved_state_bundle'];old_directory=Path(bundle['directory'])
for row in bundle['manifest']:
    source=old_directory/row['state'];destination=ROOT/row['state'];destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination);assert sha(destination)==row['state_SHA256'];assert next(b for i,b in parse((ROOT/row['preset']).read_bytes())['events']if i==213)==destination.read_bytes()
for key in ['waveshaper_bipolar_base_state','waveshaper_os_local17_parent_state']:
    source=Path(seed[key]);destination=V/source.name
    if source.resolve()!=destination.resolve():shutil.copyfile(source,destination)
    seed[key]=str(destination)
bundle['directory']=str(ROOT);assert native_dsp_settings_SHA256(seed['x'],seed)==bundle['settings_SHA256']
for stem,blob in [('PRIMARY',primary),('POST',post)]:(V/f'ZL41_{stem}_COMPONENT.bin').write_bytes(blob)
(V/'POST_NATIVE_STEREO_TRIM.bin').write_bytes(trim);(ROOT/'artifact_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
for filename in ['Diva_NATIVE_WIP_THREE_HELD.h2p','Diva_THREE_HELD_180BPM.mid']:assert(ROOT/filename).read_bytes()==(SOURCE/filename).read_bytes()
shutil.copyfile(seed['source_manifest']['source_audio'],ROOT/'Diva_SOURCE_FROZEN_48k.wav');reference=P/'diva-lead/v83-wip/Diva_original_lead_reference.wav';assert sha(reference)=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f';shutil.copyfile(reference,ROOT/reference.name)
for filename in ['completion.json','PREDECLARED_PROTOCOL.json','ACTUAL_COLD_COMPONENT_TRIM_PROOF.json','FROZEN_BEFORE_NEW12.json']:shutil.copyfile(Q/filename,V/('AP97_'+filename))
shutil.copyfile(J/'ACTUAL_DIVA_SOURCE_RECHECK.json',V/'SOURCE_DIVA_RECHECK.json')
raw,sr=sf.read(Q/'NATIVE_00.wav',dtype='float32',always_2d=True);warm,rate=sf.read(Q/'CANDIDATE_00.wav',dtype='float32',always_2d=True);control,rate=sf.read(Q/'CONTROL620_00.wav',dtype='float32',always_2d=True);assert sr==rate==48000
sf.write(V/'ACTUAL_NATIVE_INPUT_00.wav',raw,48000,subtype='FLOAT');sf.write(V/'CONTROL620_FULL_WIP.wav',control,48000,subtype='FLOAT')
canonical=None;pre_expected=None;prepack_errors=[]
for k in range(2):
    p=WinVST3('Full41-canonical-P-'+str(k));z=WinVST3('Full41-canonical-Z-'+str(k));t=NativePostTrim(ROOT.parent/'buffers','Full41-canonical-T-'+str(k),cleanup_on_close=True)
    try:
        p.load(V/'ZL41_PRIMARY_COMPONENT.bin');z.load(V/'ZL41_POST_COMPONENT.bin');t.load(V/'POST_NATIVE_STEREO_TRIM.bin');mid,_=p.render(raw);pre,_=z.render(mid);out=t.render(pre);assert p.latency()+z.latency()==0
        if canonical is None:canonical=out.copy();pre_expected=pre.copy()
        np.testing.assert_allclose(out,canonical,rtol=8*np.finfo(np.float32).eps,atol=1e-12);prepack_errors.append(float(abs(out-canonical).max()))
    finally:p.close();z.close();t.close()
warm_error=float(abs(canonical-warm).max());assert warm_error<=2e-7
sf.write(ROOT/'ZL41_STEREO_FULL_WIP.wav',canonical,48000,subtype='FLOAT')
# Exercise the portable native bundle and generator without its cached bundle.
native=[];zero_outputs=[];native_resaves=[]
for k in range(2):
    n=NativeChain(seed['source_manifest']['native_input'],'Full41-native-'+str(k),fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');native.append(n)
    model=copy.deepcopy(seed)
    if k==1:model.pop('native_saved_state_bundle')
    apply_candidate(n,np.array(model['x']),model)
    for key,value in model['chorus_overrides'].items():n.set(3,int(key),int(value))
    for row in bundle['manifest']:
        dest=ROOT.parent/f'actual-native-{k}-{row["node"]}.bin';n.save_state(row['node'],dest);assert dest.read_bytes()==(ROOT/row['state']).read_bytes()
    native_resaves.append(True);n.set(3,1,0);y,_=n.render();zero_outputs.append(y);n.close()
native_error=float(abs(zero_outputs[0]-zero_outputs[1]).max());assert native_error<=2e-7
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT.parent/'assessment');from fl20_objective import a
edit=lambda y:a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));ref,rate=sf.read(reference,always_2d=True);np.testing.assert_array_equal(ref,a.REF);new_edit=edit(canonical);old_edit=edit(control);rms=lambda y:float(np.sqrt(np.mean(y*y)));gains=[1.,rms(ref)/rms(old_edit),rms(ref)/rms(new_edit)];gap=np.zeros((24000,2));ab=np.concatenate([ref,gap,old_edit*gains[1],gap,new_edit*gains[2]]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
sf.write(ROOT/'AB_ORIGINAL_620_ZL41_WIP.flac',ab,48000,subtype='PCM_24');working=ROOT.parent/'AB-working.wav';sf.write(working,ab,48000,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(working),'-codec:a','libmp3lame','-b:a','320k',str(ROOT/'AB_ORIGINAL_620_ZL41_WIP.mp3')],check=True);working.unlink()
(V/'AB_LEVELS.json').write_text(json.dumps(dict(order=['original','620','full41'],starts_seconds=[0,4.168,8.336],global_stereo_RMS_gains=gains,common_peak_safety_gain=safety,same_actual_native_input_for620_and41=True,only_AB_normalized=True,no_independent_channel_normalization=True),indent=2)+'\n')
choice=copy.deepcopy(prior);choice.update(native_base=seed,native_ZL_component_state=str(V/'ZL41_PRIMARY_COMPONENT.bin'),primary_ZL_component_state=str(V/'ZL41_PRIMARY_COMPONENT.bin'),post_ZL_component_state=str(V/'ZL41_POST_COMPONENT.bin'),post_native_trim_state=str(V/'POST_NATIVE_STEREO_TRIM.bin'),post_native_trim_state_SHA256=hashlib.sha256(trim).hexdigest(),source_accepted_cohort='full41-RightAP12800-Q25-after620',full_public_kit_directory='ZL-WIP41',accepted_full_public_kit='ZL41',recorded_audio=str(ROOT/'ZL41_STEREO_FULL_WIP.wav'),loss=float(np.mean([r['candidate']['loss']for r in s['captures'][:10]])),loss_definition='exact point NEW12 vs620; first6 AND first10/3SEM, two cold, Air/Tone/stereo; not comparable across independent random-Chorus absolute means',not_adopted_until_publication=True,native_parameters_changed_from_previous_public_kit=False,source_WS_OS_step1_local17_changed=False,PRIMARY_and_POST_refitted=False,PRIMARY_unchanged_from620=True,only_POST_Right_AllPass_slot7_added=True,source_Diva_unchanged=True,source_and_all12_pre_ZL_native_states_unchanged=True,final_native_trim_unchanged=True,topology='native12 -> unchanged PRIMARY620 -> original POST40 plus Right AllPass7 12800Hz Q25 order12dB/oct -> unchanged native final trim; 13native+2ZL',nonincreasing_Air_fresh10_and_bothcold_confirmed=True,nonincreasing_Air_proof_scope='exact frozen41 point vs620 AND full40 only; future numerical children require their own gates',interrupted897_training_search_recovered_not_claimed_completed=False,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
for label,blob in [('primary',primary),('post',post)]:
    values={e.attrib['id']:float(e.attrib['value'])for e in ET.fromstring(blob[8:8+struct.unpack_from('<I',blob,4)[0]]).find('Para')};active=[dict(slot=k,type=values['filter_type'+str(k)],lr_mode=values['lr_mode'+str(k)],frequency=values['freq'+str(k)],Q=values['q'+str(k)],gain_dB=values['gain'+str(k)])for k in range(24)if values['filter_status'+str(k)]==2];choice[label+'_active_filters']=active
    if label=='post':
        for mode,number in [('Stereo',0),('Left',1),('Right',2),('Mid',3),('Side',4)]:
            choice['post_'+mode+'_AllPasses']=[f for f in active if f['type']==9 and f['lr_mode']==number];choice['post_'+mode+'_EQ']=[f for f in active if f['type']!=9 and f['lr_mode']==number]
assert choice['post_Right_AllPasses']==[dict(slot=7,type=9.,lr_mode=2.,frequency=12800.,Q=25.,gain_dB=0.)]
(V/'candidate.json').write_text(json.dumps(choice,indent=2)+'\n')
guide='''# WIP41: три длинные ноты, Diva и обычная обработка

Это небольшое подтверждённое улучшение относительно620. Полного совпадения с оригиналом пока нет. Изменён только второй ZL: добавлен Right AllPass в полосе7,12800Hz,Q25,12dB/oct. Первый ZL, все13 Fruity, Diva, MIDI, ARP/ADSR и маршруты сохранены. Остаточный перекос по частотам остаётся.

1. Распакуйте полный ZIP в новую папку. Нужны Diva, штатные Fruity FL Studio20 и бесплатный ZL Equalizer2v1.4.1 x64: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi . При необходимости выполните Plugin Manager → Find installed plugins.
2. Откройте Diva_ZL41_STEREO_WIP.flp, включите Pattern,180BPM,48000Hz. Если Diva запросит пресет, загрузите Diva_NATIVE_WIP_THREE_HELD.h2p из ZIP. MIDI Diva_THREE_HELD_180BPM.mid содержит три длинные входящие ноты41→37→36 на фразу, два повтора. Верхние скачки создаёт внутренний ARP.
3. При переносе ИЗ620 замените только второй ZL на presets/ZL41_STEREO_FIX.vstpreset либо загрузите presets/SUM_ZL41_STEREO_FIX.fst. Первый ZL и последний Fruity Stereo Shaper оставьте как в620. Для более старого проекта предпочтителен полный новый FLP.
4. Порядок на SUM: прежний StereoShaper → ZL41 PRIMARY → ZL41 STEREO FIX → последний Fruity StereoShaper POST TRIM → Master. Оба ZL: Minimum Phase,Lookahead0,AutoGainOff,Mix100%. Всего13native+2ZL, нового плагина нет. Старого Finish/свёртки нет. Референс в синтез не подмешивается; MistaTowa не используется.

A/B AB_ORIGINAL_620_ZL41_WIP.mp3/FLAC: оригинал0с →620с4.168с →WIP41с8.336с. Оба наших варианта обработаны из одного реального native-входа. Только A/B выровнен общей stereoRMS и общей защитой пиков; каналы отдельно не нормировались. Рабочий ZL41_STEREO_FULL_WIP.wav без нормировки.

Точка прошла12 новых сравнений, оба порога first6/first10>max(.0005,3SEM), оба холодных запуска, снижение Air против620 и полного40, Tone и все стерео/paired-lowmid ограничения. Цифры находятся в verification/AP97_completion.json; это не процент сходства на слух. Проверены реальные DLL/VST3 под Wine, нативные состояния/генератор без кеша, FLP/FST/MIDI, независимая распаковка ZIP и холодные каскады. Заявленный ZL PDC0; задержка ASIO и открытие нового FLP в WindowsGUI здесь не проверены.
'''
for name in ['FL_STUDIO_RU.md','README_RU.md']:(ROOT/name).write_text(guide)
(V/'BUILD_PROOF.json').write_text(json.dumps(dict(exactly_one_DSP_payload_changed_from620=True,PRIMARY_source_MIDI_ARP_ADSR_routes_all13_native_unchanged=True,changed_artifacts=changes,all12_native_state_resaves_exact_with_AND_without_cached_bundle=native_resaves,native_zeroDepth_generator_vs_cache_max_error=native_error,zeroDepth_only_diagnostic_not_exported=True,cold_vs_quality_validation_warm_error=warm_error,unchanged_native_absolute_tolerance=2e-7,reference_match_reached=False),indent=2)+'\n')
archive=ROOT.parent/'Diva_ZL41_STEREO_WIP_complete.zip'
def pack():
    (ROOT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n'for p in sorted(ROOT.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as zipped:
        for file in sorted(ROOT.rglob('*')):
            if file.is_file():zipped.write(file,ROOT.name+'/'+file.relative_to(ROOT).as_posix())
pack();restore=ROOT.parent/'independent-ZIP-restore';restore.mkdir()
with zipfile.ZipFile(archive)as zipped:assert zipped.testzip()is None;zipped.extractall(restore)
restored=restore/ROOT.name
for line in(restored/'SHA256SUMS.txt').read_text().splitlines():digest,name=line.split('  ',1);assert sha(restored/name)==digest
saved_raw,rate=sf.read(restored/'verification/ACTUAL_NATIVE_INPUT_00.wav',dtype='float32',always_2d=True);saved_wav,rate=sf.read(restored/'ZL41_STEREO_FULL_WIP.wav',dtype='float32',always_2d=True);np.testing.assert_array_equal(saved_raw,raw)
errors=[];pre_errors=[];latencies=[];impulse_delays=[]
for k in range(2):
    p=WinVST3('Full41-ZIP-P-'+str(k));z=WinVST3('Full41-ZIP-Z-'+str(k));t=NativePostTrim(ROOT.parent/'cold-buffers','Full41-ZIP-T-'+str(k),cleanup_on_close=True)
    try:
        for host,key in [(p,'primary_component'),(z,'post_component'),(t,'post_native_trim_state')]:
            path=restored/layout[key];host.load(path);dest=ROOT.parent/f'ZIP-cold-{k}-{path.name}';host.save(dest);assert dest.read_bytes()==path.read_bytes()
        mid,_=p.render(saved_raw);pre,_=z.render(mid);got=t.render(pre);np.testing.assert_allclose(pre,pre_expected,rtol=8*np.finfo(np.float32).eps,atol=1e-12);np.testing.assert_array_equal(got,saved_wav);errors.append(float(abs(got-saved_wav).max()));pre_errors.append(float(abs(pre-pre_expected).max()));latencies.append(p.latency()+z.latency());assert latencies[-1]==0
        pulse=np.zeros((32768,2),np.float32);pulse[8192]=.0001;mid,_=p.render(pulse);pre,_=z.render(mid);out=t.render(pre);indices=np.flatnonzero(np.max(abs(out),axis=1)>1e-12);assert len(indices);impulse_delays.append(int(indices[0])-8192);assert impulse_delays[-1]==0
        if k==0:
            for host,stem in [(p,'PRIMARY'),(z,'POST')]:
                path=V/(stem+'_610_PARAMETERS.tsv');host.dump(path);blob=path.read_bytes();text=blob.decode();normal='\n'.join(line+'""'if line.endswith('\t')else line for line in text.splitlines())+'\n';assert list(csv.reader(io.StringIO(text),delimiter='\t'))==list(csv.reader(io.StringIO(normal),delimiter='\t'));(V/(path.name+'.raw.gz')).write_bytes(gzip.compress(blob,mtime=0));path.write_text(normal)
    finally:p.close();z.close();t.close()
zip_proof=dict(two_cold_ZIP_full_working_WAV_errors=errors,two_cold_ZL_before_trim_errors=pre_errors,all_component_trim_resaves_exact=True,ZL_PDC_frames=latencies,postprocessing_impulse_added_delay_frames=impulse_delays,final_metadata_repack_only_DSP_and_audio_unchanged=True)
(V/'COLD_ZIP_PROOF.json').write_text(json.dumps(zip_proof,indent=2)+'\n');pack()
with zipfile.ZipFile(archive)as zipped:
    assert zipped.testzip()is None
    for file in ROOT.rglob('*'):
        if file.is_file():assert zipped.read(ROOT.name+'/'+file.relative_to(ROOT).as_posix())==file.read_bytes()
result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(ROOT),ZIP=str(archive),ZIP_SHA256=sha(archive),ZIP_bytes=archive.stat().st_size,exact_post_RightAP12800_Q25_point=True,source_cohort=620,cold_vs_warm_native_roundoff_error=warm_error,all_native_state_resaves_exact=True,native_no_cache_vs_cached_zeroDepth_error=native_error,**zip_proof,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
(J/'ZL41_BUILD_COMPLETION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
