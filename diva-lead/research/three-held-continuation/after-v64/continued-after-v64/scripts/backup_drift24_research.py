from pathlib import Path
import json,shutil,hashlib
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');P=REPO/'diva-lead/research/three-held-continuation';T=P/'after-v59';T.mkdir(exist_ok=False)
ignore=shutil.ignore_patterns('*.dll','*.so','*.exe','*.pyc','__pycache__')
for folder in ['source-wide','source-drift24-proof']:shutil.copytree(R/folder,T/folder,ignore=ignore)
for name in ['prove_drift24.py','prepare_drift24_continuation.py','continue_drift24.py','validate_three_source_model.py','drift24-proof.log','source-wide.log','drift24-continuation-state.json','drift24-controller-launch.json','verify_public_v59.py','public-v59-verification.json']:
 if (R/name).exists():shutil.copyfile(R/name,T/name)
ref,sr=sf.read(REPO/'diva-lead/v59-wip/Diva_original_lead_reference.wav');previous,pr=sf.read(REPO/'diva-lead/v59-wip/Diva_Lead_v59_REFERENCE_EDIT.wav');edit,er=sf.read(R/'source-drift24-proof/REFERENCE_EDIT_WIP.wav');assert sr==pr==er==48000 and ref.shape==previous.shape==edit.shape
scale=np.sqrt(np.mean(ref*ref)/np.mean(edit*edit));sf.write(T/'AB_REFERENCE_V59_DRIFT24_RESEARCH_WIP.wav',np.concatenate([ref,np.zeros((24000,2)),previous,np.zeros((24000,2)),edit*scale]),48000,subtype='PCM_24')
report=json.loads((R/'source-drift24-proof/validation.json').read_text());assert report['all_chosen_three_guards_passed']
(T/'README.md').write_text('''# После v59: более широкий подбор самой Diva

Проверены ещё **44 настоящих рендера Diva** с той же трёхнотной партией, ARP и огибающими. Изменялись PW, баланс осцилляторов, Drift, резонанс и срез фильтра, Tune1 и KeyScale. Лучший допустимый скрининговый вариант изменил только **OSC:Drift 24,80 → 24,00**.

Его предварительное преимущество очень мало: критерий тембра 0,848973399 → 0,848859443; прежний общий критерий 0,941659039 → 0,941569122. Ошибка crest снизилась 0,558807220 → 0,557472174 dB. Это численные результаты, предпочтение на слух не установлено. Точного совпадения ещё нет.

Для Drift24 выполнены повторная настоящая Diva, точное совпадение сырого WAV с предложением, все281 параметр (изменился один), 12 входящих событий и Windows/native. **Заново построена своя независимая NEW-база для изменённого источника**, проверены полная цепочка и12 произвольных сигналов на4частотах. Все финальные пределы по исходному выбранному трёхнотному варианту выполнены; диагностические более свободные screening-пределы не использованы для принятия.

В [A/B WAV](AB_REFERENCE_V59_DRIFT24_RESEARCH_WIP.wav): оригинал с0с, опубликованный v59 с4,168с, Drift24 с8,336с. Кандидат выровнен одним общим RMS-множителем. Отдельный исходник/пресет/анализ/сохранённый независимый пересчёт — в `source-drift24-proof/`.

**Основной комплект v59 не изменён.** Изменение Drift пока оставлено отдельным исследованием. Для него запущен свой подбор обработки с его собственным сырьём и NEW-базой; смешивать его с контроллером неизменённого источника нельзя. `continue_drift24.py --check-only` прошёл полную проверку этой семьи. Записанный state — снимок при бэкапе, а не обещание жизни процессов после остановки среды. В рабочей среде продолжение ведётся отдельным процессом без автоматической публикации Git. Другой контроллер продолжает исходную трёхнотную настройку.

Все44пробы и полный proof сохранены. Численные предложения последующих раундов не считаются принятыми до свежей проверки Diva/Windows/ownNEW/fixture/всех12произвольных случаев. GUI FL Studio и прослушивание ассистентом не выполнялись.
''')
p=P/'README.md';s=p.read_text();s=s.replace('Отдельный более широкий скрининг параметров настоящей Diva начат после сборки v59; его новые результаты не включены в этот снимок.','После сборки v59 выполнен отдельный более широкий скрининг из44проб и полный proof источника Drift24 с новой собственной NEW-базой: [последующее исследование](after-v59/README.md). Этот отдельный кандидат не включён в неизменяемый комплект v59; подбор обработки обеих трёхнотных настроек продолжается.')
p.write_text(s)
(T/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(T))+'\n' for p in sorted(T.rglob('*')) if p.is_file()))
print('DRIFT2444_SCREENINGS_AND_OWN_NEW_PROOF_BACKED_UP',sum(1 for p in T.rglob('*') if p.is_file()))
