"""Start only the local headless X server required by the Wine plugin hosts."""
from pathlib import Path
import argparse,json,socket,subprocess,time
a=argparse.ArgumentParser();a.add_argument('--probe-only',action='store_true');args=a.parse_args();number=91 if args.probe_only else 90;endpoint=Path('/tmp/.X11-unix')/('X'+str(number));binary=Path('/tmp/divalead-native-effects/xvfb-verified/usr/bin/Xvfb');assert binary.is_file()
def connected():
 s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
 try:s.connect(str(endpoint));return True
 except OSError:return False
 finally:s.close()
if connected():
 assert not args.probe_only,'Probe display already in use; preserve it';print(json.dumps(dict(display=':'+str(number),existing_local_X_socket_responds=True)))
else:
 assert not endpoint.exists(),'Preserve an existing X socket and inspect its owner'
 log=Path(__file__).resolve().parent/('XVFB-display-'+str(number)+'.log')
 with log.open('ab',buffering=0)as f:child=subprocess.Popen([str(binary),':'+str(number),'-screen','0','1280x800x24','-nolisten','tcp','-ac'],stdin=subprocess.DEVNULL,stdout=f,stderr=f,start_new_session=True)
 try:
  deadline=time.monotonic()+10
  while not connected():
   assert child.poll()is None,log.read_text(errors='replace')[-1000:]
   if time.monotonic()>deadline:raise TimeoutError('No local X socket after startup')
   time.sleep(.05)
  print(json.dumps(dict(display=':'+str(number),local_X_socket_responds=True,PID=child.pid,test_server_stopped_on_exit=args.probe_only)))
 finally:
  if args.probe_only:child.terminate();child.wait(timeout=10)
