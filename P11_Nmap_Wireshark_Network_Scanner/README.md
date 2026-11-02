# Program 11: Network utility tools: Nmap, Wireshark, network scanner

**Aim:** discover hosts and services on a network, find open ports and running services,
and capture and analyse traffic.

> Scan only your own machines or networks you have permission to scan. Scanning other
> people's networks can be illegal and breaks most college IT policies.

## Files

| File | What it is |
|---|---|
| `netscanner.py` | A network scanner written for this lab (Python 3, no installs): ping sweep, ARP (IP→MAC), TCP port scan |
| `sample_output_localhost.txt` | Real run against 127.0.0.1 |

## 1. Network scanner (`netscanner.py`)

```
python netscanner.py ports 127.0.0.1               # 31 common ports on this PC
python netscanner.py ports 127.0.0.1 -p 1-1024     # a range
python netscanner.py sweep 192.168.1.0/28          # who is alive on (part of) your LAN + their MACs
python netscanner.py arp                           # the ARP cache
```
Real output on the PC that wrote this:
```
TCP connect scan of 127.0.0.1 (127.0.0.1): 31 ports in 0.5s
PORT     STATE   SERVICE
135/tcp  open    epmap
445/tcp  open    microsoft-ds
3306/tcp open    mysql
5432/tcp open    postgresql
27 closed or filtered ports not shown
```

**How it works (the manual's algorithm, step by step):**
1. Input target: an IP, hostname, or range in CIDR (`ipaddress` module).
2. Send discovery requests: ICMP echo to every address, 64 in parallel (system `ping`).
3. Receive responses: a reply containing `TTL=` means the host is alive.
4. Resolve MACs: after the sweep, the PC's ARP cache holds IP→MAC for the live hosts (`arp -a`).
5. Scan ports: `socket.connect_ex()` attempts a full TCP 3-way handshake. 0 means the port is
   open; refused or timed out means closed or filtered.
6. Output: open ports with service names (`getservbyport`).

## 2. Nmap

Install from nmap.org (Windows installer includes Zenmap GUI and Npcap).

| Command | Does |
|---|---|
| `nmap -sn 192.168.1.0/24` | host discovery only (ping scan): list of live hosts with MAC + vendor |
| `nmap 192.168.1.10` | top 1000 TCP ports |
| `nmap -p 1-65535 192.168.1.10` | all ports |
| `nmap -sS 192.168.1.10` | SYN ("half-open") scan: SYN → SYN/ACK = open, RST = closed; needs admin |
| `nmap -sT ...` | full TCP connect scan (what `netscanner.py` does) |
| `nmap -sU -p 53,67,161 ...` | UDP scan |
| `nmap -sV 192.168.1.10` | service and version detection |
| `nmap -O 192.168.1.10` | OS detection (TCP/IP fingerprint) |
| `nmap -A 192.168.1.10` | -O + -sV + scripts + traceroute |
| `nmap -oN out.txt ...` | save the report |

Port states: **open** (a service answers), **closed** (reachable, nothing listening),
**filtered** (a firewall dropped the probe, no answer).

Example to practise safely: `nmap -sV 127.0.0.1` or `nmap scanme.nmap.org` (the Nmap project
explicitly allows scanning it).

## 3. Wireshark

1. Install from wireshark.org (with Npcap). Start it and pick the active interface (Wi-Fi/Ethernet).
2. Start the capture, generate traffic (`ping 8.8.8.8`, open a website, `nslookup google.com`), then stop.
3. Apply display filters:

| Filter | Shows |
|---|---|
| `icmp` | ping requests/replies (type 8 / type 0) |
| `arp` | ARP who-has / is-at |
| `dns` | DNS queries and answers (UDP 53) |
| `tcp.port == 443` / `http` | HTTPS / HTTP traffic |
| `tcp.flags.syn == 1 && tcp.flags.ack == 0` | TCP handshake starts (SYN) |
| `ip.addr == 8.8.8.8` | everything to or from one host |
| `dhcp` (`bootp` on old versions) | DORA |

4. Click a packet. The middle pane shows each layer (Frame → Ethernet II → IPv4 → TCP/UDP →
   application), and the bottom pane shows raw bytes.
5. Use **Statistics > Protocol Hierarchy** (protocol distribution), **Statistics >
   Conversations**, and **Follow > TCP Stream**.
6. Save with **File > Save As (.pcapng)** for later analysis.

Capture filters (set before starting, BPF syntax): `host 8.8.8.8`, `port 53`, `icmp`.

No Wireshark? Packet Tracer's **Simulation** mode does the same for lab topologies: an event
list plus a per-layer PDU view.

## Viva answers

1. **Nmap's purpose:** network discovery and security auditing. It sends crafted packets
   (ICMP, TCP SYN/ACK, UDP) and reads the replies (or silence) to find live hosts, open ports,
   services and versions, and the OS.
2. **Wireshark vs Nmap:** Nmap is **active**. It sends probes to map hosts and ports.
   Wireshark is **passive**. It captures and decodes the packets already on the wire.
3. **Using a network scanner:**
   - Choose the IP range.
   - Send ARP/ICMP discovery.
   - Collect replies (live hosts, MACs).
   - Optionally port-scan each host.
   - Report the hosts, MAC vendors and services.
4. **What Nmap reports:** live hosts, MAC address and vendor, open/closed/filtered ports,
   service names and versions, OS guess, traceroute, script results (vulnerabilities, banners).
5. **Wireshark filtering:** with capture filters (BPF, before capture) or display filters
   (`ip.addr==`, `tcp.port==`, protocol names). A busy link produces thousands of packets per
   second, and filters isolate the conversation you care about.
6. **Open ports matter:** every open port is a running service that can be attacked. Unneeded
   open ports widen the attack surface, and knowing them lets you close or firewall them and
   patch the rest.
7. **Ethics:** scan or capture only with written permission. Respect privacy (captures contain
   personal data and passwords). Don't disrupt services. Follow law and policy (in India, the
   IT Act 2000 and the college's policy).
8. **When Wireshark beats Nmap:** diagnosing *why* an application is slow or failing, e.g.
   seeing TCP retransmissions, a DNS server not answering, or a DHCP Offer that never arrives.
   Nmap would only say the port is open.
9. **Pen testing:**
   - Reconnaissance (Nmap discovery).
   - Enumeration (service versions → known CVEs).
   - Traffic analysis (Wireshark: clear-text credentials, weak protocols).
   - Verifying that fixes work.
10. **Limits in a corporate network:**
    - Firewalls and IDS block or flag scans.
    - Switched networks show you only your own traffic (you need SPAN/mirror ports).
    - Encrypted traffic (TLS) hides payloads.
    - Captures get huge.
    - You need authorisation.
    - Aggressive scans can crash fragile devices.
