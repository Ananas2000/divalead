from pathlib import Path
u=Path(__file__).resolve().parent;s=(u/'study_native_bipolar_even8_current556.py').read_text();s=s[:s.index("try:\n (R/'PREDECLARED_PROTOCOL.json')")]
a=s.index("H=Path(__file__).resolve().parent;");b=s.index("for name,key in",a)
s=s[:a]+'''H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects');R=H/'WS_BIPOLAR_ODD9_EVEN8_CURRENT39';R.mkdir(exist_ok=False);STATE=N/'ORIGINAL_NATIVE_WS_ODD_EVEN17_CURRENT39_STUDY.json'
prior=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());assert prior['full_public_kit_directory']=='ZL-WIP39';seed=prior['native_base'];base=np.array(seed['x']);bundle=seed['native_saved_state_bundle'];bundledir=Path(bundle['directory']);wsrow=next(row for row in bundle['manifest']if row['node']==0);original_canonical=(bundledir/wsrow['state']).read_bytes();canonical=original_canonical;count=struct.unpack_from('<I',canonical,30)[0];assert count==233 and struct.unpack_from('<I',canonical,16)[0]==1
origin=np.zeros(17);step=np.r_[np.array([.001,.001,.0007,.0007,.001,.0015,.0018,.002]),np.full(9,.0006)]
'''+s[b:]
a=s.index("(R/'ANCHOR38_PRIMARY.bin')");b=s.index("(R/'PRIOR_COMBINED",a);s=s[:a]+s[b:]
s=s.replace("B=np.column_stack(B);B/=B.max(axis=0);", "B.append(S*window)\nfor center in np.linspace(.08,.64,8):B.append(S*np.exp(-.5*((abs(S)-center)/.045)**2)*window)\nB=np.column_stack(B);B/=np.max(abs(B),axis=0);assert B.shape[1]==17;")
s=s.replace("waveshaper_bipolar_even_research_format='official_GUI_bipolar_compact_even8_research_v1',waveshaper_bipolar_even_coefficients=", "waveshaper_bipolar_odd_even_research_format='canonical_parent_local_even8_odd9_research_v1',waveshaper_bipolar_odd_even_coefficients=")
s=s.replace("waveshaper_bipolar_base_state=str(R/'BIPOLAR_GUI_CONVERTED_BASE.bin'),waveshaper_bipolar_base_SHA256=", "waveshaper_research_parent_state=str(R/'BIPOLAR_GUI_CONVERTED_BASE.bin'),waveshaper_research_parent_SHA256=")
s=s.replace("only_native_WaveShaper_bipolar_even8_curve_controls_varied=True,current_comparator=556", "only_native_WaveShaper_local_even8_odd9_controls_varied=True,current_comparator=prior['source_accepted_cohort']").replace("full_base_kit='ZL-WIP38'", "full_base_kit='ZL-WIP39'")
s=s.replace('first6/cold2','first6/first10/cold2').replace('all52 supported stock WaveShaper curve controls','17 local odd/even stock WaveShaper curve controls')
(u/'study_native_odd_even17_current39.py').write_text(s+(u/'odd_even17_terminal.py.txt').read_text())
