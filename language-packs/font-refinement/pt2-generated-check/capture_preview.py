from pathlib import Path
import socket
import subprocess
import time
from pebble import pulse2, commander

out=Path(__file__).resolve().parent
repo=out.parents[2]
build=repo/'cmake-build-matrix/qemu_emery-normal'
interface=pulse2.Interface.open_dbgserial(url='socket://127.0.0.1:12445')
prompt=commander.apps.Prompt(interface.get_link())
print(list(prompt.command_and_response('app launch -100')),flush=True)
prompt.close()
time.sleep(2)

def key(name):
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
        s.settimeout(2)
        s.connect(str(build/'qemu-mon.sock'))
        s.recv(4096)
        s.sendall(('sendkey '+name+' 100\n').encode())
        time.sleep(.6)
    time.sleep(.6)

def screenshot(name):
    subprocess.run([str(repo/'.venv/bin/pbl'),'-b',str(build),'screenshot','--output',str(out/(name+'.png'))],cwd=repo,check=True)

screenshot('DROID_SERIF_28_BOLD')
key('down')
screenshot('DROID_SERIF_28_BOLD-accents')
key('up')
key('right')
screenshot('ROBOTO_CONDENSED_21')
key('down')
screenshot('ROBOTO_CONDENSED_21-accents')
key('up')
