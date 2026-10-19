"""Fresh Diva oscillator/filter tuning; three held notes and envelopes locked."""
from pathlib import Path
import os,sys,json,hashlib,re,subprocess,ctypes,shutil,copy
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parent;B=ROOT/'baseline';F=ROOT/'verified-hf1';V=ROOT/'source-fine';V.mkdir(exist_ok=False)
P=Path('/workspace/divalead/diva-lead/research/repository-selection');sys.path.insert(0,str(P));import compare_all as a
a.WORK=V;(V/'scores').mkdir();base=json.loads((B/'validation.json').read_text());scales=json.loads((P/'ranking.json').read_text())['normalizing_errors']
weights=dict(H24=.30,upper_harm=.25,ERB=.20,low_harm=.10,upper_off=.10,relative_phase=.05)
guards=dict(H24=1.001,upper_harm=1.001,upper_off=1.001,ERB=1.001,low_harm=1.002,relative_phase=1.005,whole=1.003,envelope=1.003,body=1.02,stereo_phase=1.005,stereo_balance=1.005)
crest_cap=base['crest_RMS_dB']*1.002
lib=ctypes.CDLL(str(F/'native_finish.so'));lib.native_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
data=(B/'Diva_THREE_HELD_BASELINE.h2p').read_bytes();expected=json.loads((B/'MIDI_events_48k.json').read_text())
setup=Path('/workspace/divalead-setup');env=os.environ.copy();env.update(WINEPREFIX=str(setup/'wine2'),WINEDLLPATH=str(setup/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',XDG_CACHE_HOME=str(setup/'cache'))
def win(p):return 'Z:'+str(p).replace('/','\\')
def write(p,x):
 q=p.with_suffix('.tmp');q.write_text(json.dumps(x,indent=2)+'\n');q.replace(p)
history=[];cache={};best=None
def evaluate(fields,label):
 global best
 key=json.dumps(fields,sort_keys=True)
 if key in cache:return cache[key]
 index=len(history);case=V/('trial-'+format(index,'03d'));case.mkdir();preset=case/'source.h2p';patched=data
 for key,value in fields.items():
  module,name=key.split(':');start=patched.index(('#cm='+module+'\n').encode())+len('#cm='+module+'\n');end=patched.find(b'#cm=',start);end=len(patched) if end<0 else end
  segment,n=re.subn(rb'(?m)^'+re.escape(name.encode())+rb'=[^\r\n\x00]*',(name+'='+format(value,'.2f')).encode(),patched[start:end]);assert n==1;patched=patched[:start]+segment+patched[end:]
 preset.write_bytes(patched);rawpath=V/'current-Diva.wav';dump=case/'all281.tsv'
 commands='\n'.join(['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(dump),'render '+win(rawpath),'quit'])+'\n';(case/'commands.txt').write_text(commands)
 with (case/'Diva.log').open('w') as log:subprocess.run([str(setup/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(preset)],input=commands,text=True,env=env,stdout=log,stderr=log,timeout=90,check=True)
 events=[list(map(int,s.split()[1:])) for s in (case/'Diva.log').read_text().splitlines() if s.startswith('NOTE ')];assert events==expected
 dry,rate=sf.read(rawpath,dtype='float32');assert rate==48000 and dry.shape==(288000,2)
 out=np.zeros_like(dry);assert lib.native_render(dry.ctypes.data,out.ctypes.data,len(dry),48000)
 edit=a.h.edit_aligned(a.h.align_with_pdc(out.astype('float64'),dict(alignment_frames=819),latency=12416));editfile=V/'current-edit.wav';sf.write(editfile,edit,48000,subtype='FLOAT')
 measured=a.score(dict(id='source'+str(index),canonical_path=str(editfile),aliases=[]));m=measured['metrics'];tone=sum(weights[k]*m[k]/scales[k] for k in weights);score=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS);crest=measured['diagnostics']['crest_RMS_db']
 feasible=bool(all(m[k]<=base['metrics'][k]*limit for k,limit in guards.items()) and crest<=crest_cap and score<=base['score']*1.0001 and np.max(abs(out))<.99)
 row=dict(index=index,label=label,fields=fields,tone_score=tone,score=score,metrics=m,crest_RMS_dB=crest,feasible=feasible,guards_relative_to_user_chosen_three=guards,crest_cap_dB=crest_cap,source_preset=str(preset),raw_SHA256=hashlib.sha256(dry.tobytes()).hexdigest(),original_six_input_note_on_events_unchanged=True,arpeggiator_and_envelopes_locked=True,changed_source_needs_new_own_independent_base=bool(fields),match_reached=False)
 if index==0:
  assert not fields;np.testing.assert_array_equal(dry,sf.read(B/'Diva_source.wav',dtype='float32')[0]);np.testing.assert_allclose(out,sf.read(F/'actual-Windows.wav',dtype='float32')[0],rtol=0,atol=2e-7)
 history.append(row);cache[json.dumps(fields,sort_keys=True)]=row;write(case/'result.json',row);write(V/'history.json',history)
 if feasible and (best is None or tone<best['tone_score']):
  best=row;dest=V/'best';dest.mkdir(exist_ok=True);shutil.copyfile(preset,dest/'source.h2p');shutil.copyfile(dump,dest/'all281.tsv');sf.write(dest/'Diva_source.wav',dry,48000,subtype='FLOAT');sf.write(dest/'native-WITH_PDC.wav',out,48000,subtype='FLOAT');sf.write(dest/'REFERENCE_EDIT_WIP.wav',edit,48000,subtype='FLOAT');write(dest/'selection.json',row)
 print('THREE_SOURCE',index,label,'tone',tone,'score',score,'feasible',feasible,flush=True);return row
current=evaluate({},'user-selected source with proved HF1')
for field,values in [('OSC:PW',[51.77,51.82,51.92,51.97]),('OSC:OscMix',[5.47,5.62,5.82,5.97]),('VCF1:Res',[11.89,12.04,12.24,12.39]),('VCF1:Freq',[143.87,144.02,144.32,144.47]),('OSC:Tune2',[24.,24.01,24.03,24.04]),('VCF1:KeyScl',[7.88,8.18,8.58,8.88])]:
 origin=copy.deepcopy(current);choices=[current]
 for value in values:
  fields=copy.deepcopy(origin['fields']);fields[field]=value;choices.append(evaluate(fields,field+'='+str(value)))
 current=min([r for r in choices if r['feasible']],key=lambda r:r['tone_score'])
write(V/'completed.json',dict(best=best,trials=len(history),match_reached=False));print('SOURCE_FINE_COMPLETE',len(history),best['tone_score'],best['score'],flush=True)
