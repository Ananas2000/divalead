"""Verify exact saved GUI Diva controls and embedded accepted ZL component."""
from pathlib import Path
import struct,json,subprocess,gzip,csv,io,hashlib
R=Path(__file__).resolve().parent.parent;S=R/'sessions/2026-10-24'
d=(S/'Diva_ZL23_BEST_FL26.flp').read_bytes();j=d.index(b'/*@Meta')
matches=[o for o in range(j-100,j)if d[o:o+4]==struct.pack('<i',53)]
assert len(matches)==1;off=matches[0];i,n=struct.unpack_from('<iQ',d,off)
assert off+12+n<=len(d)
p=S/'Diva_ZL23_BEST_FL26.h2p';p.write_bytes(d[j:off+12+n].rstrip(b'\0'))
proc=subprocess.run([str(R/'tools/native-host/diva_source_render_host.exe'),r'C:\Program Files\VstPlugins\Diva(x64).dll',str(p.relative_to(R))],cwd=R,input='dump sessions/2026-10-24/BEST_FL26_ALL281.tsv\nquit\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW,timeout=20)
(S/'BEST_DIVA_VERIFY.log').write_text(proc.stdout,encoding='utf-8');assert proc.returncode==0
a=list(csv.DictReader((S/'BEST_FL26_ALL281.tsv').open(),delimiter='\t'))
b=list(csv.DictReader(io.StringIO(gzip.decompress((S/'ZL23_upstream/FL20_ZL_23_WIP/verification/all281.tsv.gz').read_bytes()).decode()),delimiter='\t'))
assert len(a)==len(b)==281
delta=max(abs(float(x['normalized'])-float(y['normalized']))for x,y in zip(a,b))
c=(S/'ZL23_CONFIRMED_INPUT.bin').read_bytes()
report=dict(counts=[len(a),len(b)],max_normalized_delta=delta,all281_exact=delta==0,ZL_confirmed_component_embedded_exactly_once=d.count(c)==1,ZL_resaved_byte_exact=c==(S/'ZL23_CONFIRMED_RESAVED.bin').read_bytes(),preset_name_visible_and_embedded=d.count(b'Diva_ZL23_20261024')==1,flp_sha256=hashlib.sha256(d).hexdigest(),FL26_parser_limitation='FL26 event172 layout not handled by old FL20 parser; bytes not altered; bounded unique TLV53 extraction checked')
assert report['all281_exact'] and report['ZL_confirmed_component_embedded_exactly_once']
(S/'BEST_FLP_VERIFICATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
