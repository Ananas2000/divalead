"""Check actual supplied FL DLL initialization, without DSP or licensing stubs."""
from pathlib import Path
import concurrent.futures, datetime, hashlib, json, os, re, subprocess, time

W=Path(__file__).resolve().parent;S=Path('/workspace/divalead-setup')
names=['Fruity Chorus_x64.dll','Fruity Stereo Shaper_x64.dll','Fruity Parametric EQ 2_x64.dll','Maximus_x64.dll']
env=os.environ.copy();env.update(WINEPREFIX=str(W/'wine'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),
 WINEDEBUG='+module',DISPLAY=':90',XDG_CACHE_HOME=str(W/'cache'))
def run(name):
    plugin=next(Path('/workspace/attachments').glob('*/'+name))
    label=name.replace(' ','_').replace('.dll','');log=W/(label+'-native-load.log')
    with log.open('w') as f:
        p=subprocess.Popen([str(S/'sysroot/usr/lib/wine/wine64'),str(W/'fl_native_probe.exe'),
                            'Z:'+str(plugin).replace('/','\\')],env=env,stdout=f,stderr=f)
        start=time.monotonic();stop='exited'
        while p.poll() is None and time.monotonic()-start<35:
            text=log.read_text()
            if 'NATIVE_LOAD_EXCEPTION rip=0000000000000000' in text:
                stop='null_function_call_during_native_library_initialization';break
            time.sleep(.2)
        if p.poll() is None:
            if stop=='exited':stop='timeout_waiting_for_initialization'
            p.terminate()
        code=p.wait(timeout=5)
    text=log.read_text()
    missing=sorted(set(re.findall(r'Failed to load module L"([^"\n]+)"',text)))
    evidence=[s for s in text.splitlines() if any(x in s for x in [
        'dsp_ippv2','QuickFontCache_x64.dll','freetype_x64.dll','FruityPlug_x64.dll',
        'NATIVE_LOAD_EXCEPTION','NATIVE_EXCEPTION_STACK','CREATE_BEGIN','INFO sdk=',
        'RENDER finite=','SAVED_NATIVE_STATE','LOAD_FAILED'])]
    evidence_path=W/(label+'-native-load-evidence.log');evidence_path.write_text('\n'.join(evidence)+'\n')
    result=dict(name=name,SHA256=hashlib.sha256(plugin.read_bytes()).hexdigest(),exit_code=code,
                stop_reason=stop,missing_module_names=missing,
                native_CreatePlugInstance_reached='CREATE_BEGIN' in text,
                native_audio_render_reached='RENDER finite=' in text,
                evidence_log=str(evidence_path),elapsed_seconds=time.monotonic()-start)
    print(json.dumps(result),flush=True);return result
with concurrent.futures.ThreadPoolExecutor(2) as pool:results=list(pool.map(run,names))
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),QuickFontCache_uploaded=True,
 self_built_FreeType_present=True,private_audio_DSP_replacement_used=False,
 plugin_cases=results,all_cases_native_audio_render_reached=all(x['native_audio_render_reached'] for x in results),
 native_migration_complete=False,reference_match_reached=False)
(W/'NATIVE_EFFECTS_NEW_DEPENDENCY_TESTS.json').write_text(json.dumps(report,indent=2)+'\n')
