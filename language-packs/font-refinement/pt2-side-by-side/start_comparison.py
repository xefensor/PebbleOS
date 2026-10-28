"""Open the manual and generated previews as two independent PT2 windows."""
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

out=Path(__file__).resolve().parent
root=out.parent
repo=root.parents[1]
build=repo/'cmake-build-matrix/qemu_emery-normal'
qemu='/home/xela/pebbleos-sdk-0.1.8/qemu/bin/qemu-pebble'
# Stop only our previous preview instances before replacing their monitor socket.
for folder in [root/'pt2-candidate-check',root/'pt2-generated-check',out/'manual',out/'generated']:
    pidfile=folder/'qemu.pid'
    if not pidfile.exists():continue
    pid=int(pidfile.read_text())
    proc=Path('/proc')/str(pid)/'cmdline'
    if proc.exists() and str(folder/'pebbleos.elf').encode() in proc.read_bytes():
        os.kill(pid,signal.SIGTERM)
time.sleep(.5)
for key,source,title,port in [
    ('manual','pt2-candidate-check','PT2 - 1 Manualni upravy',12544),
    ('generated','pt2-generated-check','PT2 - 2 Generovano z TTF',12644),
]:
    dest=out/key
    dest.mkdir(exist_ok=True)
    for name in ['pebbleos.elf','qemu_spi_flash.bin']:
        shutil.copy2(root/source/name,dest/name)
    monitor=build/'qemu-mon.sock' if key=='manual' else dest/'qemu-mon.sock'
    cmd=[qemu,'-name',title,'-rtc','base=localtime',
         '-monitor',f'unix:{monitor},server=on,wait=off',
         '-qmp',f'unix:{dest}/qmp.sock,server=on,wait=off',
         '-serial',f'file:{dest}/uart1.log',
         '-serial',f'tcp:127.0.0.1:{port},server=on,wait=off',
         '-serial',f'tcp:127.0.0.1:{port+1},server=on,wait=off',
         '-machine','pebble-emery,audiodev=snd0','-audiodev','none,id=snd0',
         '-kernel',str(dest/'pebbleos.elf'),
         '-drive',f'if=mtd,format=raw,file={dest}/qemu_spi_flash.bin',
         '-display','sdl,show-cursor=on']
    env=dict(os.environ,SDL_VIDEODRIVER='x11')
    with (dest/'qemu.log').open('w') as log:
        p=subprocess.Popen(cmd,cwd=repo,env=env,stdout=log,stderr=log,stdin=subprocess.DEVNULL,start_new_session=True)
    (dest/'qemu.pid').write_text(str(p.pid)+'\n')
    print(title,p.pid,flush=True)
time.sleep(3)
from pebble import pulse2,commander
from pbl.emulator import Monitor
for port in [12545,12645]:
    interface=pulse2.Interface.open_dbgserial(url=f'socket://127.0.0.1:{port}')
    prompt=commander.apps.Prompt(interface.get_link())
    print(port,list(prompt.command_and_response('app launch -100')),flush=True)
    prompt.close()
time.sleep(2)
# Manual starts at Bitham 30; generated starts at Droid Serif.
for _ in range(3):
    with Monitor(str(build/'qemu-mon.sock')) as m:m.command('sendkey right 100')
    time.sleep(1)
for title,x in [('PT2 - 1 Manualni upravy',100),('PT2 - 2 Generovano z TTF',550)]:
    subprocess.run(['wmctrl','-r',title,'-e',f'0,{x},140,400,456'],check=False)
subprocess.run([str(repo/'.venv/bin/pbl'),'-b',str(build),'screenshot','--output',str(out/'manual-droid.png')],cwd=repo,check=True)
with Monitor(str(out/'generated/qemu-mon.sock')) as m:m.command(f'screendump {out}/generated-droid.png -f png')
print('Both windows show Droid Serif, sample 1.',flush=True)
