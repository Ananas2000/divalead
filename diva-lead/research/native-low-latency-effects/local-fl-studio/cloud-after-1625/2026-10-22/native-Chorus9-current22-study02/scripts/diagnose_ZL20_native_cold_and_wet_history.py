"""Separate cold actual-preset replay from hot native render history."""
from pathlib import Path
import datetime,hashlib,json,shutil
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import D,WinVST3

ROOT=D/'ZL20-native-cold-vs-wet-history-audit-01'
ROOT.mkdir(exist_ok=False)
kit=D.parent/'FL20_ZL_20_WIP'
extracted=D/'ZL20-actual-ZIP-replay/FL20_ZL_20_WIP'
report=json.loads((kit/'verification/ZL_FULL_VERIFICATION.json').read_text())
seed=json.loads((kit/'verification/candidate.json').read_text())['native_base']
for source in [Path('/tmp/divalead-native-effects/ZL20-restored-native-render.wav'),Path('/tmp/divalead-native-effects/ZL20-original-native-zero-check-render.wav'),D/'ZL20-restored-ZIP-VST3-output.f32',D/'ZL20-original-native-ZL-zero-check-output.f32']:
    shutil.copyfile(source,ROOT/('failed-'+source.name))
captures={}
checks=[]
for label,base,wet in [('fresh-ZIP-1',extracted,0),('fresh-original',kit,6),('fresh-ZIP-2',extracted,0)]:
    c=NativeChain(base/'verification/NATIVE_SOURCE_WITH_TAIL.wav','native-history-audit-'+label,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
    z=WinVST3('ZL20-native-history-audit-'+label)
    def capture(name):
        raw,status=c.render();out,zstatus=z.render(raw)
        sf.write(ROOT/(name+'-native.wav'),raw,48000,subtype='FLOAT')
        sf.write(ROOT/(name+'-whole.wav'),out,48000,subtype='FLOAT')
        captures[name]=(raw,out)
        return raw,out
    try:
        apply_candidate(c,np.array(seed['x']),dict(seed,native_saved_state_bundle=None))
        for k,v in seed['chorus_overrides'].items():c.set(3,int(k),int(v))
        for row in report['native_plugin_manifest']:c.load_state(row['node'],base/row['state'])
        z.load(base/'verification/ZL_component.bin')
        c.set(3,1,0)
        first=capture(label+'-first-zero')
        again=capture(label+'-second-zero')
        if wet:
            for row in report['native_plugin_manifest']:c.load_state(row['node'],base/row['state'])
            for repeat in range(wet):c.render()
            c.set(3,1,0)
            capture(label+'-after-six-wet-zero')
            for row in report['native_plugin_manifest']:c.load_state(row['node'],base/row['state'])
            c.set(3,1,0)
            capture(label+'-after-reloaded-presets-zero')
        state_dir=ROOT/(label+'-states');state_dir.mkdir()
        for row in report['native_plugin_manifest']:
            if row['node']==3:continue # zero-depth is an intentional control change
            saved=state_dir/Path(row['state']).name;c.save_state(row['node'],saved)
            assert saved.read_bytes()==(base/row['state']).read_bytes(),(label,row['node'])
        checks.append(dict(label=label,all_unchanged_native_preset_bytes_exact=True,actual_WaveShaper_controls=[c.value_hint(0,j)for j in range(3)],actual_Chorus_depth=c.value_hint(3,1)))
    finally:c.close();z.close()
comparisons=[]
control=captures['fresh-ZIP-1-first-zero']
for label,pair in captures.items():
    comparisons.append(dict(label=label,native_max_abs_error=float(abs(control[0]-pair[0]).max()),whole_max_abs_error=float(abs(control[1]-pair[1]).max()),native_bit_exact=bool(np.array_equal(control[0],pair[0])),whole_bit_exact=bool(np.array_equal(control[1],pair[1]))))
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_DLL_and_official_VST3_executed=True,checks=checks,comparisons=comparisons,earlier_failed_hot_cold_capture_files_retained=True,no_tolerances_changed=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
(ROOT/'ACTUAL_COLD_AND_HISTORY_DIAGNOSIS.json').write_text(json.dumps(proof,indent=2)+'\n')
print('ACTUAL_NATIVE_COLD_HISTORY_AUDIT',json.dumps(proof),flush=True)
