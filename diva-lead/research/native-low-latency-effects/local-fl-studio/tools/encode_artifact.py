"""Encode one explicitly named workspace artifact for the authorized GitHub upload."""
from pathlib import Path
import base64, hashlib, json, sys
root=Path(__file__).resolve().parent.parent
path=(root/sys.argv[1]).resolve()
assert path.is_relative_to(root)
data=path.read_bytes()
offset=int(sys.argv[2]) if len(sys.argv)>2 else 0
length=int(sys.argv[3]) if len(sys.argv)>3 else len(data)
part=data[offset:offset+length]
git_blob_sha1=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
print(json.dumps(dict(path=sys.argv[1],bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=git_blob_sha1,offset=offset,chunk_bytes=len(part),base64=base64.b64encode(part).decode('ascii'))))
