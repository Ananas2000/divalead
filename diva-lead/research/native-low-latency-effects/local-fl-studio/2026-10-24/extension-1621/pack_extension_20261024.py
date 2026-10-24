"""Preserve the final bounded extension, including every actual rendered WAV."""
from joint_dynamic_extension_20261024 import *
import zipfile,hashlib,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=ROOT/'divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24/extension-1621';O.mkdir(exist_ok=True,parents=True)
groups=[json.loads((E/n).read_text())for n in('SCREEN.json','PHASE_SCREEN.json','OPPOSED_SCREEN.json','DETECTOR_SCREEN.json')]
fig,axes=plt.subplots(2,2,figsize=(11,7))
common=groups[0]['trials'];axes[0,0].plot([r['delta_db']for r in common],[-np.mean(r['improvements'])*1000 for r in common],'o-');axes[0,0].set(xlabel='Common target gain increase (dB)',ylabel='Loss change x1000',title='Two coincident Side dynamic peaks')
phase=[r for r in groups[1]['trials']if r['title']=='Freq19'];axes[0,1].plot([(r['after']/r['before']-1)*100 for r in phase],[np.mean(r['improvements'])*1000 for r in phase],'o-');axes[0,1].set(xlabel='Mid AllPass19 frequency change (%)',ylabel='Improvement x1000',title='Small phase sensitivity')
opp=[r for r in groups[2]['trials']if r['variant']['phase']==1];axes[1,0].plot([r['variant']['a']for r in opp],[np.mean(r['improvements'])*1000 for r in opp],'o-');axes[1,0].set(xlabel='Gain16 delta / opposite Gain17 delta (dB)',ylabel='Improvement x1000',title='Nearly flat difference coordinate')
top=[r['improvements']for r in groups[2]['trials']if r['variant']['phase']!=1][0];axes[1,1].bar(['Input 0','Input 1','Mean'],np.array([*top,np.mean(top)])*1000);axes[1,1].set(ylabel='Improvement x1000',title='Combined candidate: below acceptance floor')
for i,ax in enumerate(axes.ravel()):
    ax.axhline(0,color='gray',lw=.7);ax.grid(alpha=.2)
    if i>0:ax.axhline(.5,color='red',ls='--',label='Minimum acceptance floor');ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(E/'EXTENSION_DIAGNOSTICS.png',dpi=160);plt.close(fig)
prefixes=('JOINT_','EXTPHASE_','EXTOPP_','EXTDET_')
audio=[p for p in R.glob('*.wav')if p.name.startswith(prefixes)]
assert len(audio)==57,len(audio)
archive=E/'EXTENSION_AUDIO.zip';manifest=[]
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
    for p in sorted(audio):
        arc='local-fl-matching/'+p.relative_to(ROOT).as_posix();z.write(p,arc);manifest.append(dict(path=arc,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
with zipfile.ZipFile(archive)as z:assert z.testzip()is None
(O/'AUDIO_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
data=archive.read_bytes();parts=[]
for start in range(0,len(data),10*1024*1024):
    name=f'EXTENSION_AUDIO.zip.part{len(parts)+1:02}';chunk=data[start:start+10*1024*1024];(O/name).write_bytes(chunk);parts.append(dict(file=name,bytes=len(chunk),sha256=hashlib.sha256(chunk).hexdigest()))
desc=[dict(file='EXTENSION_AUDIO.zip',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),parts=parts)]
(O/'EXTENSION_AUDIO_PARTS.json').write_text(json.dumps(desc,indent=2))
join='''from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
for group in json.loads((root/'EXTENSION_AUDIO_PARTS.json').read_text()):
    chunks=[]
    for part in group['parts']:
        data=(root/part['file']).read_bytes()
        assert len(data)==part['bytes'] and hashlib.sha256(data).hexdigest()==part['sha256']
        chunks.append(data)
    data=b''.join(chunks)
    assert len(data)==group['bytes'] and hashlib.sha256(data).hexdigest()==group['sha256']
    out=root/group['file']
    if out.exists():assert out.read_bytes()==data
    else:out.write_bytes(data)
    print(out.name,len(data),group['sha256'])
'''
(O/'join_extension_audio.py').write_text(join)
scripts=['joint_dynamic_extension_20261024.py','phase_extension_20261024.py','opposed_extension_20261024.py','detector_extension_20261024.py','pack_extension_20261024.py']
meta=[p for p in E.iterdir()if p.is_file()and p.suffix.lower()in('.json','.tsv','.bin','.flp','.log','.md','.png')]
meta += [p for p in(S/'assessment').glob('*.json')if p.name.startswith(prefixes)]
meta += [ROOT/'tools'/n for n in scripts]
with zipfile.ZipFile(O/'EXTENSION_REPORTS_AND_STATES.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
    for p in meta:z.write(p,'local-fl-matching/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(O/'EXTENSION_REPORTS_AND_STATES.zip')as z:assert z.testzip()is None
for p in E.iterdir():
    if p.is_file()and p.suffix.lower()in('.json','.md','.png'):shutil.copyfile(p,O/p.name)
for name in scripts:shutil.copyfile(ROOT/'tools'/name,O/name)
print(json.dumps(dict(audio_files=len(audio),audio_archive_bytes=len(data),parts=len(parts),archive_sha256=desc[0]['sha256'],reports_bytes=(O/'EXTENSION_REPORTS_AND_STATES.zip').stat().st_size),indent=2))
