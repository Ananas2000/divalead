from pathlib import Path
V=Path(__file__).resolve().parent;s=(V/'Diva_precise17_support.py').read_text().replace('/tmp/divalead-Diva-precise17-current576-20261104','/tmp/divalead-Diva-preWS-pan8-native12-20261104').replace('ORIGINAL_DIVA_PRECISE17_CURRENT576_STUDY.json','ORIGINAL_DIVA_PRE_WS_PAN8_NATIVE12_STUDY.json');(V/'Diva_preWS_pan8_support.py').write_text(s)
s=(V/'study_Diva_precise17_current576.py').read_text().replace('import Diva_precise17_support as q','import Diva_preWS_pan8_support as q').replace('DIVA_PRECISE17_CURRENT576','DIVA_PRE_WS_PAN8_NATIVE12').replace('DivaPrecise17-576','DivaPreWS-Pan8');a=s.index('axes=[');b=s.index('\ndef powers(',a);s=s[:a]+"axes=[dict(section='VCA1',key='Pan',index=167,origin=-39.33,step=.3)]"+s[b:]
a=s.index("baseline=evaluate('baseline'");b=s.index(' candidates=sorted(',a);s=s[:a]+"baseline=evaluate('baseline',[0])\n for delta in [-4,-2,-1,1,2,4,8]:evaluate('pan-'+str(delta),[delta])\n"+s[b:]
s=s.replace('for k in range(3):\n  native,_=c.render()','for k in range(6):\n  native,_=c.render()').replace('actual_training_native_DSP_renders=3*len(rows)','actual_training_native_DSP_renders=6*len(rows)')
s=s.replace('source_models=\'baseline +12 scalar derivatives +up to4 joint proposals; h2p values round2 decimals; every source chunk replayed; identical source audio rejected\'','source_models=\'baseline pan-39.33 plus shifts[-1.2,-.6,-.3,+.3,+.6,+1.2,+2.4] before WS; six real native draws each; exact source chunk replay and identity gates\'')
s=s.replace('Finer actual Diva PWM/mix/detune/filter probes','Actual source pre-WaveShaper panning and nonlinear stereo/tone interaction')
(V/'study_Diva_preWS_pan8_native12.py').write_text(s)
print('Prepared8 actual Diva pre-WS panning models; 6native draws each, all source chunk gates')
