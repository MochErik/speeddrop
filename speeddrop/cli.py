"""SpeedDrop CLI Main Entrypoint."""

import argparse
import os
import sys
from typing import List

from speeddrop.lan_ip import get_local_lan_ip
from speeddrop.server import start_send_server, start_receive_server

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"


def main(args: List[str] = None):
    parser = argparse.ArgumentParser(
        prog="speeddrop",
        description="⚡ SpeedDrop - Instant Peer-to-Peer Wi-Fi LAN File Transfer CLI",
        epilog="Examples:\n"
               "  speeddrop send document.pdf      # Share file across local Wi-Fi\n"
               "  speeddrop receive ./downloads    # Start receiver server on local Wi-Fi\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="subcommand")

    # Send
    send_p = subparsers.add_parser("send", help="Share a local file to other devices on the same Wi-Fi")
    send_p.add_argument("file", help="File to share")
    send_p.add_argument("--port", "-p", type=int, default=8765, help="Port to listen on (default: 8765)")

    # Receive
    rec_p = subparsers.add_parser("receive", help="Receive files from other devices via web UI")
    rec_p.add_argument("dest", nargs="?", default="./received", help="Destination folder (default: ./received)")
    rec_p.add_argument("--port", "-p", type=int, default=8765, help="Port to listen on (default: 8765)")

    parsed = parser.parse_args(args)
    local_ip = get_local_lan_ip()

    if parsed.subcommand == "send":
        if not os.path.exists(parsed.file):
            print(f"{YELLOW}❌ Error: File '{parsed.file}' not found.{RESET}")
            sys.exit(1)
        start_send_server(parsed.file, local_ip, parsed.port)
    elif parsed.subcommand == "receive":
        start_receive_server(parsed.dest, local_ip, parsed.port)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
