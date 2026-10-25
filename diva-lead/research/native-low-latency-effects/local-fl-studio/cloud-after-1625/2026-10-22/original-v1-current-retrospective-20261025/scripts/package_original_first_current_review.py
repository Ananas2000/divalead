"""Package the retrospective comparison, exact scoring WAVs and level-matched A/B."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
import numpy as np,soundfile as sf
H=Path(__file__).resolve().parent;R=H/'original-first-current-review';report=json.loads((R/'COMPARISON.json').read_text());rows={r['label']:r for r in report['rows']}
order=['reference','v1_controlled','v8','v83_old_finish','current_cohort_155'];gap=np.zeros((24000,2));pieces=[]
for label in order:
 p=R/'audio'/('reference.wav'if label=='reference'else label+'_RMS_MATCHED.wav');y,sr=sf.read(p,always_2d=True);assert sr==48000;pieces.extend([y,gap])
joined=np.concatenate(pieces[:-1]);gain=min(1.,.95/float(abs(joined).max()));sf.write(R/'AB_ORIGINAL_V1_V8_V83_CURRENT.wav',joined*gain,48000,subtype='PCM_24')
for ext,args in [('mp3',['-codec:a','libmp3lame','-b:a','256k']),('flac',['-codec:a','flac'])]:subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'AB_ORIGINAL_V1_V8_V83_CURRENT.wav'),*args,str(R/('AB_ORIGINAL_V1_V8_V83_CURRENT.'+ext))],check=True)
(R/'AB_FIVE_STAGE_METADATA.json').write_text(json.dumps(dict(order=order,starts_seconds=[0,4.168,8.336,12.504,16.672],same_global_stereo_RMS_level=True,no_independent_channel_or_note_normalization=True,common_headroom_gain=gain),indent=2)+'\n')
archive=R/'EXACT_RMS_MATCHED_SCORING_WAVs.zip';members={}
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in sorted((R/'audio').glob('*')):
  if p.name.startswith('source-'):continue
  assert p.suffix=='.wav';z.write(p,p.name);members[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for name,digest in members.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
(R/'EXACT_SCORING_WAV_SHA256.json').write_text(json.dumps(members,indent=2)+'\n')
labels={'v1_controlled':'v1, самый ранний пресет на общей контрольной партии','v2_stereo':'v2 STEREO, самый ранний готовый WAV','v8':'v8','v20':'v20','v24':'v24','v53':'v53','v57':'v57, прежняя многонотная ветка','v58_three_held':'v58, выбранная трёхнотная ветка','v83_old_finish':'v83, прежняя Finish-цепь с задержкой','ZL01':'первая ZL-цепь','ZL25':'ZL25','current_cohort_155':'текущий ZL25 + принятые улучшения70/155'}
table='| Этап | Гармоники24,дБ | Верхние гармоники,дБ | ERB-полосы,дБ |\n|---|---:|---:|---:|\n'
for key,row in rows.items():
 m=row['metrics'];table+='| '+labels[key]+' | '+f"{m['H24']:.3f} | {m['upper_harm']:.3f} | {m['ERB']:.3f}"+' |\n'
ratio=rows['v1_controlled']['metrics']['H24']/rows['current_cohort_155']['metrics']['H24']
text=f'''# Насколько близки к оригиналу: v1 → история → текущий вариант

Текущий вариант значительно ближе первых v1/v2/v8, но полного совпадения нет.
Переход на быструю native/ZL-цепь сохранил не всю точность прежней Finish-обработки:
v83 точнее по гармоникам/верхнему спектру и нескольким стереопоказателям.
Нельзя называть новые номера безусловным улучшением по всем параметрам.

{table}

Меньше — лучше. Это физические ошибки по одной методике, не проценты слышимого
сходства. По24гармоникам ошибка v1→current уменьшена примерно в{ratio:.1f}раз;
от v8 — примерно в1.9раз. Это не означает ни «в7разпохожее», ни «85%готовности».
Средняя текущая H24 по восьми независимым сохранённым nativeрендерам1.684дБ,
диапазон1.682–1.686дБ; строка таблицы — один сохранённый репрезентативный WAV.
У v83 около1.017дБ. Значит, перенос на цепь без большой задержки ещё не достиг
точности прежней обработки. И та прежняя обработка полного совпадения не давала.

Сейчас основной характер/партия и трёхнотная схема сильно приблизились к цели;
остаточные различия затрагивают баланс верхних гармоник, структуру фона между
гармониками, динамику и стерео. Текущая ошибка межгармонической энергииверха
около3.90дБ vs1.94дБ уv83. Знак ошибок разный по полосам/каналам: это нельзя
перевести в утверждение «у нас везде на3.9дБ больше шума». Noiseосциллятора
по-прежнему0. Корреляция L/R current~.946 vsoriginal~.922 показывает остаточную
разницу ширины; одна корреляция не описывает всё стерео. В300–800Гц current
левее~4.19дБ vsoriginal~.97дБ, разница~3.23дБ. Верх сильно исправлен против
первойZLцепи, но нулевая общая панорама не устранит все частотные отличия.

[A/B MP3: оригинал → v1 → v8 → v83 → current](AB_ORIGINAL_V1_V8_V83_CURRENT.mp3).
Начала0 /4.168 /8.336 /12.504 /16.672с.
[Тот же A/B без потерь](AB_ORIGINAL_V1_V8_V83_CURRENT.flac).
Одна общая stereoRMSнормировка на фрагмент; не выравниваются отдельно каналы
или отдельные ноты. Применён один общий headroomgain ко всему A/B.

В v1 первоначально не было публичного синтезированного WAV. Для старого общего
сравнения её точный h2p уже был загружен в настоящую Diva и отрендерен на общей
контрольной партии. Здесь использован тот сохранённый контрольный WAV.
Побайтово подтверждено: h2pконтроля равен самому первому rootпресету v1,
SHA25618f7469ec62c9b3f668fd835b8ef4610f245ae247a36e77ca26f42416a85de3b.
Это не исторический экспорт исходной неверно восстановленной MIDIпартииv1.
Самый ранний уже готовый доставленный WAV — v2STEREO, он сравнен отдельно.
v1моно; некоторые Mid/Sideметрики сильно штрафуют отсутствиеSide и зависят
от численного floor. Поэтому общий индекс34.53vs1.318 не используется как
«26кратное улучшение сходства». Вывод опирается на отдельные физические метрики.

Проанализирована история этапов/архив общего ранжирования175вариантов и заново
оценены12репрезентативных WAV одним критерием. Не заявляется новое субъективное
прослушивание ассистентом, новые Divaэкземпляры или WindowsGUIэкспорты.
Originalselfcheck дал нулевые ошибки с точностью вычислений. Рабочие presets/
MIDI/эффекты и принятие новых кандидатов этим анализом не менялись.

COMPARISON.json содержит метрики/провенанс/восемь реализаций текущего кандидата.
EXACT_RMS_MATCHED_SCORING_WAVs.zip содержит все точные WAV, на которых считались
новые строки; SHA/CRC каждого проверены. Исходные рабочие WAV не изменялись.
Файлыанализа имеют общуюRMSнормировку, это не рабочие синтезаторныепресеты.
Скриптreview_original_first_and_current.py использует подготовленную cloudсреду;
его полное восстановление на чистой машине этой проверкой не подтверждается.
Полного совпадения нет; сроки достижения или %готовности из этих данных не следуют.
'''
(R/'README_RU.md').write_text(text)
print(json.dumps(dict(root=str(R),scoring_ZIP_bytes=archive.stat().st_size,scoring_ZIP_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),reference_to_current_H24_ratio=ratio,comparison_not_perceptual_percentage=True),ensure_ascii=False),flush=True)
