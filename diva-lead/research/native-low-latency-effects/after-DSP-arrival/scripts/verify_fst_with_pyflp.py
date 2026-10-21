"""Independent container check using PyFLP, with an explicit Python 3.12 fix.

No PyFLP code is distributed here. Its original binary-format parser is used.
The tiny metaclass shim handles Python 3.12 refusing empty Enum base classes;
the same shim is first tested against PyFLP's stock Soft Clipper/insert fixtures.
This is not an FL Studio GUI test.
"""
from pathlib import Path
import hashlib,json,sys
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'pyflp-source'))
import pyflp
from pyflp._events import _EventEnumMeta,EventEnum
original_call=_EventEnumMeta.__call__
def compatible(cls,value,*args,**kwargs):
    if cls is EventEnum:return cls._missing_(int(value))
    return original_call(cls,value,*args,**kwargs)
_EventEnumMeta.__call__=compatible
fixtures=W/'pyflp-source/tests/assets'
for relative in ['plugins/fruity-soft-clipper.fst','inserts/100%-left.fst']:
    obj=pyflp.parse(fixtures/relative)
    assert len(list(obj.events))>0
root=Path(sys.argv[1]);rows=[]
for path in sorted((root/'presets').glob('*.fst')):
    obj=pyflp.parse(path);events=list(obj.events)
    names=[e.value for e in events if int(e.id)==201]
    data=[e for e in events if int(e.id)==213]
    assert names and len(names)==len(data)
    rows.append(dict(file=path.relative_to(root).as_posix(),format=str(obj.format),native_names=names,native_state_events=len(data),SHA256=hashlib.sha256(path.read_bytes()).hexdigest()))
report=dict(independent_parser='PyFLP',source='https://github.com/demberto/PyFLP',python312_empty_Enum_compatibility_shim=True,stock_sample_positive_controls_passed=True,generated_presets=rows,FL_GUI_tested=False)
(root/'verification/FST_INDEPENDENT_PARSE.json').write_text(json.dumps(report,indent=2)+'\n')
print('INDEPENDENT_FST_PARSE_PASS',len(rows))
