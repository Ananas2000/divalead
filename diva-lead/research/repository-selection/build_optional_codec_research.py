"""Build a pinned optional encoder for diagnostics; no system packages or boot changes."""
from pathlib import Path
import os,json,subprocess,datetime,hashlib,traceback
from concurrent.futures import ThreadPoolExecutor
W=Path(os.environ.get('DIVALEAD_VALIDATION_WORK','/workspace/divalead-work/all-repository-selection'));R=Path('/workspace/divalead-setup/codec-research/fdk-aac');B=R.parent/'build';STATE=W/'optional-codec-build-state.json'
def state(phase,**kw):
 row=dict(time_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller_PID=os.getpid(),phase=phase,diagnostic_only=True,match_reached=False,**kw);temp=STATE.with_suffix('.tmp');temp.write_text(json.dumps(row,indent=2));temp.replace(STATE)
try:
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert commit=='716f4394641d53f0d79c9ddac3fa93b03a49f278';B.mkdir(exist_ok=True);objects=B/'objects';objects.mkdir(exist_ok=True);includes=[arg for p in sorted(R.glob('lib*/include')) for arg in ['-I',str(p)]];sources=sorted(R.glob('lib*/src/*.cpp'));assert len(sources)>100;state('compiling_optional_pinned_FDK',source_commit=commit,files=len(sources),workers=2)
 def compile_source(p):
  obj=objects/(str(p.relative_to(R)).replace('/','_')+'.o')
  with obj.with_suffix('.log').open('w') as log:subprocess.run(['g++','-std=c++11','-O1','-fPIC','-fno-exceptions','-fno-rtti',*includes,'-c',str(p),'-o',str(obj)],stdin=subprocess.DEVNULL,stdout=log,stderr=log,check=True)
  return obj
 with ThreadPoolExecutor(max_workers=2) as pool:compiled=list(pool.map(compile_source,sources))
 library=B/'libfdk_aac_research.so';subprocess.run(['g++','-shared','-o',str(library),*[str(p) for p in compiled],'-lm'],check=True)
 text=(R/'aac-enc.c').read_text();needle='\n\tout = fopen(outfile, "wb");';assert text.count(needle)==1;text=text.replace(needle,'\n\tfprintf(stdout,"{\\"codec_delay\\":%u,\\"frame_length\\":%u,\\"input_channels\\":%u}\\n",info.nDelay,info.frameLength,info.inputChannels);\n'+needle);example=B/'aac-enc-info.c';example.write_text(text);binary=B/'aac-enc-info';subprocess.run(['gcc','-O2','-I',str(R),*includes,str(example),str(R/'wavreader.c'),'-L',str(B),'-lfdk_aac_research','-Wl,-rpath,'+str(B),'-lm','-o',str(binary)],check=True)
 state('completed_optional_encoder_build',source_commit=commit,binary=str(binary),library=str(library),library_SHA256=hashlib.sha256(library.read_bytes()).hexdigest(),no_system_or_boot_configuration_changed=True)
except Exception:
 state('failed',error=traceback.format_exc());raise
