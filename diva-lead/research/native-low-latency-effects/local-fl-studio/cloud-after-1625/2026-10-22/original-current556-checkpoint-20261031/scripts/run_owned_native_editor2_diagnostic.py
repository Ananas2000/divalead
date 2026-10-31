"""Own isolated native editor probe with proper SDK application HWND; 120s cap."""
from pathlib import Path
import datetime,json,os,subprocess,time
T=Path(__file__).resolve().parent;R=T/'WS_EDITOR2_DIAGNOSTIC';R.mkdir(exist_ok=False);commands=R/'commands.jsonl';commands.touch();S=T.parent.parent/'divalead-setup';W=Path('/tmp/divalead-native-effects');state=T.parent/'native-low-latency-effects/validated-bases/FL20_NATIVE_ZL_REBASED_10/verification/SOURCE_WaveShaper.bin'
win=lambda p:'Z:'+str(Path(p).resolve()).replace('/','\\')
env=dict(os.environ,WINEPREFIX=str(W/'wine'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(W/'cache'))
out=(R/'stdout.log').open('wb',buffering=0);err=(R/'stderr.log').open('wb',buffering=0);child=subprocess.Popen([str(S/'sysroot/usr/lib/wine/wine64'),str(W/'fl_native_WS_editor_probe2.exe'),win(W/'plugins/Fruity_WaveShaper_x64/Fruity WaveShaper_x64.dll'),win(state)],stdin=subprocess.PIPE,stdout=out,stderr=err,env=env)
(R/'OWNER.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=child.pid,starttime=(Path('/proc')/str(child.pid)/'stat').read_text().split()[21],not_FL_Studio=True,SDK_AppHandle_and_MainFormHandle_initialized=True),indent=2)+'\n');deadline=time.monotonic()+120;offset=0
try:
 while time.monotonic()<deadline and child.poll()is None:
  with commands.open()as f:f.seek(offset);lines=f.readlines();offset=f.tell()
  for line in lines:
   cmd=json.loads(line)['command'];assert cmd.startswith(('CAPTURE ','SAVE ','CLICK ','RCLICK ','Q'))and'\n'not in cmd and'\r'not in cmd;child.stdin.write((cmd+'\n').encode());child.stdin.flush()
  if(R/'STOP').exists():break
  time.sleep(.1)
finally:
 if child.poll()is None:
  child.terminate()
  try:child.wait(timeout=5)
  except subprocess.TimeoutExpired:child.kill();child.wait()
 out.close();err.close();(R/'CLOSED.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),only_owned_GUI_process_closed=True,returncode=child.returncode,no_DSP_workers_or_Wine_server_terminated=True),indent=2)+'\n')
