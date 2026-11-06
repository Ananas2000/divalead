"""New amplitude-crest controls where the existing compact local17 window vanishes."""
from pathlib import Path
V=Path(__file__).resolve().parent;s=(V/'study_proxy_derivative_local17_native12.py').read_text().replace('/tmp/divalead-native12-local17-zeroDepth-derivatives-fullChorus-20261104','/tmp/divalead-native12-highcrest8-proxy-fullChorus-20261104').replace('NATIVE12_LOCAL17_PROXY_DERIVATIVES','NATIVE12_HIGHCREST8_PROXY').replace('Native12ProxyJ','Native12Crest8J')
s=s.replace("origin=np.array(seed['waveshaper_os_local17_adjustment'],float);step=.35*np.r_[np.array([.001,.001,.0007,.0007,.001,.0015,.0018,.002]),np.full(9,.002)]","origin=np.zeros(8);step=np.full(8,.00035)")
a=s.index('X=np.cumsum(');b=s.index('def native(tag):',a)
s=s[:a]+'''X=np.cumsum([struct.unpack_from('<d',canonical,34+24*k)[0]for k in range(count)]);S=2*X-1;window=np.maximum(0,1-(S/.74)**2)**4
B=[]
for center in [.56,.60,.64,.68]:
 bump=np.exp(-.5*((abs(S)-center)/.020)**2)*window
 B.extend([S*S*bump,S*bump])
B=np.column_stack(B);B/=np.max(abs(B),axis=0);Y0=np.array([struct.unpack_from('<d',canonical,42+24*k)[0]for k in range(count)])
(R/'PINNED_CANONICAL_NATIVE12_PARENT.bin').write_bytes(canonical)
def native_case(v):
 return dict(seed,not_compatible_with_standard_x95_exporter=True,waveshaper_crest8_research_format='bipolar_highcrest_even_odd4_gaussian_float32_v1',waveshaper_crest8_research_coefficients=list(map(float,v)),waveshaper_crest8_research_parent=str(R/'PINNED_CANONICAL_NATIVE12_PARENT.bin'),waveshaper_crest8_research_parent_SHA256=hashlib.sha256(canonical).hexdigest())
def curve(v):
 if v is None:return original_canonical
 y=np.asarray(Y0+B@np.asarray(v),np.float32).astype(np.float64)
 if y.min()<0 or y.max()>1 or np.min(np.diff(y))< -1e-10:return None
 data=bytearray(canonical)
 for k,value in enumerate(y):struct.pack_into('<d',data,42+24*k,float(value))
 return bytes(data)
'''+s[b:]
s=s.replace('range(17)','range(8)').replace('np.eye(17)','np.eye(8)').replace('np.zeros(17)','np.zeros(8)').replace('[-9:]','[-5:]').replace('np.eye(9)','np.eye(5)').replace('np.zeros(9)','np.zeros(5)').replace('strong9','strong5').replace('all17','all8')
s=s.replace('not_compatible_with_standard_x95_exporter=False','not_compatible_with_standard_x95_exporter=True').replace('not_compatible_with_current_supported_curve_generator=False','not_compatible_with_current_supported_curve_generator=True').replace('requires_explicit_supported_metadata_migration=False','requires_explicit_supported_metadata_migration=True')
s=s.replace('latest_BEST_context_and_full_FL20_export_required=True','latest_BEST_context_explicit_generator_schema_migration_and_full_FL20_export_required=True')
s=s.replace('local_even_controls=8,local_odd_controls=9','highcrest_centers=[.56,.60,.64,.68],basis_width=.020,compact_support_abs=.74,highcrest_even_controls=4,highcrest_odd_controls=4')
s=s.replace('native_GUI_OS_step1_and_local_even8_odd9_controls_varied=True','native12_OSstep1_fixed_new_highcrest_even4_odd4_controls_varied=True')
s=s.replace("other11_native_source_MIDI_ARP_ADSR_routing_and_both_ZL_unchanged=True","other11_native_source_MIDI_ARP_ADSR_routing_and_both_ZL_unchanged_for_matching_models_only=True,proxy_derivatives_only_Chorus_depth0=True")
s=s.replace("actual_training_DSP_renders=sum(12 if r['label']=='current580-canonical-control'else 1 if r['label']=='same-canonical-parent-origin'or r['label'].startswith('derivative-')else 4 for r in rows)","actual_training_DSP_renders=sum(12 if r['label']=='current580-canonical-control'else 1 if r['label']=='same-canonical-parent-origin'or r['label'].startswith('derivative-')else 4 for r in rows)")
s=s.replace('new deterministic proxy-slope/full-Chorus-residual proposals; same supported generator and source3held','new highcrest8 amplitude region .56-.68, existing local17 window ends at.67; canonical float32 research state, pending explicit supported migration')
s=s.replace('proxyJ-native12-new12','crest8-native12-new12')
s=s.replace('Use actual zeroDepth native derivatives only for proposals; accept only full saved Chorus.','Explore new highcrest even/odd8 native curves; proxy slopes only, full saved Chorus accepts.')
s=s.replace("  bylabel={r['label']:r for r in rows};","  (R/'ACTUAL_DERIVATIVE_ROWS_BEFORE_PROPOSALS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));bylabel={r['label']:r for r in rows};")
(V/'study_native12_crest8_proxy_fullChorus.py').write_text(s)
print('Prepared new crest8 actual native float32 curves; explicit unsupported-export flag until migration')
