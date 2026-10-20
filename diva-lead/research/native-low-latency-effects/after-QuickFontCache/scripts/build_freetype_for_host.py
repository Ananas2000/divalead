"""Rebuild the open-source GUI dependency, never substitute an audio DSP library."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys

W=Path(__file__).resolve().parent;S=Path('/workspace/divalead-setup')
source=W/'freetype-source';build=W/'freetype-build'
expected='42608f77f20749dd6ddc9e0536788eaad70ea4b5'
if not source.exists():
    subprocess.run(['git','clone','--depth','1','--branch','VER-2-13-3',
                    'https://github.com/freetype/freetype.git',str(source)],check=True)
assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==expected
cmake=W/'cmake-python/cmake/data/bin/cmake'
if not cmake.exists():
    subprocess.run([sys.executable,'-m','pip','install','--target',str(W/'cmake-python'),
                    '--no-deps','--no-cache-dir','cmake==3.31.6'],check=True)
compiler=S/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix'
windres=S/'sysroot/usr/bin/x86_64-w64-mingw32-windres'
wrapper=W/'freetype-cross-windres.sh'
wrapper.write_text('#!/bin/sh\nexec '+str(windres)+' --preprocessor='+str(compiler)+
                   ' --preprocessor-arg=-E --preprocessor-arg=-xc --preprocessor-arg=-DRC_INVOKED "$@"\n')
wrapper.chmod(0o700)
args=[str(cmake),'--fresh','-S',str(source),'-B',str(build),'-DCMAKE_SYSTEM_NAME=Windows',
      '-DCMAKE_C_COMPILER='+str(compiler),'-DCMAKE_RC_COMPILER='+str(wrapper),
      '-DCMAKE_BUILD_TYPE=Release','-DBUILD_SHARED_LIBS=ON','-DFT_DISABLE_ZLIB=TRUE',
      '-DFT_DISABLE_BZIP2=TRUE','-DFT_DISABLE_PNG=TRUE','-DFT_DISABLE_HARFBUZZ=TRUE',
      '-DFT_DISABLE_BROTLI=TRUE','-DCMAKE_SHARED_LINKER_FLAGS=-static-libgcc']
subprocess.run(args,check=True)
subprocess.run([str(cmake),'--build',str(build),'-j','2'],check=True)
shutil.copyfile(build/'libfreetype.dll',W/'freetype_x64.dll')
report=dict(source_repository='https://github.com/freetype/freetype.git',source_commit=expected,
    source_tag='VER-2-13-3',configure_command=args,
    built_DLL_SHA256=hashlib.sha256((W/'freetype_x64.dll').read_bytes()).hexdigest(),
    purpose='GUI font rendering dependency only; no audio DSP replacements',
    original_FL_binary_identical=False,audio_host_readiness_not_established_by_this_build=True)
(W/'FreeType-rebuild-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
