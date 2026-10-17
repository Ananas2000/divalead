"""Actual Diva rendering with a pinned, previously proved idle-warmup recipe."""
from pathlib import Path
import json,subprocess,hashlib
import numpy as np,soundfile as sf
from v18performancelib import WINE,ENV,PLUGIN,winpath,commands
def render_performance(settings,tag,preset,dump,history):
    host_source=Path(history['host_source'])
    assert hashlib.sha256(host_source.read_bytes()).hexdigest()==history['host_source_SHA256']
    assert history['prelude_repeats']==0 and history['target_MIDI_events_unchanged']
    path=Path('/workspace/divalead-work')/(tag+'.wav');path.unlink(missing_ok=True)
    lines=commands(settings,path,dump=dump).splitlines();extra=[]
    if 'second_velocities' in settings:extra+=['secondvel '+' '.join(str(int(q)) for q in settings['second_velocities'])]
    if 'second_offsets' in settings or 'second_gates' in settings:extra+=['secondgrid '+' '.join(map(str,settings.get('second_offsets',settings['offsets'])+settings.get('second_gates',settings['gates'])))]
    lines=lines[:-2]+extra+['warmblocks '+str(history['warmup_blocks']),'preludes 0']+lines[-2:]
    with path.with_suffix('.log').open('w') as log:
        subprocess.run([WINE,str(host_source.with_suffix('.exe')),PLUGIN,winpath(preset)],input='\n'.join(lines)+'\n',text=True,env=ENV,stdout=log,stderr=log,check=True,timeout=150)
    text=path.with_suffix('.log').read_text();assert 'ERROR ' not in text
    notes=[line for line in text.splitlines() if line.startswith('NOTE ')]
    expected=[line for line in (host_source.parent/'baseline.log').read_text().splitlines() if line.startswith('NOTE ')]
    assert len(notes)==32 and notes==expected
    raw,sr=sf.read(path,dtype='float32');assert sr==48000 and raw.shape==(288000,2) and np.isfinite(raw).all()
    assert hashlib.sha256(raw.tobytes()).hexdigest()==history['source_samples_SHA256']
    return raw
