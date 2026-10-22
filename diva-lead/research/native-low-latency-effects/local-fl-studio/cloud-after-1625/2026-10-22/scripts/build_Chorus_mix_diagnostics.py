"""Prepare minimal FL04 diagnostic copies for a future actual-FL export.

Every byte outside the specified Chorus state/control record is preserved.
These projects are analysis fixtures and do not replace the user's open FL05.
"""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path('/tmp/divalead-local-1625/FL-Chorus-diagnostic-projects');ROOT.mkdir(exist_ok=False)
LOCAL=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio')
sys.path.insert(0,str(LOCAL/'tools'));import cloud_native_fst as f
source=LOCAL/'2026-10-22/Diva_NATIVE_LOCAL_04_CALIBRATED_WIP.flp';original=source.read_bytes();p=f.parse(original);old_states=[b for i,b in p['events']if i==213];assert len(old_states)==13
assert len(old_states[2])==52 and struct.unpack('<13i',old_states[2])==(1,344,2139,246,2643,4647,2286,0,0,0,0,4532,0)
rows=[]
for name,enabled,mix,wetonly in [('DRY_CHORUS_BYPASS',0,4923,0),('FULL_PLUGIN',1,12800,0),('WET_ONLY',1,12800,1024),('MIX_4923',1,4923,0)]:
    events=[];states_seen=0;control_changes=[]
    for ident,b in p['events']:
        if ident==213:
            if states_seen==2:
                v=bytearray(b);struct.pack_into('<i',v,48,wetonly);b=bytes(v)
            states_seen+=1
        if ident==225:
            v=bytearray(b)
            for o in range(0,len(v),12):
                _,param,kind,track,value=struct.unpack_from('<IBBHi',v,o)
                if kind==31 and (track>>6)&127==1 and track&63==1 and param in [0,1]:
                    new=enabled if param==0 else mix
                    if new!=value:control_changes.append(dict(insert=1,slot=1,param=param,before=value,after=new))
                    struct.pack_into('<i',v,o+8,new)
            b=bytes(v)
        events.append((ident,b))
    data=f.container(p['format'],b''.join(f.event(i,b)for i,b in events),p['channels']);out=ROOT/('DIAG_FL04_CHORUS_'+name+'.flp');out.write_bytes(data)
    q=f.parse(data);new_states=[b for i,b in q['events']if i==213];assert len(new_states)==13
    for index,(old,new)in enumerate(zip(old_states,new_states)):
        if index!=2:assert old==new
        else:assert old[:48]==new[:48] and struct.unpack_from('<i',new,48)[0]==wetonly
    assert [b for i,b in q['events']if i in [224,235]]==[b for i,b in p['events']if i in [224,235]]
    if name=='MIX_4923':assert data==original
    rows.append(dict(project=out.name,SHA256=hashlib.sha256(data).hexdigest(),Chorus_enabled=enabled,slot_mix_raw=mix,WetOnly_raw=wetonly,control_changes=control_changes,source_Diva_state_and_MIDI_and_routes_unchanged=True,other11_native_states_byte_exact=True,actual_FL_export_pending=True,not_a_lead_candidate=True))
(ROOT/'VERIFICATION.json').write_text(json.dumps(rows,indent=2)+'\n')
(ROOT/'README_RU.md').write_text('''# Диагностика Chorus в FL Studio 20

Эти четыре проекта — копии проверенного FL04 для анализа смешивания.
Открытый у пользователя FL05 не изменён. Ноты, Diva, channel volume11148,
маршруты и остальные11 native states сохранены. Это не новые лид-пресеты.

При следующем локальном сеансе экспортировать каждый проект в отдельный WAV:
48kHz, stereo, float32, Pattern3bars, HQ all plugins, insert/master effects ON,
Leave remainder. По возможности сделать по три повтора каждого экспорта.
Сохранить после открытия также фактический FLP: это подтвердит, что FL
прочла enable/mix/WetOnly именно так, как записано в VERIFICATION.json.

- DRY_CHORUS_BYPASS: только Chorus выключен.
- FULL_PLUGIN: Chorus WetOnly0, слот100%.
- WET_ONLY: Chorus WetOnly1024 (native «yes»), слот100%.
- MIX_4923: исходный FL04, слот4923/12800. Файл побитно равен исходному FL04.

В actual native DLL отдельно измерено FULL_PLUGIN≈0.7×DRY+WET_ONLY
при нулевой глубине модуляции. Это пока НЕ измерение закона ручки Mix в FL.
После реальных экспортов проверить коэффициенты FULL и MIX как комбинации
DRY/WET с учётом небольшой вариативности исходного Diva и Chorus.
Ни один из этих WAV не используется как инструмент или материал синтеза.
''',encoding='utf-8')
print('FOUR_VERIFIED_MINIMAL_FL_DIAGNOSTIC_PROJECTS_PREPARED',flush=True)
