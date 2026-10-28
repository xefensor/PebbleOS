"""Control the isolated emulator used to review the Czech catalog."""

import argparse
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).resolve().parent
BUILD = OUTPUT / "build-pt2"
sys.path.insert(0, str(ROOT / "tests/integration"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", type=Path)
    parser.add_argument("--console", action="append", default=[])
    parser.add_argument("--sync-time", action="store_true")
    parser.add_argument("--keys", nargs="*", default=[])
    parser.add_argument("--screenshot")
    parser.add_argument("--burst-prefix")
    parser.add_argument("--quit", action="store_true")
    parser.add_argument("--pause", type=float, default=0.6)
    args = parser.parse_args()

    if args.install:
        from harness.connections import start_protocol
        from libpebble2.communication.transports.qemu import QemuTransport
        from libpebble2.services.putbytes import PutBytes, PutBytesType

        pebble = start_protocol(QemuTransport("127.0.0.1", 13444))
        try:
            PutBytes(
                pebble,
                PutBytesType.File,
                args.install.read_bytes(),
                bank=0,
                filename="lang",
            ).send()
            print("Installed", args.install, flush=True)
        finally:
            pebble.transport.socket.close()

    if args.sync_time:
        args.console.insert(0, f"time set {int(time.time())}")

    if args.console:
        from harness.connections.pulse import PulseConnection

        connection = PulseConnection("socket://127.0.0.1:13445")
        connection.open(15)
        try:
            for command in args.console:
                print(command, connection.prompt(command, 15), flush=True)
        finally:
            connection.close()
        time.sleep(args.pause)

    for key in args.keys:
        if key not in {"up", "down", "left", "right"}:
            raise ValueError(f"Unknown key: {key}")
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as monitor:
            monitor.settimeout(2)
            monitor.connect(str(BUILD / "qemu-mon.sock"))
            monitor.recv(4096)
            monitor.sendall(f"sendkey {key} 80\n".encode())
            time.sleep(0.15)
            monitor.recv(4096)
        time.sleep(args.pause)

    def screenshot(name):
        subprocess.run(
            [
                str(ROOT / ".venv/bin/pbl"),
                "-b",
                str(BUILD),
                "emulator",
                "screenshot",
                "--output",
                str(OUTPUT / name),
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        print("Saved", name, flush=True)

    if args.screenshot:
        time.sleep(args.pause)
        screenshot(args.screenshot)

    if args.burst_prefix:
        for index in range(20):
            screenshot(f"{args.burst_prefix}-{index:02d}.png")
            time.sleep(0.2)

    if args.quit:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as monitor:
            monitor.settimeout(2)
            monitor.connect(str(BUILD / "qemu-mon.sock"))
            monitor.recv(4096)
            monitor.sendall(b"quit\n")
        print("Stopped the isolated emulator", flush=True)


if __name__ == "__main__":
    main()
