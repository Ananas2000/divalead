"""Split large audit ZIPs for connector transfer; no audio conversion."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parent.parent;S=R/'sessions/2026-10-24'
O=R/'divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24'
groups=[]
for name in('STATIC_TRIALS_AUDIO.zip','DYNAMIC_TRIALS_AUDIO.zip'):
    b=(O/name).read_bytes();parts=[]
    # Keep the original complete ZIP outside the checkout as well.
    (S/'audit-complete').mkdir(exist_ok=True);shutil.copyfile(O/name,S/'audit-complete'/name)
    for start in range(0,len(b),10*1024*1024):
        n=name+f'.part{len(parts)+1:02}';c=b[start:start+10*1024*1024];(O/n).write_bytes(c)
        parts.append(dict(file=n,bytes=len(c),sha256=hashlib.sha256(c).hexdigest()))
    groups.append(dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),parts=parts))
(O/'AUDIT_AUDIO_PARTS.json').write_text(json.dumps(groups,indent=2),encoding='utf-8')
join='''"""Join the lossless audit ZIP parts downloaded next to this script."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
for group in json.loads((root/'AUDIT_AUDIO_PARTS.json').read_text()):
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
(O/'join_audit_parts.py').write_text(join,encoding='utf-8')
for p in(S/'CONTINUE_RU.md',O/'README_RU.md'):
    text=p.read_text(encoding='utf-8').replace('[аудио static trials](STATIC_TRIALS_AUDIO.zip), [аудио dynamic trials](DYNAMIC_TRIALS_AUDIO.zip)','[части аудио static/dynamic trials](AUDIT_AUDIO_PARTS.json)')
    text=text.replace('ZIP распаковываются с сохранением','Для больших аудиоархивов скачать шесть `.partNN` из этой папки вместе с `AUDIT_AUDIO_PARTS.json` и запустить `python join_audit_parts.py`; SHA256 каждого фрагмента и собранного ZIP проверяется, данные не перекодируются. Основной полный комплект и инструменты доступны обычными ZIP. ZIP распаковываются с сохранением')
    p.write_text(text,encoding='utf-8')
print(json.dumps(groups,indent=2))
