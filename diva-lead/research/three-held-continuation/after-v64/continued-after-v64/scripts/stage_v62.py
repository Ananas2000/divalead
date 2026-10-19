from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ROOT=REPO/'diva-lead/research/three-held-continuation';P=ROOT/'after-v62';T=R/'v62-build';D=REPO/'diva-lead/v62-wip'
assert json.loads((T/'clean-ZIP-Windows-proof.json').read_text())['full_WAV_sample_exact']
assert json.loads((T/'ZIP-proof.json').read_text())['clean_extraction_release_replay_passed']
P.mkdir(exist_ok=False);assert not D.exists();ignore=shutil.ignore_patterns('*.so','*.dll','*.exe','*.pyc','__pycache__')
for name,target in [('verified-cont-0013-hf','accepted-HF13'),('verified-cont-0014-gain','accepted-gain14')]:shutil.copytree(R/name,P/target,ignore=ignore)
for name in ['round-0012-gain','round-0013-hf','round-0014-gain']:shutil.copytree(R/'continuation'/name,P/'rounds'/name,ignore=ignore)
shutil.copytree(R/'source-post62',P/'source-check25',ignore=ignore)
for name in ['build_three_v62.py','write_v62_docs.py','finalize_v62.py','verify_zip_windows_v62.py','stage_v62.py','continue_three.py','continue_phase18.py','continue_drift24.py','fit_three_hf_fixed_anchor.py','fit_three_gains.py','three_hf_interior_projection.py','three_gain_interior_projection.py','validate_three_model.py','validate_three_source_model.py','source_post62.py','source-post62.log','prepare_fine55.py','fit_three_fine55.py','finish_fine55_first.py','phase18-paused-for-fine55.json','drift24-paused-for-source-post62.json','continuation-state.json','phase-continuation-state.json','drift24-continuation-state.json']:
 if (R/name).exists():shutil.copyfile(R/name,P/name)
for name in ['check.log','launch.json','state.json']:
 if (R/'fine55-first'/name).exists():(P/'fine55-in-progress').mkdir(exist_ok=True);shutil.copyfile(R/'fine55-first'/name,P/'fine55-in-progress'/name)
for name in ['ZIP-proof.json','clean-extraction-proof.json','clean-ZIP-Windows-proof.json','spectral-proof.json','release-proof.json','fresh-source-proof.json']:json.loads((T/name).read_text());shutil.copyfile(T/name,P/name)
S=json.loads((R/'verified-cont-0014-gain/validation.json').read_text())
(P/'README.md').write_text('''# v62: дальнейший подбор исключительно трёхнотного лида

[Полный комплект v62](../../../v62-wip/README.md), [инструкция FL Studio](../../../v62-wip/FL_STUDIO_RU.md), [оригинал → v61 → v62](../../../v62-wip/AB_REFERENCE_V61_V62_WIP.mp3): **0 / 4,168 / 8,336 с**. Сравнение направлено на исходный WAV пользователя. Предыдущая версия — контроль прогресса. Полное совпадение пока не достигнуто.

После проверенного gain2 продолжены 100 существующих HF-коэффициентов и 93 усиления гармоник. Полные `accepted-HF13` и `accepted-gain14` сохраняют исходный выбранный трёхнотный пресет Diva, все 281 параметр, сырой WAV и 12 MIDI-событий точно. В комплект v62 включён **gain14**. Три удержания на фразу, внутренний ARP On; дополнительные MIDI-ноты и новые состояния DSP не добавлены.

Критерий тембра v61 → v62: **0,838107207 → 0,833750165**, общий критерий **0,928066435 → 0,924617531**. Ошибка верхних гармоник **1,261202429 → 1,244583789**. Небольшие ухудшения ERB/огибающей/тел и других измерений видны в [полной таблице](../../../v62-wip/COMPARISON_RU.md). Это ошибки, а не процент сходства на слух. Исходные ограничения относительно первоначальной выбранной трёхнотной основы и все допуски проверок сохранены.

Каждый принятый proof включает свежую Diva, точные raw/all281/12 событий, Windows/native, полный независимый replay собственной подходящей NEW-базы, спектральный fixture и все 12 причинных случаев на четырёх sample rate. Финальный validation.json записывается после всех случаев. Старые 16-нотные источники/базы исключены.

Для полного комплекта дополнительно проверены настоящая DLL по умолчанию относительно выбранного рендера, блоки 47/127/512/2048, FXP/состояние/неверный ID/PDC/тишина на четырёх частотах, побайтовая повторная сборка, чистая распаковка ZIP и фактическая DLL из ZIP с точным воспроизведением полного WAV. Новый ID **0x444c3632**, image base **0x362620000**. v61 и все предыдущие комплекты/ZIP не перезаписаны.

## Новые физические проверки и продолжение

`source-check25/`: ещё 25 настоящих запусков Diva на более новой обработке gain14: PW, баланс осцилляторов, резонанс и частота фильтра, Drift, KeyScale. ARP, огибающие и три удержания сохранены. **Ни одно изменение источника не дало улучшения при тех же строгих пределах.** Поэтому сохранён исходный пользовательский источник. Некоторые недопустимые пробы имеют меньшее численное значение цели; они не приняты и не названы улучшениями. Новый matching-NEW для непринятого изменённого источника не заявляется. Полные пресеты, параметры, измерения и решение сохранены.

В текущем дополнительном исследовании проверяются 55 уже существующих коэффициентов подробного фазового профиля. Его нулевой расчёт совпал с действующим WAV, два ненулевых расчёта — с полной независимой численной реализацией. Проверены свежие carriers и исходный crest. **На момент этого бэкапа полный actual proof нового ненулевого fine55-кандидата ещё не завершён, этот кандидат в v62 не включён.** Для него валидатор переносит существующие 55 значений в C-заголовок и проверяет те же произвольные входы; конечный validation.json должен появиться только после всех проверок.

На время fine55 один фазовый поиск phase18 временно приостановлен с сохранением PID/starttime и всей незаконченной работы; finish_fine55_first.py возобновляет его после исследования. На время 25 source-проверок отдельно приостанавливалась трёхнотная Drift24-семья, после завершения она **уже возобновлена**. Исходная HF/gain-семья продолжала работу. Снимки состояния в Git не означают, что процессы переживают остановку машины. Не запускать второй экземпляр, не возобновлять прежние 16-нотные поиски.

GUI FL Studio и прослушивание ассистентом здесь не выполнялись. MistaTowa исключён. Пользователь просит продолжать до совпадения или лимита; этот бэкап не завершает подбор.
''')
shutil.copytree(T/'v62-wip',D);shutil.copyfile(T/'Diva_lead_v62_WIP_checkpoint.zip',REPO/'Diva_lead_v62_WIP_checkpoint.zip')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
release=json.loads((REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
for k,v in list(release.items()):
 if isinstance(v,str):release[k]=v.replace('v61','v62').replace('V61','V62').replace('v60','v61').replace('V60','V61')
release.update(ZIP_SHA256=sha(REPO/'Diva_lead_v62_WIP_checkpoint.zip'),DLL_SHA256=sha(D/'Diva_Lead_Finish_v62_WIP_x64.dll'),score=S['score'],tone_score=S['tone_score'],research_model='diva-lead/research/three-held-continuation/after-v62')
(REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').write_text(json.dumps(release,indent=2)+'\n')
current=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text());current.update(selected_complete_release='diva-lead/v62-wip',research_validation='after-v62/accepted-gain14/validation.json',score=S['score'],tone_score=S['tone_score'],selected_complete_release_score=S['score'],selected_complete_release_tone_score=S['tone_score'],latest_research_is_not_a_new_complete_DLL_release=False)
(ROOT/'CURRENT_THREE_NOTE_MODEL.json').write_text(json.dumps(current,indent=2)+'\n')
p=ROOT/'README.md';s=p.read_text();a=s.index('Полный проверенный промежуточный комплект:');b=s.index('\n\n',a);s=s[:a]+'''Полный проверенный промежуточный комплект: [v62](../../v62-wip/README.md), [инструкция FL Studio](../../v62-wip/FL_STUDIO_RU.md). [A/B оригинал → v61 → v62](../../v62-wip/AB_REFERENCE_V61_V62_WIP.mp3): 0 / 4,168 / 8,336 с. [Подборы и проверки](after-v62/README.md), [текущая трёхнотная основа](CURRENT_THREE_NOTE_MODEL.json). Точное совпадение ещё не достигнуто, работа продолжается до совпадения или лимита.'''+s[b:];p.write_text(s)
p=REPO/'README.md';s=p.read_text();before,archive=s.split('**Архивный исследовательский этап:**',1);before=before.replace('v61','v62').replace('V61','V62').replace('v60','v61').replace('V60','V61');before=before.replace('Ошибки верхних гармоник, межгармонической энергии и уровней срабатываний уменьшились','Ошибки верхних гармоник и мощности гармоник уменьшились');p.write_text(before+'**Архивный исследовательский этап:**'+archive)
(P/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(P))+'\n' for p in sorted(P.rglob('*')) if p.is_file()))
print('COMPLETE_V62_KIT_AND_NEW_FULL_PROOFS_AND25_SOURCE_CHECKS_STAGED',flush=True)
