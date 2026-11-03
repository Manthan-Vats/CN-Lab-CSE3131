# How to download and run the labs on a lab PC

## 1. What to download

You only need the **`.pkt` file** for the program you're doing. The configuration is already
inside it: devices, cables, IP addresses, routing, VLANs, NAT, passwords. You don't paste anything.

| Program | Download | Then also read |
|---|---|---|
| 1 Device tour | `P01_Intro_PacketTracer_NetSim/P01_Device_Tour.pkt` | its README (NetSim part is theory) |
| 2 Network commands | `P02_Network_Utility_Commands/P02_Commands_Practice.pkt` | README (commands + real outputs) |
| 3 Star hub/switch | `P03_Star_Topology_Hub_Switch/P03_Star_Hub_and_Switch.pkt` | |
| 4 DHCP | `P04_DHCP_Configuration/P04_DHCP_Router.pkt` | |
| 5 Router modes | `P05_Router_Modes_Basic_Commands/P05_Router_Switch_Basics.pkt` | README (command list) |
| 6 Static routing | `P06_Static_Routing/P06_Static_Routing.pkt` | |
| 7 RIP | `P07_RIPv1_RIPv2/P07a_RIPv1.pkt` and `P07b_RIPv2.pkt` | |
| 8 OSPF | `P08_OSPF/P08a_OSPF_Manual_2_Routers.pkt` (manual), `P08b_OSPF_3_Routers_Video.pkt` (YouTube video), `P08c_..._BROKEN.pkt` (troubleshooting) | |
| 9 VLAN | `P09_VLAN/P09a_VLAN_Two_Switches_Trunk.pkt`, `P09b_InterVLAN_Router_on_a_Stick.pkt` | |
| 10 NAT | `P10_NAT/P10a_Static_NAT.pkt`, `P10b_Dynamic_NAT.pkt`, `P10c_PAT_Overload.pkt` | |
| 11 Nmap/Wireshark | `P11_Nmap_Wireshark_Network_Scanner/netscanner.py` | README (no .pkt; real tools) |
| 12 Security | `P12_Network_Security/P12_Device_Security_ACL_SSH.pkt` | README (one extra step for SSH) |
| 13 Case study | `P13_Case_Study_Scaling_Network/P13a_...pkt`, `P13b_...pkt`, `P13c_..._BROKEN.pkt` | |

**Option A: one file.** Open the file on GitHub, then click the **⬇ Download raw file** button
(top-right of the file view). *Don't* use right-click > Save link on the file list: that saves
a web page, not the `.pkt`.

**Option B: everything at once (easiest).** On the repo's main page, click the green
**Code** button, then **Download ZIP**. Right-click the zip and choose **Extract All**. You get
every lab, config and README offline.

No internet on the lab PC? Download the ZIP on your phone or laptop and copy it over on a pen drive.

## 2. Open it in Packet Tracer

1. Any Cisco Packet Tracer from **7.x up to 9.x** should work, including older lab installs such
   as 8.0, 8.1 and 8.2.0 (Help > About shows your version). The files carry a deliberately
   old version stamp so older copies don't reject them.
2. Double-click the `.pkt`, or in Packet Tracer use **File > Open** and pick it.
   If it asks you to log in, use your college Networking Academy / Skills for All account, or
   choose guest mode if the lab PC offers it.
3. **Wait 30–60 seconds**, or click **Fast Forward Time** (bottom-left, next to Realtime) 3–4 times.
   - Link lights go from orange to green (switch spanning tree).
   - Routers exchange OSPF/RIP routes.
   - DHCP PCs get their addresses.

Pinging before this finishes gives timeouts. That doesn't mean the file is broken.

## 3. Check that it works

- **Ping:** click a PC > **Desktop** > **Command Prompt** > `ping <IP>`. Losing the first
  reply ("Request timed out" once) is normal: that's ARP.
- **See the configuration:** click a router or switch > **CLI** tab > press Enter > `enable` >
  `show running-config` (space for the next page).
- **What should happen:** every lab has a `<file>.results.md` listing each ping and whether
  it should succeed or fail, plus the IP and cabling tables. Some failures are deliberate (VLAN
  isolation, ACL block, NAT without a mapping, the BROKEN labs).

Quick tests for each lab:

| Lab | Try this | Expect |
|---|---|---|
| P01 | PC0: `ping 192.168.1.100` | reply |
| P02 | PC0: `nslookup www.cnlab.local`, `tracert 192.168.2.100`, `ipconfig /all`, `arp -a` | name resolves, 2 hops |
| P03 | PC0: `ping 192.168.1.5`; Simulation mode shows the hub flooding but the switch not | reply |
| P04 | PC > Desktop > IP Configuration shows **DHCP** with a 192.168.1.x address; router: `show ip dhcp binding` | addresses leased |
| P05 | router CLI: `enable` (password `class`), `show ip interface brief` | interfaces up |
| P06 | PC0: `ping 192.168.2.2`; router: `show ip route` | reply, `S` routes |
| P07a/b | PC0: `ping 8.0.0.2`; router: `show ip route`, `show ip protocols` | reply, `R` routes |
| P08a/b | PC0: `ping 192.168.3.14` (P08b); router: `show ip ospf neighbor` | reply, neighbours FULL |
| P08c | some pings fail on purpose; find and fix the faults (answers in the README) | |
| P09a | STUDENT PC ↔ STUDENT PC on the other switch works; STUDENT ↔ FACULTY fails | as described |
| P09b | every PC pings every PC | reply |
| P10a/b/c | PC0: `ping 198.51.100.10`, then R1: `show ip nat translations` | reply, translations listed |
| P12 | Guest-PC: `ping 192.168.30.100` | blocked by the ACL; staff PCs get replies |
| P13a/b | Sales-PC1: `ping 198.51.100.10`; Web Browser → `www.example.com` | reply, page loads |
| P13c | faults to troubleshoot (README) | |

**PC shows 0.0.0.0 or 169.254.x.x (DHCP labs P04, P13)?** Open Desktop > IP Configuration,
click **Static**, then **DHCP** again. It asks the router for an address.

**P12 only:** SSH keys can't be stored in a file, so on R1's CLI run:
```
enable                 (password Str0ngEnable!)
configure terminal
crypto key generate rsa general-keys modulus 1024
ip ssh version 2
end
```
Then on Admin-PC run `ssh -l admin 192.168.10.1` (password `Adm1n@123`).

## 4. Save your own copy

Lab PCs often reset. Use **File > Save As** to save to your folder or pen drive (for example
`P06_Static_Routing_<your roll no>.pkt`) before you change or submit anything.

## 5. If a file won't open (backup plan)

- **"This file was created with a newer version"**: the files are stamped `7.0.0.0000`, so this
  should only appear on Packet Tracer 6.x or older. If you do see it, note the version in
  Help > About and re-stamp the file on any PC with Python 3 (you can do this at home):
  ```
  python tools/restamp.py --show P06_Static_Routing/P06_Static_Routing.pkt
  python tools/restamp.py P06_Static_Routing/P06_Static_Routing.pkt --version 6.0.0.0000 --out fixed
  ```
  (`--version` can be any number at or below the lab's version.) Otherwise rebuild by hand
  using the next point.
- **Opens, but a device looks wrong or misbehaves on a very old version**: use the hand-rebuild
  below. The `configs/` text is plain IOS and works on any version.
- **Rebuild by hand in about 5 minutes:**
  1. Place the devices listed in `<file>.results.md` (2911 routers, 2960 switches, PC-PT).
  2. For serial links, add the **HWIC-2T** module to the router: power it off, drag in the
     module, power it on.
  3. Cable them following the cabling table.
  4. Open each device's CLI tab, type `enable` then `configure terminal`, and paste the
     matching `configs/<file>/<device>.txt`.
  5. Set the PC IPs from the addressing table (Desktop > IP Configuration).

## 6. Program 11 (no Packet Tracer)

Download `netscanner.py` and run it in Command Prompt (needs Python 3, nothing else):
```
python netscanner.py ports 127.0.0.1
python netscanner.py sweep 192.168.1.0/28
python netscanner.py arp
```
For Nmap and Wireshark, install them from nmap.org and wireshark.org and follow the README.
Scan only your own PC, or the lab network if your instructor allows it.
