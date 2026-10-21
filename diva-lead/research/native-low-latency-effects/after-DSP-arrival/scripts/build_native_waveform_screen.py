from pathlib import Path
W=Path('/tmp/divalead-native-effects');s=(W/'probe_Diva_PW_keyfollow.py').read_text()
s=s.replace("W/'Diva-PW-keyfollow-screen-isolated-assessment'", "W/'Diva-waveform-source-screen-isolated-assessment'")
s=s.replace("ROOT=W/'native-Diva-PW-keyfollow-screen-01'", "ROOT=W/'native-Diva-waveform-screen-01'")
s=s.replace("preset=(V/'Diva_Lead_v83_WIP.h2p').read_text();original,sr=sf.read(V/'Diva_SOURCE_FROZEN_48k.wav',dtype='float32');assert sr==48000", "B=Path('/workspace/divalead-work/native-low-latency-effects/source-bases/PW-keyfollow-depth-1')\npreset=(B/'Diva.h2p').read_text();original,sr=sf.read(B/'Diva_source.wav',dtype='float32');assert sr==48000")
s=s.replace("prior=parameters(V/'verification/Diva_all281.tsv')", "prior=parameters(B/'all281.tsv')")
a=s.index("cases=[('baseline'");b=s.index('features=FeaturesOriginal',a)
s=s[:a]+'''cases=[('baseline',{},set())]
for label,values,allowed in [
 ('osc1-no-triangle',{'Tri1':0},{111}),
 ('osc1-no-pulse',{'PWM1':0},{114}),
 ('osc1-add-saw',{'Saw1':1},{113}),
 ('osc1-saw-pulse',{'Tri1':0,'Saw1':1},{111,113}),
 ('osc1-triangle-saw',{'PWM1':0,'Saw1':1},{114,113}),
 ('osc1-saw-only',{'Tri1':0,'PWM1':0,'Saw1':1},{111,114,113}),
 ('osc2-add-sine',{'Sin2':1},{112}),
 ('osc2-add-triangle',{'Tri2':1},{115}),
 ('osc2-add-saw',{'Saw2':1},{116}),
 ('osc2-saw-only',{'PW2':0,'Saw2':1},{117,116}),
 ('osc2-triangle-only',{'PW2':0,'Tri2':1},{117,115}),
 ('osc2-sine-only',{'PW2':0,'Sin2':1},{117,112}),
 ('osc2-sync-off',{'Sync2':0},{95}),
 ('oscillator-mix-10',{'OscMix':10.},{96}),
 ('oscillator-mix-15',{'OscMix':15.},{96}),
 ('oscillator-mix-2',{'OscMix':2.},{96})]:
    cases.append((label,{('OSC',k):v for k,v in values.items()},allowed))
''' +s[b:]
s=s.replace("f'Diva-PW-keyfollow-{threading.get_ident()}'", "f'Diva-waveform-{threading.get_ident()}'")
s=s.replace("fl_graph=True,engine_override='fl_native_source_variants_host.exe'", "fl_graph=True,phase_pair=len(x)==95,engine_override='fl_native_common_phase_host.exe' if len(x)==95 else 'fl_native_source_variants_host.exe'")
s=s.replace("assert len(x)==94", "assert len(x) in [94,95]")
(W/'probe_Diva_waveforms_native.py').write_text(s)
