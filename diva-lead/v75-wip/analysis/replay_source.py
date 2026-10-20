"""Replay a packaged Diva source under Linux/Wine and compare decoded samples.

Compile diva_source_render_host.c with MinGW first. Diva is supplied by the user.
This does not run FL Studio or reproduce its internal startup history.
"""
from pathlib import Path
import argparse,json,os,subprocess
import numpy as np
import soundfile as sf

p=argparse.ArgumentParser(description=__doc__)
for key in ['wine','host','plugin','wine-prefix','wine-dll-path','output']:
    p.add_argument('--'+key,required=True,type=Path)
a=p.parse_args();D=Path(__file__).resolve().parent.parent
a.output.mkdir(parents=True,exist_ok=True)
def win(path):return 'Z:'+str(path.resolve()).replace('/','\\')
preset=D/'Diva_Lead_v75_WIP.h2p';fixture=D/'Diva_SOURCE_FROZEN_48k.wav'
expected=[[e[k] for k in ['frame','status','pitch','velocity']] for e in json.loads((D/'verification/MIDI_note_events_48k.json').read_text())['events']]
assert len(expected)==12 and sum(e[1]==144 for e in expected)==6
roots=json.loads((D/'render_timing_180BPM.json').read_text())['root_velocities']
commands=['pattern 3 0 8','velocities '+' '.join(map(str,roots))]
output=a.output/'Diva.wav';logfile=a.output/'Diva.log';dump=a.output/'all281.tsv'
commands+=['warmblocks 128','preludes 0','dump '+win(dump),'render '+win(output),'quit']
env=os.environ.copy();env.update(WINEPREFIX=str(a.wine_prefix.resolve()),WINEDLLPATH=str(a.wine_dll_path.resolve()),WINEDEBUG='-all')
with logfile.open('w') as log:
    subprocess.run([str(a.wine),str(a.host),win(a.plugin),win(preset)],input='\n'.join(commands)+'\n',text=True,env=env,stdout=log,stderr=log,timeout=120,check=True)
text=logfile.read_text();assert 'ERROR ' not in text
actual_events=[list(map(int,line.split()[1:])) for line in text.splitlines() if line.startswith('NOTE ')]
assert actual_events==expected
actual,rate=sf.read(output,dtype='float32');saved,saved_rate=sf.read(fixture,dtype='float32')
assert rate==saved_rate==48000
np.testing.assert_array_equal(actual,saved)
expected_dump=D/'verification/Diva_all281.tsv'
assert dump.read_bytes()==expected_dump.read_bytes()
print(json.dumps(dict(fresh_Diva_samples_exact=True,all281_exact=True,all_MIDI_events_exact=True,three_held=True,FL_GUI_tested=False)))
