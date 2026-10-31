"""Recreate ephemeral audio tooling from the prepared snapshot and verified sources.

Never changes BEST, source presets, MIDI, private references, or the checkout.
Existing Wine/MinGW, uploaded DLLs and the Python environment are prerequisites.
"""
from pathlib import Path
import csv,datetime,hashlib,json,os,shutil,subprocess,sys

T=Path(__file__).resolve().parent
P=Path('/workspace/divalead');S=Path('/workspace/divalead-setup')
H=T.parent/'stereo-refinement-20261026'
PUBLIC=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
AFTER=P/'diva-lead/research/native-low-latency-effects/after-DSP-arrival/scripts'
W=Path('/tmp/divalead-native-effects');B=Path('/tmp/divalead-local-1625');D=B/'internet-plugins-20261023'
ZL_SHA='3269c63a7b6c4a2cc38b249c3678efaf2759ea4a71a299020e3b67a96595028d'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
copies=[
 (PUBLIC/'stereo-repair-GUI-native-20261024/scripts/native_chain.py',W/'native_chain.py'),
 (AFTER/'apply_native_candidate.py',W/'apply_native_candidate.py'),
 (AFTER/'fl_native_chain_host.c',W/'fl_native_chain_host.c'),
 (PUBLIC/'scripts/fl_native_fl20_host.c',W/'fl_native_fl20_host.c'),
 (PUBLIC/'original-bipolar-even8-full39/current-runtime/fl20_curve.py',B/'fl20_curve.py'),
 (PUBLIC/'scripts/fl20_objective.py',B/'fl20_objective.py'),
 (PUBLIC/'scripts/fl20_diva_wrapper.py',B/'fl20_diva_wrapper.py'),
 (PUBLIC/'ZL23-validated-continuation/scripts/watch_ZL_useful_complete_backups.py',D/'watch_ZL_useful_complete_backups.py'),
]
plugin=D/'ZL Equalizer 2.vst3/Contents/x86_64-win/ZL Equalizer 2.vst3'
critical=[W/'fl_native_chain_host.exe',W/'fl_native_fl20_host.exe',D/'vst3_effect_host.exe',D/'ZL-default-parameters.tsv',W/'wine/drive_c/windows/system32/zlib1.dll',B/'runtime/analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json',W/'xvfb-verified/usr/bin/Xvfb']
ready=all(p.is_file()for p in critical)and plugin.is_file()and sha(plugin)==ZL_SHA and all(dst.is_file()and sha(src)==sha(dst)for src,dst in copies)

def run(args,**kwargs):return subprocess.run([str(x)for x in args],check=True,**kwargs)
def active_hosts():
 rows=[]
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   args=[x.decode(errors='replace')for x in p.read_bytes().split(b'\0')if x]
   names=[x.replace('\\','/').rsplit('/',1)[-1]for x in args]
   if any(x=='vst3_effect_host.exe'or(x.startswith('fl_native_')and x.endswith('.exe'))for x in names):rows.append(int(p.parent.name))
  except OSError:pass
 return rows

if not ready:
 assert not active_hosts(),'Preserve live audio hosts; diagnose mismatched runtime files without overwriting them'
 for p in [S/'sysroot/usr/lib/wine/wine64',S/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix',T.parent/'native-low-latency-effects/runtime/freetype_x64.dll']:
  assert p.is_file(),f'Prepared snapshot prerequisite missing: {p}'
 run([sys.executable,'-B',AFTER/'prepare_native_runtime.py'])
 W.mkdir(exist_ok=True)
 if not(W/'xvfb-verified/usr/bin/Xvfb').is_file():
  shutil.copyfile(AFTER/'verify_xvfb_package.py',W/'verify_xvfb_package.py')
  run([sys.executable,'-B',W/'verify_xvfb_package.py'])
  run(['dpkg-deb','-x',W/'xvfb-verified.deb',W/'xvfb-verified'])
 run([sys.executable,H/'start_native_headless_display.py'])
 if not(B/'runtime').exists():
  run([sys.executable,'-B',P/'diva-lead/research/native-low-latency-effects/local-fl-studio/tools/restore_checkpoint.py','--destination',B/'runtime'])
 if not D.exists():
  run([sys.executable,'-B',PUBLIC/'external-plugins-20261023-02/scripts/setup_ZL_runtime.py','--destination',D])
 assert plugin.is_file()and sha(plugin)==ZL_SHA,'Pinned official ZL package must be verified; never silently replace it'
 for src,dst in copies:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 cc=S/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix'
 common=[cc,'--sysroot='+str(S/'sysroot'),'-B'+str(S/'sysroot/usr/lib/gcc/x86_64-w64-mingw32/14-posix/'),'-L'+str(S/'sysroot/usr/x86_64-w64-mingw32/lib'),'-O3','-static','-Wl,--no-insert-timestamp']
 for src,exe,flags in [('fl_native_chain_host.c','fl_native_chain_host.exe',[]),('fl_native_fl20_host.c','fl_native_fl20_host.exe',['-DFL_PRESET_GRAPH','-DCOMMON_PHASE_PAIR'])]:
  run([*common,*flags,W/src,'-o',W/exe,'-lole32','-luuid','-lm'])
 prefix=W/'wine';system=prefix/'drive_c/windows/system32';system.mkdir(parents=True,exist_ok=True)
 zlib=S/'sysroot/usr/x86_64-w64-mingw32/lib/zlib1.dll';shutil.copyfile(zlib,system/'zlib1.dll');assert sha(zlib)==sha(system/'zlib1.dll')
 env=dict(os.environ,WINEPREFIX=str(prefix),WINEARCH='win64',WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(W/'cache'))
 marker=run([S/'sysroot/usr/lib/wine/wine64','cmd','/c','echo DIVALEAD_PREFIX_READY'],env=env,text=True,capture_output=True,timeout=60)
 assert 'DIVALEAD_PREFIX_READY'in marker.stdout
 sys.path.insert(0,str(D));from win_vst3 import WinVST3
 host=WinVST3('restore-actual-param-map-'+str(os.getpid()))
 try:host.dump(D/'ZL-default-parameters.tsv')
 finally:host.close()
else:
 run([sys.executable,H/'start_native_headless_display.py'])

assert all(p.is_file()for p in critical)and sha(plugin)==ZL_SHA
assert all(sha(src)==sha(dst)for src,dst in copies)
rows=list(csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t'))
assert len(rows)==610 and len({r['id']for r in rows})==610
for title in ['Output Gain','Freq20','Q22','Side Freq21']:assert sum(r['title']==title for r in rows)==1
for row in json.loads((W/'staged-plugin-manifest.json').read_text()):assert sha(row['staged'])==row['SHA256']
assert 'INPUT_LOADED'in(W/'fl_native_chain_host.c').read_text()
assert '78,80,86,94,95'in(W/'apply_native_candidate.py').read_text()
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),runtime_was_already_valid=ready,official_ZL_SHA256=sha(plugin),native_input_switch_protocol_current=True,native95_and_WS52_high4_runtime_current=True,native11_bipolar_even8_runtime_current=True,parameter_map610_ids_verified=True,all_supplied_native_DLL_hashes_verified=True,live_hosts_preserved=True,source_and_BEST_unchanged=True,real_audio_readiness_must_be_exercised_separately=True,sources=[dict(source=str(src),destination=str(dst),SHA256=sha(dst))for src,dst in copies])
(T/'TMP_RUNTIME_RESTORATION_PROVENANCE.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({k:v for k,v in proof.items()if k!='sources'}),flush=True)
