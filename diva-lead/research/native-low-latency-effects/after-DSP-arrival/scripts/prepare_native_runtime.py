"""Restore this research host from private uploads and public source files.

Does not distribute Image-Line libraries or emulate their DSP/licensing.
Run only while no native fitting host is using the runtime executables.
Existing Wine and verified Xvfb setup remain prerequisites.
"""
from pathlib import Path
import hashlib,json,shutil,struct,subprocess,sys
W=Path('/tmp/divalead-native-effects');W.mkdir(exist_ok=True)
HERE=Path(__file__).resolve().parent
active=[]
for path in Path('/proc').glob('[0-9]*/cmdline'):
    try:
        args=path.read_bytes().split(b'\0');first=args[0].decode(errors='replace')
        if first.startswith(str(W)+'/') and first.endswith('.exe'):active.append(int(path.parent.name))
    except (FileNotFoundError,ProcessLookupError,PermissionError):continue
assert not active,f'Refusing to rebuild while native hosts exist: {active}'
for name in ['fl_native_chain_host.c','fl_native_probe.c','native_chain.py','native_features.py','native_harmonic_features.py','native_original_objective.py','apply_native_candidate.py','native_fst.py','export_native_checkpoint.py','export_native_chorus_checkpoint.py','complete_native_checkpoint.py','verify_native_latency_blocks.py','verify_fst_with_pyflp.py','search_native_chorus.py','search_native_chorus_controls.py','continue_native_chorus.py','fit_native_harmonic.py','fit_native_joint.py','search_native_coordinates.py','assess_native_reference.py','compare_to_v83.py','extract_dsp_archive.py','Fruity_WaveShaper_x64-default-state.bin']:
    src=HERE/name
    if src.resolve()!=(W/name).resolve():shutil.copyfile(src,W/name)
for name in ['start_native_chorus.py','native_cpu_slots.py','publish_native_progress.py']:
    src=HERE/name
    if src.is_file() and src.resolve()!=(W/name).resolve():shutil.copyfile(src,W/name)
manifest=json.loads((HERE/'staged-plugin-manifest.json').read_text())
for row in manifest:
    src=Path(row['original']);assert hashlib.sha256(src.read_bytes()).hexdigest()==row['SHA256']
    dst=Path(row['staged']);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    if row['placeholder_visual_palette']:
        # A synthetic GUI-only gradient; the supplied audio DLL is untouched.
        a=dst.parent/'Artwork';a.mkdir(exist_ok=True);width,height=512,256
        pixels=bytearray()
        for y in range(height):
            for x in range(width):pixels.extend((int(255*x/(width-1)),int(255*y/(height-1)),int(255*(1-x/(width-1)))))
        header=struct.pack('<2sIHHI',b'BM',54+len(pixels),0,0,54)+struct.pack('<IiiHHIIiiII',40,width,height,1,24,0,len(pixels),2835,2835,0,0)
        (a/'Spectrum.bmp').write_bytes(header+pixels)
(W/'staged-plugin-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
rar=Path('/workspace/attachments/e7dc0509-3eae-44dd-9ab7-44302ae95c37/dsp_ippv2_x64.rar')
assert hashlib.sha256(rar.read_bytes()).hexdigest()=='ffc08015f5f025b8c625a5936bc9251aac54bd02eec3696549b9bbf236729d29'
subprocess.run([sys.executable,'-B',str(W/'extract_dsp_archive.py'),str(rar)],check=True)
assert hashlib.sha256((W/'dsp_ippv2_x64.dll').read_bytes()).hexdigest()=='9ba8a03bf803b2ffd1165cafd55ccf4c51dddef52704a297112f47ef7df8bfbb'
q=Path('/workspace/attachments/e9c99597-edf7-4aae-9ae0-5c3aff1ac188/QuickFontCache_x64.dll')
shutil.copyfile(q,W/q.name)
free=Path('/workspace/divalead-work/native-low-latency-effects/runtime/freetype_x64.dll')
assert free.is_file(),'Rebuild FreeType with the previous verified build helper first'
shutil.copyfile(free,W/free.name)
cc='/workspace/divalead-setup/sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix'
for exe,defines in [('fl_native_chain_host.exe',[]),('fl_native_fl_graph_host.exe',['-DFL_PRESET_GRAPH']),('fl_native_chorus_verified_host.exe',['-DFL_PRESET_GRAPH']),('fl_native_source_variants_host.exe',['-DFL_PRESET_GRAPH'])]:
    subprocess.run([cc,'-O3','-static-libgcc','-Wl,--no-insert-timestamp',*defines,'-o',str(W/exe),str(W/'fl_native_chain_host.c'),'-lole32','-luuid','-lm'],check=True)
import numpy as np,soundfile as sf
x,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_SOURCE_FROZEN_48k.wav',dtype='float32',always_2d=True);assert sr==48000
sf.write(W/'native-frozen-source-with-tail.wav',np.pad(x,((0,32768),(0,0))),sr,subtype='FLOAT')
print('NATIVE_RUNTIME_STAGED; verify Xvfb/Wine and do a real render next')
