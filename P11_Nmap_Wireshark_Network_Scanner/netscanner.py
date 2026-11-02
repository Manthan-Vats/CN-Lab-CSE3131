"""Program 11 - a small network scanner (standard-library Python 3, no installs).

Does the three things the manual lists for a "network scanner":
  1. host discovery  - ping sweep of an IP range (ICMP echo via the system ping)
  2. MAC lookup      - reads the ARP table after the sweep (IP -> MAC)
  3. port scan       - TCP connect() scan of chosen ports, with service names

Only scan machines you own or have permission to scan.

Examples
    python netscanner.py ports 127.0.0.1                 # common ports on this PC
    python netscanner.py ports 127.0.0.1 -p 1-1024       # a port range
    python netscanner.py sweep 192.168.1.0/28            # who is alive on (part of) your LAN
    python netscanner.py arp                             # show the ARP cache
"""

import argparse
import concurrent.futures as cf
import ipaddress
import platform
import re
import socket
import subprocess
import time

COMMON = [20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 123, 135, 137, 139, 143, 161,
          389, 443, 445, 587, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 8080, 8443]
WINDOWS = platform.system() == "Windows"


def ping(ip, timeout_ms=600):
    """True if `ip` answers one ICMP echo request."""
    cmd = ["ping", "-n", "1", "-w", str(timeout_ms), ip] if WINDOWS else \
          ["ping", "-c", "1", "-W", str(max(1, timeout_ms // 1000)), ip]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    # Windows returns 0 for "Destination host unreachable" too, so look for a real reply
    return r.returncode == 0 and ("TTL=" in r.stdout.upper())


def arp_table():
    """{ip: mac} parsed from `arp -a`."""
    out = subprocess.run(["arp", "-a"], stdout=subprocess.PIPE, text=True).stdout
    table = {}
    for ip, mac in re.findall(r"(\d+\.\d+\.\d+\.\d+)\D+?([0-9a-fA-F]{2}(?:[-:][0-9a-fA-F]{2}){5})", out):
        table[ip] = mac.lower().replace("-", ":")
    return table


def scan_port(ip, port, timeout=0.5):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((ip, port)) == 0   # 0 = TCP handshake completed = port open


KNOWN = {1433: "ms-sql", 1521: "oracle", 3306: "mysql", 3389: "rdp", 5432: "postgresql",
         5900: "vnc", 8080: "http-alt", 8443: "https-alt"}


def service(port):
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return KNOWN.get(port, "?")


def parse_ports(spec):
    ports = set()
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            ports.update(range(int(a), int(b) + 1))
        else:
            ports.add(int(part))
    return sorted(p for p in ports if 0 < p < 65536)


def cmd_sweep(args):
    net = ipaddress.IPv4Network(args.network, strict=False)
    if net.num_addresses > 1024:
        raise SystemExit("range too large (max /22) - scan less at a time")
    t = time.time()
    hosts = [str(h) for h in net.hosts()]
    with cf.ThreadPoolExecutor(64) as ex:
        alive = [h for h, up in zip(hosts, ex.map(ping, hosts)) if up]
    arp = arp_table()
    print("Ping sweep of %s: %d of %d hosts answered (%.1fs)" % (net, len(alive), len(hosts), time.time() - t))
    print("%-16s %-18s %s" % ("IP address", "MAC address", "Hostname"))
    for h in alive:
        try:
            name = socket.gethostbyaddr(h)[0]
        except OSError:
            name = ""
        print("%-16s %-18s %s" % (h, arp.get(h, "(this PC / not in ARP)"), name))


def cmd_ports(args):
    ip = socket.gethostbyname(args.host)
    ports = parse_ports(args.ports) if args.ports else COMMON
    t = time.time()
    with cf.ThreadPoolExecutor(100) as ex:
        res = list(ex.map(lambda p: (p, scan_port(ip, p, args.timeout)), ports))
    opened = [p for p, ok in res if ok]
    print("TCP connect scan of %s (%s): %d ports in %.1fs" % (args.host, ip, len(ports), time.time() - t))
    print("%-8s %-7s %s" % ("PORT", "STATE", "SERVICE"))
    for p in opened:
        print("%-8s %-7s %s" % ("%d/tcp" % p, "open", service(p)))
    print("%d closed or filtered ports not shown" % (len(ports) - len(opened)))


def cmd_arp(args):
    for ip, mac in sorted(arp_table().items(), key=lambda x: ipaddress.IPv4Address(x[0])):
        print("%-16s %s" % (ip, mac))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sweep", help="ping sweep + ARP lookup")
    s.add_argument("network", help="e.g. 192.168.1.0/24")
    s.set_defaults(fn=cmd_sweep)
    p = sub.add_parser("ports", help="TCP connect port scan")
    p.add_argument("host")
    p.add_argument("-p", "--ports", help="e.g. 22,80,443 or 1-1024 (default: 31 common ports)")
    p.add_argument("-t", "--timeout", type=float, default=0.5)
    p.set_defaults(fn=cmd_ports)
    a = sub.add_parser("arp", help="print the ARP cache")
    a.set_defaults(fn=cmd_arp)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
