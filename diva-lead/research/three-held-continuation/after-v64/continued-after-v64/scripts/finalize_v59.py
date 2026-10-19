from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile,os
R=Path(__file__).resolve().parent;T=R/'v59-build';D=T/'v59-wip';V=D/'verification'
p=D/'FL_STUDIO_RU.md';p.write_text(p.read_text().replace('Это промежуточный результат после v57','Это продолжение выбранного трёхнотного варианта v58'))
for a,b in [('spectral-proof.json','packaged_spectral_verification.json'),('release-proof.json','packaged_release_verification.json'),('fresh-source-proof.json','standalone_fresh_source_verification.json')]:
 json.loads((T/a).read_text());shutil.copyfile(T/a,V/b)
# Rebuild the actual published image at a new output path, compare every byte.
compiler='/workspace/divalead-setup/sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix'
out=T/'exact-rebuild'/'Diva_Lead_Finish_v59_WIP_x64.dll';out.parent.mkdir(exist_ok=True)
subprocess.run([compiler,'-O3','-shared','-static-libgcc','-Wl,--no-insert-timestamp','-Wl,--image-base,0x359590000','-o',str(out),str(D/'analysis/lead_finish.c'),'-lm'],check=True)
assert out.read_bytes()==(D/'Diva_Lead_Finish_v59_WIP_x64.dll').read_bytes()
(V/'exact_rebuild.json').write_text(json.dumps(dict(byte_exact_rebuild=True,image_base='0x359590000',DLL_SHA256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2)+'\n')
# Do not accidentally ship compiler products, caches or the user's Diva binary.
files=sorted(p for p in D.rglob('*') if p.is_file())
assert all(p.suffix not in ['.pyc','.so','.exe','.vst3'] and '__pycache__' not in p.parts for p in files)
(D/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(D))+'\n' for p in files))
archive=T/'Diva_lead_v59_WIP_checkpoint.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(D.rglob('*')):
  if p.is_file():z.write(p,str(p.relative_to(T)))
Q=Path('/tmp/divalead-v59-clean-extraction');Q.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 z.extractall(Q)
clean=Q/'v59-wip';env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
with (T/'clean-extraction-proof.json').open('w') as log:subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(clean/'analysis/verify_release.py')],stdout=log,env=env,check=True)
manifest=[]
for p in sorted(D.rglob('*')):
 if p.is_file():
  relative=str(p.relative_to(D));assert p.read_bytes()==(clean/relative).read_bytes();manifest.append(relative)
(T/'ZIP-proof.json').write_text(json.dumps(dict(ZIP_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),ZIP_bytes=archive.stat().st_size,members=len(manifest),all_extracted_files_byte_equal=True,clean_extraction_release_replay_passed=True,byte_exact_DLL_rebuild=True,match_reached=False),indent=2)+'\n')
print('V59_ARCHIVE_AND_CLEAN_EXTRACTION_PASS',archive,flush=True)
