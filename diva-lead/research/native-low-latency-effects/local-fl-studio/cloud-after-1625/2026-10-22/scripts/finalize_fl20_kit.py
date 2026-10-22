"""Patch verified FL05, preserve its performance, document and package a WIP."""
from pathlib import Path
import hashlib,json,os,struct,subprocess,sys,zipfile
import numpy as np
import soundfile as sf
from native_fst import parse,container,event
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(Path(sys.argv[1]).parent/(Path(sys.argv[1]).name+'-finalize-assessment'))
from fl20_objective import a

root=Path(sys.argv[1]);label=sys.argv[2]
LOCAL=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22')
proof=json.loads((root/'verification/NATIVE_PRESET_VERIFICATION.json').read_text())
assert proof['preset_state_bytes_exact'] and proof['zero_depth_routing_audio_exact']
assert proof['actual_FL_validation_pending'] and not proof['match_reached']
candidate=json.loads((root/'verification/candidate.json').read_text());mix=round(candidate['x'][93]*12800)
src=LOCAL/'Diva_NATIVE_LOCAL_05_MODDEPTH_WIP.flp';old=src.read_bytes();p=parse(old)
states=[b for i,b in p['events']if i==213];assert len(states)==13
nodes=[0,3,13,14,10,4,5,11,6,7,12,8]
manifest={r['node']:r for r in proof['native_plugin_manifest']}
newstates=[(root/manifest[n]['state']).read_bytes()for n in nodes]
old_native_names=[b.decode('utf-16-le').rstrip('\0')for i,b in p['events']if i==201 and b not in [b'',b'\0\0']]
assert old_native_names[1:]==[manifest[n]['internal_name']for n in nodes],old_native_names
events=[];seen=0;changed_controls=[]
for ident,b in p['events']:
    if ident==213:
        if seen>0:b=newstates[seen-1]
        seen+=1
    if ident==225:
        data=bytearray(b)
        for off in range(0,len(data),12):
            _,param,kind,track,value=struct.unpack_from('<IBBHi',data,off)
            if param==1 and kind==31 and (track>>6)&127==1 and track&63==1:
                struct.pack_into('<i',data,off+8,mix)
                if value!=mix:changed_controls.append(dict(before=value,after=mix))
        b=bytes(data)
    events.append((ident,b))
data=container(p['format'],b''.join(event(i,b)for i,b in events),p['channels'])
dest=root/(label+'.flp');dest.write_bytes(data);q=parse(data)
actualstates=[b for i,b in q['events']if i==213]
assert actualstates==[states[0],*newstates]
assert [i for i,b in q['events']]==[i for i,b in p['events']]
for (i,oldb),(j,newb)in zip(p['events'],q['events']):
    if i not in [213,225]:assert oldb==newb,(i,len(oldb),len(newb))
notes_old=[b for i,b in p['events']if i==224];assert sum(len(b)//24 for b in notes_old)==6
assert notes_old==[b for i,b in q['events']if i==224]
assert [b for i,b in q['events']if i==235]==[b for i,b in p['events']if i==235]
flp_proof=dict(source=src.name,project=dest.name,project_SHA256=hashlib.sha256(data).hexdigest(),
    Diva_state_byte_exact_against_actual_local_FL05=True,other_than_native_states_and_Chorus_slot_mix_events_byte_exact=True,
    all12_native_states_exact_against_real_DLL_saved_states=True,only_three_held_notes_per_phrase=True,
    six_note_blocks_total=True,MIDI224_unchanged=True,routes235_unchanged=True,channel_volume11148_unchanged=True,
    Chorus_slot_mix_raw=mix,changed_controls=changed_controls,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
(root/'verification/FLP_VERIFICATION.json').write_text(json.dumps(flp_proof,indent=2)+'\n')

ref,_=sf.read(root/'Diva_original_lead_reference.wav',dtype='float64')
old83,_=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_Lead_v83_REFERENCE_EDIT.wav',dtype='float64')
local05,_=sf.read(LOCAL/'renders/FL_NATIVE_05_MODDEPTH.wav',dtype='float64')
local05=a.h.edit_aligned(a.h.align_with_pdc(local05,dict(alignment_frames=819),latency=0))
native,_=sf.read(root/'NATIVE_REFERENCE_EDIT_WIP.wav',dtype='float64')
assert ref.shape==old83.shape==local05.shape==native.shape
clips=[ref,old83,local05,native];rms=lambda y:float(np.sqrt(np.mean(y*y)))
gains=[rms(ref)/rms(y)for y in clips];gap=np.zeros((24000,2))
ab=np.concatenate([z for i,y in enumerate(clips)for z in ([gap]if i else[])+[y*gains[i]]])
safety=min(1.,.95/float(abs(ab).max()));ab*=safety
tmp=root.parent/(label+'-AB-working.wav');sf.write(tmp,ab,48000,subtype='FLOAT')
abname='AB_ORIGINAL_V83_ACTUAL_FL05_'+label+'.mp3'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-codec:a','libmp3lame','-b:a','320k',str(root/abname)],check=True)
tmp.unlink()
(root/'verification/AB_LEVELS.json').write_text(json.dumps(dict(order=['original','v83 old Finish','actual local FL05 export',label+' native DLL host, pending FL export'],
    starts_seconds=[i*(len(ref)/48000+.5)for i in range(4)],per_clip_RMS_gains=gains,common_peak_safety_gain=safety,
    only_AB_level_normalized=True,full_candidate_WAV_FLOAT32_unscaled=True),indent=2)+'\n')

guide=f'''# {label} — промежуточный вариант на трёх нотах

Полного совпадения с оригиналом нет. Этот кандидат улучшает критерии в
исправленном native-хосте, но его новый контрольный экспорт в реальной FL
Studio ещё не выполнен. WAV получен настоящими DLL эффектов из свежего
Diva FL05; он не выдаётся за экспорт из вашей FL. Проверенный FL05 сохранён.

## Как загрузить в FL Studio 20

1. Распакуйте комплект в новую папку. Откройте `{label}.flp` через File → Open.
   Нужна установленная Diva и штатные Fruity WaveShaper, Chorus, Parametric EQ 2,
   Stereo Shaper. Присланные DLL не надо сканировать как VST; в архиве их нет.
2. Включите **Pattern**, выбранный паттерн с Diva, **180 BPM**. Нажмите Play.
   Уже записаны три длинные ноты 41→37→36 на фразу, две фразы. Вверх звук
   уходит за счёт внутреннего ARP Diva; MIDI на короткие ноты не заменён.
3. Diva, исходный channel volume11148 и маршруты сохранены из проверенного
   локального FL05. Новый пресет Diva отдельно: `Diva_NATIVE_WIP_THREE_HELD.h2p`.
   PWModDepth +1, KeyFollow2, VCA ModDepth−58; ARP/ADSR прежние.
4. Проверьте цепочку SOURCE → MID/SIDE → SUM → Master по таблице ниже.
   Старый Finish здесь не используется. Все посылы100%, фейдеры0dB, у SOURCE
   прямой посыл Master выключен; у MID/SIDE только SUM, у SUM только Master.

| Дорожка | Порядок эффектов |
| --- | --- |
| SOURCE | WaveShaper → Chorus → Stereo Shaper Phase_R → Stereo Shaper Phase_L |
| MID | Stereo Shaper Encode → EQ2 A → EQ2 B |
| SIDE | Stereo Shaper Encode → EQ2 A → EQ2 B → Stereo Shaper Decode |
| SUM | Stereo Shaper Stereo |

Mix именно **слота Chorus: {100*mix/12800:.8g}%** (raw{mix}/12800).
Остальные слоты100%. Native WetOnly=0. Две формы LFO изменены, их actual
raw-значения сохранены в candidate.json/chorus_overrides и внутри FST/FLP.
При желании собрать вручную: загрузите четыре `presets/01_SOURCE.fst` …
`04_SUM.fst` через Mixer → File → Open mixer track state и выставьте маршруты
вручную. Эти новые FST используют исправленный FL20 slot shell. Отдельные
12 plugin FST также включены. Состояния каждого плагина реально прочитаны
обратно из DLL; zero-depth control повторил весь аудиотракт по отсчётам.

## Что слушать

`NATIVE_FULL_180BPM_WIP.wav` — 6с, 48kHz stereo FLOAT32, полный рендер без
скрытых gain/time corrections. `NATIVE_REFERENCE_EDIT_WIP.wav` — прежний
фиксированный монтаж под референс. A/B: **оригинал → v83 со старым Finish →
реальный FL05 → этот WIP**. Начала сегментов0 / 4.168 / 8.336 / 12.504с.
Только в A/B выровнены RMS и общий безопасный peak; коэффициенты в AB_LEVELS.
Свободный Chorus слегка меняет повторные WAV: выбрана медианная оценка из6,
а не самый удачный дубль. Оригинал используется только для сравнения.

Цепочка сообщает declared PDC0, старый Finish сообщал12416 кадров при48kHz.
Это не измерение задержки звуковой карты или всей FL. Если нужно сравнить
сам звук, не добавляйте мастер-лимитер/нормализацию. Контрольный экспорт:
48kHz stereo FLOAT32, HQ all plugins, insert/master FX ON, Leave remainder,
Pattern3bars. Первый новый actual-FL экспорт остаётся обязательной проверкой
переноса; данные хоста сами по себе её не заменяют.
'''
(root/'FL_STUDIO_RU.md').write_text(guide,encoding='utf-8')
(root/'README_RU.md').write_text(f'''# {label} WIP

Три удерживаемые ноты на фразу; подбор продолжается, полного совпадения нет.
[Загрузка в FL Studio 20](FL_STUDIO_RU.md). FLP основан на реальном FL05;
native DLL рендер и FST проверены, новый actual-FL GUI export ещё предстоит.
''',encoding='utf-8')
(root/'verification/CHECKPOINT_KIND.json').write_text(json.dumps(dict(native_port_checkpoint=True,technical_WIP=True,
    actual_FL_validation_pending=True,replace_main_v83=False,replace_user_local_FL05=False,reference_match_reached=False),indent=2)+'\n')
files=sorted(p for p in root.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt')
assert not any(p.suffix.lower()in['.dll','.exe','.rar']for p in files)
(root/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\n'for p in files))
zipname=root.parent/(label+'_complete_WIP.zip')
with zipfile.ZipFile(zipname,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for p in sorted(root.rglob('*')):
        if p.is_file():z.write(p,root.name+'/'+p.relative_to(root).as_posix())
with zipfile.ZipFile(zipname)as z:
    assert z.testzip()is None
    for p in root.rglob('*'):
        if p.is_file():assert z.read(root.name+'/'+p.relative_to(root).as_posix())==p.read_bytes()
print('FL20_WIP_PROJECT_AB_INSTRUCTIONS_AND_ZIP_VERIFIED',label,zipname.stat().st_size,flush=True)
