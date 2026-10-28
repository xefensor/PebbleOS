import os
from pathlib import Path
import subprocess

out = Path(__file__).resolve().parent
repo = out.parents[2]
build = repo / 'cmake-build-matrix/qemu_emery-normal'
qemu = '/home/xela/pebbleos-sdk-0.1.8/qemu/bin/qemu-pebble'
cmd = [qemu, '-rtc', 'base=localtime',
       '-monitor', f'unix:{build}/qemu-mon.sock,server=on,wait=off',
       '-qmp', f'unix:{build}/qmp.sock,server=on,wait=off',
       '-serial', f'file:{out}/uart1.log',
       '-serial', 'tcp:127.0.0.1:12444,server=on,wait=off',
       '-serial', 'tcp:127.0.0.1:12445,server=on,wait=off',
       '-machine', 'pebble-emery,audiodev=snd0', '-audiodev', 'none,id=snd0',
       '-kernel', str(out/'pebbleos.elf'),
       '-drive', f'if=mtd,format=raw,file={out}/qemu_spi_flash.bin',
       '-display', 'sdl,show-cursor=on']
with (out/'qemu.log').open('a') as log:
    proc = subprocess.Popen(cmd, cwd=repo, stdout=log, stderr=log, stdin=subprocess.DEVNULL, start_new_session=True)
(out/'qemu.pid').write_text(str(proc.pid)+'\n')
print('QEMU PID', proc.pid)
