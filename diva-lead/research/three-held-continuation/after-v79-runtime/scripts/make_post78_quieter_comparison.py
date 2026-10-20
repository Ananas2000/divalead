"""Audition files from independently fully proved three-note models, at one stereo RMS."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead');D=Path('/tmp/divalead-post78-quieter-comparison');D.mkdir(exist_ok=False)
main=P/'diva-lead/v79-wip';quiet=R/'post74joint-verified-post77-cleaner-hf100-alternative-0001'
a=json.loads((main/'verification/selected_validation.json').read_text());b=json.loads((quiet/'validation.json').read_text())
assert b['quieter_alternative_not_claimed_primary_tone_improvement'] and b['all_chosen_three_guards_passed']
assert b['metrics']['upper_off']<a['metrics']['upper_off'] and b['tone_score']>a['tone_score']
assert (main/'verification/Diva_all281.tsv').read_bytes()==(quiet/'Diva_all281.tsv').read_bytes()
reference,sr=sf.read(main/'Diva_original_lead_reference.wav');current,cr=sf.read(main/'Diva_Lead_v79_REFERENCE_EDIT.wav');alternative,ar=sf.read(quiet/'REFERENCE_EDIT_WIP.wav')
assert sr==cr==ar==48000 and reference.shape==current.shape==alternative.shape==(176064,2)
assert hashlib.sha256(reference.tobytes()).hexdigest()=='450ab495963c48a8a3c5e94e64475a59ffdd04db4e7d4b5ad0d595e137ce512c'
gains=[]
for wave in [current,alternative]:
    gain=np.sqrt(np.mean(reference*reference)/np.mean(wave*wave));wave*=gain;gains.append(float(gain))
gap=np.zeros((24000,2));path=D/'AB_REFERENCE_V79_QUIETER_WIP.wav'
sf.write(path,np.concatenate([reference,gap,current,gap,alternative]),sr,subtype='PCM_24')
sf.write(D/'QUIETER_THREE_HELD_REFERENCE_EDIT_WIP.wav',alternative,sr,subtype='PCM_24')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(path),'-codec:a','libmp3lame','-b:a','320k',str(path.with_suffix('.mp3'))],check=True)
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sequence=['uploaded original','full v79','fully proved quieter tradeoff'],starts_seconds=[0,4.168,8.336],sample_rate=sr,frames_per_fragment=176064,one_common_stereo_RMS_gain_per_fragment=gains,channels_and_notes_not_normalized_separately=True,full_v79_tone=a['tone_score'],quieter_tone=b['tone_score'],full_v79_upper_off_error=a['metrics']['upper_off'],quieter_upper_off_error=b['metrics']['upper_off'],same_all281_Diva_and_three_held_MIDI=True,quieter_is_not_claimed_primary_tone_winner=True,subjective_audition_performed=False,match_reached=False)
(D/'comparison.json').write_text(json.dumps(receipt,indent=2)+'\n')
(D/'README_RU.md').write_text('''# Оригинал → v79 → отдельный вариант с меньшим остатком

[WAV A/B](AB_REFERENCE_V79_QUIETER_WIP.wav), [MP3](AB_REFERENCE_V79_QUIETER_WIP.mp3). Оригинал — с 0 с, полный v79 — с 4,168 с, отдельный вариант — с 8,336 с.

У отдельного варианта ниже измеренная ошибка энергии между верхними гармониками; основная ошибка тембра немного выше. Он прошёл свежую настоящую Diva/Windows/native/собственную NEW-базу/отдельный fixture/все 12 причинных случаев и все прежние абсолютные ограничения. Это сохранённый компромисс, выбранный по метрике остатка. Ассистент субъективное прослушивание не выполнял. Совпадение ещё не достигнуто.

`QUIETER_THREE_HELD_REFERENCE_EDIT_WIP.wav` — готовый короткий WAV этого варианта. Для FL Studio: 180 BPM, 48 kHz, перетащить в Playlist, Normalize выключить, Time stretching → Resample, Time → Reset, канал/Insert/Master 0 dB, чистый Insert. Обработка уже записана в WAV.

Для редактирования MIDI и игры актуальный полный комплект — [v79](../../../../v79-wip/FL_STUDIO_RU.md). В отдельном WAV использованы другие коэффициенты Finish; этот файл является самостоятельным готовым аудиофрагментом. Три удерживаемые ноты, исходная Diva и ARP прежние. Оба кандидата выровнены к оригиналу одним общим стерео RMS-множителем, без раздельного выравнивания каналов или нот. Измерения и времена — comparison.json.
''')
print('FULLY_PROVED_QUIETER_COMPARISON_READY',receipt['quieter_upper_off_error'],flush=True)
