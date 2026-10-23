"""Rebuild the official external-VST3 runtime in a new private directory.

Run after the repository's existing Wine/MinGW/native-effects setup. Downloads
only the official pinned MSI; does not install it into Wine or overwrite an
existing runtime. Plugin bytes and SDK declarations are not redistributed.
"""
from pathlib import Path
import argparse,hashlib,io,json,os,shutil,subprocess,sys,urllib.request
ap=argparse.ArgumentParser();ap.add_argument('--destination',required=True);args=ap.parse_args()
src=Path(__file__).resolve().parent;dest=Path(args.destination).resolve();dest.mkdir(exist_ok=False)
S=Path('/workspace/divalead-setup')
URL='https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi'
MSI_SHA='4410231ca0f739bc73646006701ae6b64d553910b8abc969575e562dc1cf79b7'
DLL_SHA='3269c63a7b6c4a2cc38b249c3678efaf2759ea4a71a299020e3b67a96595028d'
for name in ['vst3_effect_host.c','win_vst3.py','fl20_vst3_state.py']:shutil.copyfile(src/name,dest/name)
deps=dest/'pytools'
subprocess.run([sys.executable,'-m','pip','install','--no-cache-dir','--target',str(deps),'olefile==0.47','libarchive-c==5.3'],check=True)
sys.path.insert(0,str(deps));import olefile,libarchive
msi=dest/'ZL.Equalizer.2-1.4.1-Windows-x86-64.msi'
with urllib.request.urlopen(URL,timeout=60)as r,msi.open('wb')as f:shutil.copyfileobj(r,f)
assert hashlib.sha256(msi.read_bytes()).hexdigest()==MSI_SHA
bundle=dest/'ZL Equalizer 2.vst3';binary=bundle/'Contents/x86_64-win/ZL Equalizer 2.vst3';resources=bundle/'Contents/Resources'
binary.parent.mkdir(parents=True);resources.mkdir()
ids={'ID_7B5010438866CD38BC685ECA00BD6EA5':binary,'ID_F74AF367798C39606968244577A9BEE6':resources/'moduleinfo.json'}
found={}
with olefile.OleFileIO(msi)as ole:
    for stream in ole.listdir():
        data=ole.openstream(stream).read()
        if not data.startswith(b'MSCF'):continue
        with libarchive.memory_reader(data)as archive:
            for item in archive:
                if item.pathname in ids:
                    blob=b''.join(item.get_blocks());ids[item.pathname].write_bytes(blob);found[item.pathname]=hashlib.sha256(blob).hexdigest()
assert set(found)==set(ids)and hashlib.sha256(binary.read_bytes()).hexdigest()==DLL_SHA
command=[str(S/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix'),'--sysroot='+str(S/'sysroot'),
    '-B'+str(S/'sysroot/usr/lib/gcc/x86_64-w64-mingw32/14-posix/'),'-L'+str(S/'sysroot/usr/x86_64-w64-mingw32/lib'),
    '-O2','-static','-Wl,--no-insert-timestamp',str(dest/'vst3_effect_host.c'),'-o',str(dest/'vst3_effect_host.exe'),'-lole32','-luser32','-lm']
subprocess.run(command,check=True)
receipt=dict(official_URL=URL,official_version='1.4.1',MSI_SHA256=MSI_SHA,DLL_SHA256=DLL_SHA,compiler_command=command,
    component_class_ID='ABCDEF019182FAEB5A6C697545717532',downloaded_and_built_only=True,
    existing_Wine_native_runtime_unmodified=True,actual_plugin_execution_is_a_separate_check=True)
(dest/'BOOTSTRAP_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
