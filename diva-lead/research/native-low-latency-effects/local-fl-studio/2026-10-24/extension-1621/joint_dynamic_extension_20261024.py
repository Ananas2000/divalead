"""One bounded joint dynamic-band experiment during the final 20-minute window."""
from experiment_20261024 import *
import struct
import cloud_native_fst as f
E=S/'extension-1621';E.mkdir(exist_ok=True)
def embed(component,dest):
    original=(V/'ZL_component.bin').read_bytes();new=Path(component).read_bytes()
    p=f.parse((U/'Diva_ZL_23_WIP.flp').read_bytes());events=[];changed=0
    for ident,v in p['events']:
        if ident==213 and original in v:
            out=v[:4];off=4
            while off<len(v):
                key,n=struct.unpack_from('<iQ',v,off);off+=12;b=v[off:off+n];off+=n
                if key==53:
                    assert b.endswith(original);head=b[:-len(original)];assert struct.unpack_from('<Q',head,len(head)-8)[0]==len(original)
                    b=head[:-8]+struct.pack('<Q',len(new))+new;changed+=1
                out+=struct.pack('<iQ',key,len(b))+b
            v=out
        events.append(f.event(ident,v))
    assert changed==1;Path(dest).write_bytes(f.container(p['format'],b''.join(events),p['channels']))
def run():
    params={v['title']:v for v in csv.DictReader((S/'ZL23_CONFIRMED_ALL610.tsv').open(),delimiter='\t')}
    inputs=[sf.read(S/f'FL26_PRE_ZL_{i:02}.wav',dtype='float32',always_2d=True)[0]for i in range(2)]
    z=WinVST3('joint24');rows=[]
    try:
        baseline=[]
        for i,x in enumerate(inputs):
            z.load(PRIVATE);baseline.append(evaluate(z,x,f'JOINT_CONTROL_{i}'))
        for delta in(.5,1.,2.,3.,4.,6.,8.):
            pair=[]
            for i,x in enumerate(inputs):
                z.load(PRIVATE)
                for band in(16,17):
                    p=params[f'Target Gain{band}'];z.text(int(p['id']),f"{float(p['display'])+delta:.2f}")
                pair.append(evaluate(z,x,f'JOINT_D{delta:g}_TRAIN_{i}'))
            row=dict(delta_db=delta,rows=pair,mean_loss=float(np.mean([r['loss']for r in pair])),improvements=[b['loss']-r['loss']for b,r in zip(baseline,pair)])
            rows.append(row);print(json.dumps(row),flush=True)
            (E/'SCREEN.json').write_text(json.dumps(dict(baseline=baseline,trials=rows,promoted=False),indent=2))
        best=min(rows,key=lambda r:r['mean_loss']);z.load(PRIVATE)
        for band in(16,17):
            p=params[f'Target Gain{band}'];z.text(int(p['id']),f"{float(p['display'])+best['delta_db']:.2f}")
        candidate=E/'JOINT_CANDIDATE.bin';z.save(candidate);z.dump(E/'JOINT_CANDIDATE610.tsv');embed(candidate,E/'JOINT_CANDIDATE_FL20.flp')
        (E/'CANDIDATE.json').write_text(json.dumps(dict(best=best,promoted=False,acceptance='Must gain > max(.0005,3SEM), six fresh paired inputs and two cold inputs, component roundtrip and GUI render'),indent=2))
    finally:
        z.close();(E/'TRAIN_HOST.log').write_text('\n'.join(str(v)for v in z.transcript),encoding='utf-8')
if __name__=='__main__':run()
