"""Extract only the requested DLL using the existing libarchive runtime."""
from pathlib import Path, PurePosixPath
import ctypes as C, ctypes.util, hashlib, json, os, sys

archive_path=Path(sys.argv[1]).resolve()
target=Path('/tmp/divalead-native-effects/dsp_ippv2_x64.dll')
lib=C.CDLL(ctypes.util.find_library('archive'))
def bind(name,args,ret):
    f=getattr(lib,name);f.argtypes=args;f.restype=ret;return f
new=bind('archive_read_new',[],C.c_void_p)
filters=bind('archive_read_support_filter_all',[C.c_void_p],C.c_int)
formats=bind('archive_read_support_format_all',[C.c_void_p],C.c_int)
open_file=bind('archive_read_open_filename',[C.c_void_p,C.c_char_p,C.c_size_t],C.c_int)
next_header=bind('archive_read_next_header',[C.c_void_p,C.POINTER(C.c_void_p)],C.c_int)
pathname=bind('archive_entry_pathname',[C.c_void_p],C.c_char_p)
entry_size=bind('archive_entry_size',[C.c_void_p],C.c_int64)
filetype=bind('archive_entry_filetype',[C.c_void_p],C.c_uint)
read=bind('archive_read_data',[C.c_void_p,C.c_void_p,C.c_size_t],C.c_ssize_t)
skip=bind('archive_read_data_skip',[C.c_void_p],C.c_int)
error=bind('archive_error_string',[C.c_void_p],C.c_char_p)
free=bind('archive_read_free',[C.c_void_p],C.c_int)
a=new();assert a
rows=[];found=False;temp=target.with_suffix('.dll.partial')
try:
    assert filters(a)==0 and formats(a)==0
    result=open_file(a,os.fsencode(archive_path),10240)
    assert result==0,error(a)
    ent=C.c_void_p()
    while True:
        status=next_header(a,C.byref(ent))
        if status==1:break
        assert status==0,error(a)
        name=os.fsdecode(pathname(ent)).replace('\\','/')
        path=PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        size=entry_size(ent);rows.append(dict(name=name,bytes=size,type=filetype(ent)))
        if path.name.casefold()!='dsp_ippv2_x64.dll':
            assert skip(a)==0,error(a);continue
        assert not found and filetype(ent)==0o100000 and 0<size<1024**3
        found=True;total=0;buf=C.create_string_buffer(1024**2);sha=hashlib.sha256()
        with temp.open('wb') as f:
            while True:
                got=read(a,buf,len(buf))
                assert got>=0,error(a)
                if got==0:break
                chunk=buf.raw[:got];f.write(chunk);sha.update(chunk);total+=got
        assert total==size
        temp.replace(target)
    assert found,'Requested DLL not found in archive'
finally:
    free(a)
report=dict(archive=str(archive_path),archive_bytes=archive_path.stat().st_size,
            archive_SHA256=hashlib.sha256(archive_path.read_bytes()).hexdigest(),
            entries=rows,extracted_file=str(target),extracted_bytes=target.stat().st_size,
            DLL_SHA256=sha.hexdigest(),archive_reader_completed_without_CRC_error=True)
(target.parent/'DSP_ARCHIVE_EXTRACTION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
