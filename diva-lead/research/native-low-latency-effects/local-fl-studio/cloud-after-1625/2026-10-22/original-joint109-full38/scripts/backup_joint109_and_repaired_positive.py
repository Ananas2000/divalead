"""Back up both completed experiments in order; the positive is not yet adopted."""
from pathlib import Path
import json,shutil,subprocess,sys
T=Path(__file__).resolve().parent;H=T.parent/'stereo-refinement-20261026';O=T.parent/'stereo-refinement-20261025'
for root,label,note,names,retain in [
 (T/'JOINT_PRIMARY_POST_109_CURRENT413','original-primary-post109-extra-Air-not-adopted','Совместный PRIMARY94+POST15 по трём фиксированным реальным native-входам:1453 предложения/4359DSP, два unseen. Fresh12 подтвердили улучшение: first6 0.00140558, first10 0.00139962, обаcold положительные; все прежние absolute/paired stereo и Air+.02 пройдены. Но заранее добавленная цель Air<=0 НЕ пройдена: first10+0.00009165 dB, cold+0.001433/+0.000538. Не принят; гейт не ослаблялся. Источник Diva заново повторён побитово, все281/12MIDI точны, три длинные/ARP/ADSR/native12/trim прежние. Оба workers/bothZLs neutral0/0. Все36 final WAV, training/native/source WAV, два component и полные оценки/код сохранены. Последующая отдельная малогейновая коррекция проверяется и архивируется отдельно.',['study_joint_primary_post109_current413.py','Joint_primary_post109_support.py','joint_primary_post_fit.py'],False),
 (T/'JOINT109_AIR_MARGIN_REPAIR','original-joint109-Air-margin-positive','Отдельная новая коррекция прежнего joint109 без ослабления Air<=0. Только одинаковые малые сдвиги Gain и TargetGain активных20/21/22,64 настоящих комбинации на3COMMONinputs,2unseen, затем12НОВЫХпар. First6gain0.00140746/SEM0.00002117, first10gain0.00137983/SEM0.00001899; обаcold0.00147628/0.00135936. Airfirst10-0.004961dB, обаcold-0.005367/-0.003893. Все12 прежних absolute/paired stereo-гейтов пройдены. Источник/3длинные/ARP/ADSR/native12/joint109POST/trim не менялись. Положительная исследовательская точка, ЕЩЁ НЕ принята: нужны latest-context проверка, полный FL20 ZIP, независимый cold-replay и публикация. Все36 final и сохранённые training WAV, состояния/64оценки/код включены.',['repair_joint109_air_margin.py','Joint109_air_margin_support.py'],True),
]:
 s=json.loads((root/'completion.json').read_text());assert s['robust_improvement']==retain;scripts=root/'scripts';scripts.mkdir(exist_ok=True)
 for name in names:shutil.copyfile(T/name,scripts/name)
 for name in ['checked_mean_three_real_primary_fit.py','normal_staged_primary_fit.py']:shutil.copyfile(H/name,scripts/name)
 shutil.copyfile(Path(__file__),scripts/Path(__file__).name)
 args=[sys.executable,'-B',str(O/'backup_complete_finite_study.py'),'--root',str(root),'--label',label,'--note',note]
 if retain:args.append('--retain-local-audio')
 subprocess.run(args,check=True)
