from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
for group in json.loads((root/'FRESH_VALIDATION_PARTS.json').read_text()):
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
