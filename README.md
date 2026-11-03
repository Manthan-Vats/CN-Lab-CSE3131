# Computer Networks Lab (CSE3131): all practicals, ready to open

Every experiment from the CN Lab manual (July–Nov 2026), redone. Each Packet Tracer lab is a
finished `.pkt` file: devices placed, cables connected, every router and switch configured,
and the configuration saved. Download one, double-click it, and ping.

| # | Program | Open this | Also inside |
|---|---|---|---|
| 1 | Introduction to Packet Tracer & NetSim, device components | [`P01_Device_Tour.pkt`](P01_Intro_PacketTracer_NetSim/) | every device and cable type, NetSim write-up |
| 2 | Network utility commands (ping, netstat, ipconfig, arp, tracert, nslookup, pathping) | [`P02_Commands_Practice.pkt`](P02_Network_Utility_Commands/) | real Windows outputs of every command |
| 3 | Star topology with hub and switch, show/copy, password, hostname | [`P03_Star_Hub_and_Switch.pkt`](P03_Star_Topology_Hub_Switch/) | |
| 4 | DHCP on a router | [`P04_DHCP_Router.pkt`](P04_DHCP_Configuration/) | |
| 5 | Router modes, router and switch basic commands | [`P05_Router_Switch_Basics.pkt`](P05_Router_Modes_Basic_Commands/) | command reference |
| 6 | Static routing | [`P06_Static_Routing.pkt`](P06_Static_Routing/) | |
| 7 | RIPv1 and RIPv2 | [`P07a_RIPv1.pkt`, `P07b_RIPv2.pkt`](P07_RIPv1_RIPv2/) | |
| 8 | OSPF and troubleshooting | [`P08a` manual, `P08b` YouTube 3-router, `P08c` broken](P08_OSPF/) | fault-finding exercise |
| 9 | VLAN and troubleshooting | [`P09a` VLAN + trunk, `P09b` inter-VLAN](P09_VLAN/) | |
| 10 | NAT | [`P10a` static, `P10b` dynamic, `P10c` PAT](P10_NAT/) | |
| 11 | Nmap, Wireshark, network scanner | [folder](P11_Nmap_Wireshark_Network_Scanner/) | `netscanner.py` (Python scanner) |
| 12 | Security: threats, attacks, mitigation, device security | [`P12_Device_Security_ACL_SSH.pkt`](P12_Network_Security/) | |
| 13 | Case study: build a small network, scale it, troubleshoot | [`P13a`, `P13b`, `P13c`](P13_Case_Study_Scaling_Network/) | |

## How to use a file

**Step-by-step guide for lab PCs (which file, download, open, test, fallback): [HOW_TO_RUN.md](HOW_TO_RUN.md)**

1. Open the program's folder and click the `.pkt` file, then **Download raw file** (the ⬇ button).
2. Open it in **Cisco Packet Tracer 7.x, 8.x or 9.x**. The files are stamped as version
   `7.0.0.0000`, so older lab installs (8.0, 8.1, 8.2.0) don't reject them as "created with a
   newer version". See [HOW_TO_RUN.md](HOW_TO_RUN.md) if yours still complains.
3. Wait about 30–60 seconds. Switch ports go from orange to green while spanning tree settles,
   and OSPF/RIP need a few seconds to exchange routes. To skip the wait, press **Fast Forward Time**
   (bottom-left) a few times.
4. Click a PC > **Desktop** > **Command Prompt** > `ping <address>`. The first ping may lose one
   packet while ARP resolves. That's normal.

Every folder has:

- **`README.md`**: aim, theory, step-by-step procedure (to build it yourself), commands
  explained, verification, troubleshooting, and answers to the viva questions.
- **`configs/<device>.txt`**: the full CLI for each router or switch. To rebuild a lab by hand,
  place and cable the devices, then paste the file into the device's CLI tab.
- **`<file>.results.md`**: the addressing table, cabling table, expected routing tables and
  the expected result of every ping.

All routers are **Cisco 2911** (Gig0/0–0/2 plus an HWIC-2T card for Serial0/0/0–0/0/1), all
switches are **2960-24TT**, and end devices are **PC-PT** / **Server-PT**. These are the default
models in the lab.

## Passwords used

| Where | Password |
|---|---|
| P03 / P05 `enable` | `class` |
| P03 / P05 console and telnet | `cisco` |
| P12 `enable` / console | `Str0ngEnable!` / `Con$ole1` |
| P12 SSH | user `admin`, password `Adm1n@123` |
| All other labs | no passwords |

## How these files were made and checked

There was no Packet Tracer on the machine that made these files, so they were generated
programmatically. Everything needed to rebuild them is in [`tools/`](tools/):

- `ptfile.py` reads and writes the `.pkt` format: zlib, then Twofish-EAX, then two
  obfuscation passes. This is the scheme reverse-engineered by
  [pka2xml](https://github.com/mircodz/pka2xml). Twofish is implemented from the published
  spec and checked against the official test vectors.
- `templates/` holds device blocks taken from real Packet Tracer 8.2.1 saves, so every field
  Packet Tracer expects is present. Only names, MAC addresses, positions, IPs and configs change.
- `labs.py` describes every lab. `build.py` writes the files.
- `validate.py` opens each finished file and checks it: every cable lands on a real port,
  the right cable type is used, no duplicate MACs or names, the physical workspace is valid,
  configs only name interfaces that exist, and startup-config equals running-config (saved).
- `netsim.py` is a small network simulator. It reads the finished file and predicts every
  ping. It covers VLANs and trunks, hubs, static routes, RIPv1/v2, OSPF, DHCP, NAT and ACLs.
  It checks 387 pings across the 20 files, including the ones that must fail (VLAN isolation,
  NAT, ACL, planted faults).
- `selftest.py` breaks working labs on purpose (24 classic mistakes) to prove the simulator
  really catches errors.

- `restamp.py` shows or changes the version stamp of any finished `.pkt` without touching
  anything else (`python restamp.py --show .`, or `python restamp.py file.pkt --version X.Y.Z.W`).
  The default stamp for a rebuild is `FILE_VERSION` in `pktgen.py`.

```
cd tools
python ptfile.py selftest   # Twofish test vectors
python build.py             # rebuild all 20 .pkt files + validate + simulate
python selftest.py          # mutation tests of the simulator
```

What can only be confirmed inside Packet Tracer itself: the file opens, and the animations
and timers behave as described. If a file ever refuses to open, the `configs/` text plus the
cabling table in `<file>.results.md` rebuild it in a few minutes.

Credits and licence notes: [CREDITS.md](CREDITS.md).
