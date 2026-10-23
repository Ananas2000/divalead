"""Independent parse, documented FL20 workflow, ZIP extraction and real replay."""
from pathlib import Path
import gzip,hashlib,json,os,shutil,struct,subprocess,sys,zipfile
import numpy as np
import soundfile as sf
from win_vst3 import D,S,WinVST3,win
from native_chain import NativeChain
from native_fst import parse
from fl20_curve import apply_candidate
from fl20_diva_wrapper import program_chunk
from fl20_vst3_state import component_from_wrapper,read_vstpreset,decode_records,windows_uid,CID
B=D.parent;ROOT=B/'FL20_ZL_18_WIP';LABEL='Diva_ZL_18_WIP';V=ROOT/'verification'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(D/'ZL18-restoration-assessment')
from fl20_objective import FeaturesOriginal
f=FeaturesOriginal()
def read(p):return json.loads(Path(p).read_text())
choice=read(V/'candidate.json');seed=choice['native_base'];report=read(V/'ZL_FULL_VERIFICATION.json')
sys.path.insert(0,'/tmp/divalead-native-effects/pyflp-source')
import pyflp
from pyflp._events import _EventEnumMeta,EventEnum
original_call=_EventEnumMeta.__call__
def compatible(cls,value,*args,**kwargs):
    if cls is EventEnum:return cls._missing_(int(value))
    return original_call(cls,value,*args,**kwargs)
_EventEnumMeta.__call__=compatible
from pyflp.plugin import VSTPlugin,PluginID
fixtures=Path('/tmp/divalead-native-effects/pyflp-source/tests/assets')
assert len(list(pyflp.parse(fixtures/'plugins/fruity-wrapper.fst').events))>0
assert len(list(pyflp.parse(fixtures/'plugins/xfer-djmfilter.fst').events))>0
plugin_file=ROOT/'presets/SUM_ZL_18_WIP.fst';obj=pyflp.parse(plugin_file)
plugin=VSTPlugin(obj.events.subtree(lambda e:e.id in [PluginID.Data,PluginID.Wrapper]))
assert plugin.name=='ZL Equalizer 2'and plugin.vendor=='ZL Audio'and plugin.guid==windows_uid(CID)
assert not plugin.generator and not plugin.disabled
assert next(b for i,b in decode_records(plugin.state,1)if i==3)==(V/'ZL_component.bin').read_bytes()
project=pyflp.parse(ROOT/(LABEL+'.flp'));assert len(list(project.events))>0
# PyFLP's high-level mixer iterator groups event98 as a slot start. The real
# local FL20 file uses it as a terminator; even the untouched FL05 loses its
# first plugin in that iterator. Check the actual verified end-of-slot shell.
events=parse((ROOT/(LABEL+'.flp')).read_bytes())['events']
start=max(k for k,(i,b)in enumerate(events)if i==204 and b.decode('utf-16-le').rstrip('\0')=='04_SUM')
end=next(k for k in range(start+1,len(events))if events[k][0]==235)
block=events[start:end];tail=next(k for k,(i,b)in enumerate(block)if i==98 and b==struct.pack('<H',1))
head=max(k for k in range(tail)if block[k]==(98,struct.pack('<H',0)))
group=block[head+1:tail]
assert next(b for i,b in group if i==201).decode('utf-16-le').rstrip('\0')=='Fruity Wrapper'
assert struct.unpack_from('<II',next(b for i,b in group if i==212))==(4,1)
assert component_from_wrapper(next(b for i,b in group if i==213),8)==(V/'ZL_component.bin').read_bytes()
parse_report=dict(independent_parser='PyFLP',Python312_compatibility_shim_tested_on_two_real_stock_fixtures=True,
    actual_VST3_GUID_and_name_vendor_parsed=True,effect_not_generator=True,FLP_SUM_slot2_verified_by_real_FL20_end_of_slot_shell=True,
    PyFLP_high_level_mixer_slot_grouping_not_used_due_to_fixture_reproducible_start_vs_end98_difference=True,
    actual_FL_GUI_open_export_pending=True,match_reached=False)
(V/'VST3_INDEPENDENT_FL20_PARSE.json').write_text(json.dumps(parse_report,indent=2)+'\n')
subprocess.run(['/workspace/.venvs/divalead/bin/python','-B','/tmp/divalead-native-effects/verify_fst_with_pyflp.py',str(ROOT)],check=True)
guide=f'''# Diva ZL18 — промежуточный вариант на трёх нотах

Совпадение с оригиналом ещё не достигнуто. Добавлена настоящая бесплатная
ZL Equalizer 2 **1.4.1, Windows x64 VST3**. Рендеры получены настоящей Diva,
12 штатными DLL FL и официальным VST3 ZL в облачном Windows-хосте/Wine.
Новый проект не открывался и не экспортировался в вашей FL Studio.

1. Скачайте [официальный установщик ZL 1.4.1 Windows x64](https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi).
   Установите VST3; DLL плагина в комплекте нет. Нужны также ваша Diva
   и штатные Fruity WaveShaper, Chorus, Parametric EQ 2, Stereo Shaper.
2. В FL20 откройте **Options → Manage plugins**, включите проверку плагинов,
   нажмите **Find installed plugins**. Найдите **ZL Equalizer 2**, формат VST3.
3. Распакуйте комплект в новую папку, откройте **Diva_ZL_18_WIP.flp**.
   Выберите Pattern, 180 BPM, паттерн Diva. В каждой фразе три длинные ноты
   41→37→36, фраза повторяется дважды. Движение вверх делает ARP внутри Diva.
4. На микшере SUM/04_SUM уже записаны **Stereo Shaper → ZL Equalizer 2**.
   Mix обоих слотов100%. Маршруты SOURCE→MID/SIDE→SUM→Master сохранены.
   Старого Finish с задержкой12416 кадров здесь нет.
5. Если FL не нашла эффект или не восстановила его состояние: поставьте
   ZL Equalizer 2 во **второй слот SUM**, затем перетащите
   **presets/SUM_ZL_18_WIP.fst** на этот слот. Ещё один путь — загрузить
   **presets/04_SUM.fst** как состояние дорожки SUM через Mixer → File →
   Open mixer track state. Проверьте, что посыл SUM в Master включён.
   **presets/ZL_18_WIP.vstpreset** содержит то же фактическое состояние
   в стандартном VST3-контейнере и оставлен как дополнительная копия.
6. В ZL должны быть Minimum Phase, Lookahead0, Auto Gain OFF; Dynamics ON только у полос{'/'.join(str(b['index']+1)for b in choice['ZL_dynamic_bands'])}:
   12 статических Peak-полос,6 Mid и6 Side,4 All Pass и{len(choice['ZL_dynamic_bands'])} динамических Peak. Все610 значений
   прочитаны из реального плагина в verification/ZL_parameters.tsv.
   Не включайте Zero Phase/дополнительный lookahead для этой настройки.

**Послушать:** AB_REFERENCE_ZL18_WIP.mp3: оригинал0с → ZL18 с4,168с.
Только A/B выровнен по RMS. NATIVE_FULL_180BPM_WIP.wav — ненормализованный
полный6-секундный рендер; NATIVE_REFERENCE_EDIT_WIP.wav — фиксированный
монтаж для сравнения с оригиналом. Свободный Chorus меняется между дублями.

Все {len(choice['ZL_dynamic_bands'])} динамических полос входят в фактическое состояние; их
точные частоты/режимы/времена есть в610-param dump.

Сохранение/повторная загрузка состояния ZL и обработка одного и того же
входа проверены с проверкой численного остатка;12 штатных состояний также проверены реальными DLL.
WAV пакета рендерится из фактически сохранённых native-пресетов. Проверка
их численного совпадения использует прежний порог; SDK-контроль, если есть,
записан отдельно. Облачный подбор загружает сохранённые состояния только
при совпадении отпечатка всех настроек, чтобы изменения проб не игнорировались.
VST3-контейнер FL сделан по настоящим файлам FL20.8.4, отдельно разобран
PyFLP. Это не подтверждение открытия нового проекта GUI FL. Если требуется
сравнение на ПК, экспорт:48kHz stereo FLOAT32, HQ all plugins, insert/master
effects ON, Leave remainder, Pattern3bars, без добавочного мастер-лимитера.

ZL сообщает PDC0 и отвечает на импульс без добавленного сдвига; это не замер
ASIO/задержки всей DAW. Небольшая зависимость штатной цепи от размера блока
сохранена в LATENCY_AND_BLOCKS.json: максимум около2,1e−5 в zero-depth контроле.
Исходная native-цепь отвечает на импульс через2 кадра; ZL не добавляет буфера.

В verification лежат оценки, реальные состояния и доказательства ZIP replay.
NATIVE_BASE_PRESET_VERIFICATION.json и FLP_VERIFICATION.json относятся к
сохранённой основе до добавления ZL; ZL_FULL_VERIFICATION.json — ко всей новой
цепи. Обычный native x95 exporter не поддерживает этот дополнительный VST3:
для продолжения используйте отдельные ZL-скрипты и сохранённый компонент.
Оригинал служит только для анализа и A/B, в синтез не подмешивается.
'''
(ROOT/'FL_STUDIO_RU.md').write_text(guide,encoding='utf-8')
(ROOT/'README_RU.md').write_text('# Diva ZL18 WIP\n\nПолного совпадения нет. [Инструкция FL Studio20](FL_STUDIO_RU.md).\n\nКомплект: FLP, WAV, Diva, MIDI,17 FST, VST3 preset и проверки.\nОфициальный бесплатный ZL устанавливается отдельно. Новый FL GUI экспорт ожидает проверки.\n',encoding='utf-8')
(V/'CHECKPOINT_KIND.json').write_text(json.dumps(dict(family='native plus external ZL VST3',technical_WIP=True,actual_FL_validation_pending=True,reference_match_reached=False,does_not_replace_previous_native_only_kits=True),indent=2)+'\n')
archive=B/(LABEL+'_complete_WIP.zip')
def package():
    files=sorted(p for p in ROOT.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt')
    assert not any(p.suffix.lower()in ['.dll','.exe','.msi','.rar']for p in files)
    (ROOT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n'for p in files))
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file():z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None
        for p in ROOT.rglob('*'):
            if p.is_file():assert z.read(ROOT.name+'/'+p.relative_to(ROOT).as_posix())==p.read_bytes()

package()
restored=D/'ZL18-actual-ZIP-replay';restored.mkdir(exist_ok=False)
with zipfile.ZipFile(archive)as z:z.extractall(restored)
kit=restored/ROOT.name;pv=kit/'verification'
source_state=next(b for i,b in parse((kit/(LABEL+'.flp')).read_bytes())['events']if i==213)
assert program_chunk(source_state)==(pv/'Diva_VST_chunk.bin').read_bytes()
flp_states=[b for i,b in parse((kit/(LABEL+'.flp')).read_bytes())['events']if i==213]
assert component_from_wrapper(flp_states[-1],8)==(pv/'ZL_component.bin').read_bytes()
def make(tag):
    c=NativeChain(pv/'NATIVE_SOURCE_WITH_TAIL.wav',tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
    apply_candidate(c,np.array(seed['x']),dict(seed,native_saved_state_bundle=None))
    for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
    return c
c=make('ZL18-restored-native');z=WinVST3('ZL18-restored-ZIP-VST3');captures=[];state_checks=[]
try:
    for row in report['native_plugin_manifest']:
        path=kit/row['state'];c.load_state(row['node'],path);saved=restored/f"resaved-{row['node']}.bin";c.save_state(row['node'],saved)
        assert saved.read_bytes()==path.read_bytes();state_checks.append(row['node'])
    z.load(pv/'ZL_component.bin')
    for rep in range(6):
        raw,status=c.render();out,zstatus=z.render(raw);res=f.residual(out[:288000])
        captures.append(dict(loss=float(res@res)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025,assessment=f.local.last,native_status=status,VST3_status=zstatus))
    c.set(3,1,0);raw_zero,_=c.render();zero,_=z.render(raw_zero)
    # All three exported state containers must reproduce one actual active input.
    checks=[]
    for name,actual in [('FLP',component_from_wrapper(flp_states[-1],8)),('FST',component_from_wrapper(next(b for i,b in parse((kit/'presets/SUM_ZL_18_WIP.fst').read_bytes())['events']if i==213),10)),('VSTPRESET',read_vstpreset((kit/'presets/ZL_18_WIP.vstpreset').read_bytes()))]:
        path=restored/(name+'-component.bin');path.write_bytes(actual);z.load(path);again,_=z.render(raw_zero);container_error=float(abs(again-zero).max());np.testing.assert_allclose(again,zero,rtol=8*np.finfo(np.float32).eps,atol=1e-12)
        checks.append(dict(container=name,component_bytes_exact=True,active_audio_replay_bit_exact=bool(container_error==0),maximum_sample_error=container_error))
finally:c.close();z.close()
other=make('ZL18-original-native-zero-check');z=WinVST3('ZL18-original-native-ZL-zero-check')
try:
    for row in report['native_plugin_manifest']:other.load_state(row['node'],ROOT/row['state'])
    other.set(3,1,0);raw,status=other.render();z.load(V/'ZL_component.bin');expected,_=z.render(raw)
    zero_error=float(abs(expected-zero).max());np.testing.assert_allclose(expected,zero,rtol=8*np.finfo(np.float32).eps,atol=1e-12)
finally:other.close();z.close()
mean=float(np.mean([r['loss']for r in captures]));assert abs(mean-report['mean_original_objective'])<.01
proof=dict(source_ZIP_SHA256_before_adding_this_proof=hashlib.sha256(archive.read_bytes()).hexdigest(),archive_extracted_into_new_directory=True,
    all12_native_saved_states_exact=state_checks,whole_native_plus_ZL_zero_depth_audio_bit_exact=bool(zero_error==0),whole_native_plus_ZL_zero_depth_max_abs_error=zero_error,actual_active_state_container_replay=checks,
    six_fresh_whole_chain_mean=mean,six_fresh_whole_chain_std=float(np.std([r['loss']for r in captures])),captures=captures,
    actual_FL_GUI_open_or_export_not_claimed=True,fresh_machine_install_not_claimed=True,reference_match_reached=False)
(V/'ZIP_ACTUAL_REPLAY_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');package()
print('ZL18_COMPLETE_ZIP_AND_REAL_COMPONENT_REPLAY_PASS',mean,archive.stat().st_size,flush=True)
