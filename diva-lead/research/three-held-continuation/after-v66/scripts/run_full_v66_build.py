from pathlib import Path
import os,sys,json,subprocess
R=Path(__file__).resolve().parent;env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');PY=sys.executable
selected=json.loads(subprocess.check_output([PY,'-B',str(R/'auto_backup_three.py'),'--check-only'],env=env,text=True));selected['validation']=selected['best'];S=Path(selected['best']).parent
subprocess.run([PY,'-B',str(R/'build_three_v66.py'),str(S)],env=env,check=True)
T=R/'v66-build';D=T/'v66-wip';(T/'selected-basis.json').write_text(json.dumps(selected,indent=2)+'\n')
subprocess.run([PY,'-B',str(R/'write_v66_docs.py')],env=env,check=True)
compiler='/workspace/divalead-setup/sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix'
subprocess.run([compiler,'-O2','-static-libgcc','-o',str(T/'source-host.exe'),str(D/'analysis/diva_source_render_host.c'),'-lm'],check=True)
for script,args,output in [('analysis/replay_source.py',['--wine','/workspace/divalead-setup/sysroot/usr/lib/wine/wine64','--host',str(T/'source-host.exe'),'--plugin','/workspace/attachments/6a76beaa-924d-4f2e-8491-512d9b487af2/Diva(x64).vst3','--wine-prefix','/workspace/divalead-setup/wine2','--wine-dll-path','/workspace/divalead-setup/sysroot/usr/lib/x86_64-linux-gnu/wine','--output',str(T/'fresh-source-replay')],'fresh-source-proof.json'),('analysis/verify_spectral.py',['--fixtures'],'spectral-proof.json'),('analysis/verify_release.py',[],'release-proof.json')]:
    with (T/output).open('w') as log:subprocess.run([PY,'-B',str(D/script),*args],env=env,stdout=log,check=True)
subprocess.run([PY,'-B',str(R/'finalize_v66.py')],env=env,check=True)
subprocess.run([PY,'-B',str(R/'verify_zip_windows_v66.py')],env=env,check=True)
print('V66_FULL_BUILD_AND_ALL_FRESH_TESTS_COMPLETE',S,flush=True)
