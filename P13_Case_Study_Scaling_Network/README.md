# Program 13: Case study / mini project: build a small network, scale it, troubleshoot

**Aim:** design a small office network, scale it to a multi-department network, and
troubleshoot the problems that come up while scaling.

## Files

| File | Phase |
|---|---|
| `P13a_Phase1_Small_Office.pkt` | Phase 1: one router (DHCP + Internet via PAT), one switch, two PCs |
| `P13b_Phase2_Scaled_Network.pkt` | Phase 2: departments in VLANs, file server, OSPF, backup router, redundant Internet |
| `P13c_Phase3_Troubleshooting_BROKEN.pkt` | Phase 3: phase 2 with planted faults to troubleshoot |
| `configs/<file>/<device>.txt` | Commands |
| `<file>.results.md` | Addressing, cabling, routing tables, DHCP leases, expected pings |

## Phase 1: small network

```
 PC0 (DHCP) \                                  Se0/0/0           Se0/0/0
             SW1 --- Gig0/0 192.168.1.1  R1 ===203.0.113.0/30=== ISP --- Internet-Server
 PC1 (DHCP) /        DHCP pool OFFICE, PAT                              198.51.100.10 (www.example.com)
```
- R1 is the DHCP server (`ip dhcp pool OFFICE`, .1–.10 excluded), so PCs get .11 and .12.
- PAT (`ip nat inside source list 1 interface Serial0/0/0 overload`) gives Internet access
  through one public IP.
- Test: PC0 → `ping 192.168.1.12` (file sharing inside the LAN), `ping 198.51.100.10`, and
  Web Browser → `www.example.com`.

## Phase 2: scaled network

```
                   R2 (backup)  Se0/0/0 203.0.113.5 ===== ISP Se0/0/1 .6
                    | Gig0/0 10.0.12.2/30                  |  Gig0/0 198.51.100.1 -- Internet-Server
                    | OSPF area 0                          |
                    | Gig0/1 10.0.12.1/30                  |
                   R1 (main) Se0/0/0 203.0.113.1 ========== ISP Se0/0/0 .2
                    | Gig0/0 trunk: .10 / .20 / .99 sub-interfaces
                 SW-Core ── Fa0/10 File-Server 192.168.99.10 (VLAN 99, DNS files.company.local)
              trunk /    \ trunk
          SW-Sales        SW-HR
   Sales-PC1..3 (VLAN 10)  HR-PC1..3 (VLAN 20)    all DHCP
```

| Requirement (from the manual) | How it's met |
|---|---|
| Two departments, each with its own subnet | VLAN 10 SALES 192.168.10.0/24, VLAN 20 HR 192.168.20.0/24, router-on-a-stick on R1 |
| File server for central storage | File-Server in VLAN 99 SERVERS 192.168.99.0/24 (also DNS) |
| Routing protocol between subnets | OSPF area 0 on R1 and R2 (R2 learns every inside subnet) |
| VLANs to separate department traffic | trunks SW-Core↔SW-Sales/SW-HR, access ports per department |
| Backup router for redundancy | R2 has its own ISP link; R1 has a **floating default route** `ip route 0.0.0.0 0.0.0.0 10.0.12.2 5` (AD 5), used only if the primary link fails; the ISP has a floating route back |
| 20+ more devices | add PCs to SW-Sales/SW-HR access ports; DHCP pools have 244 free addresses each |
| Internet for everyone | PAT to the public pool 203.0.113.65–70 (`ip nat pool PUBLIC ... overload`) |

**Failover test:** on R1 run `interface Serial0/0/0` → `shutdown`, then ping 198.51.100.10
from Sales-PC1. It still works: `tracert` now shows R1 → R2 → ISP. `no shutdown` brings
traffic back to the primary link.

**Verify:**
- `R1# show ip route` (default route S* via 203.0.113.2)
- `show ip ospf neighbor` (R2 FULL)
- `show ip dhcp binding`
- `show ip nat translations`
- `SW-Core# show interfaces trunk`, `show vlan brief`

## Phase 3: troubleshooting (open `P13c_Phase3_Troubleshooting_BROKEN.pkt`)

The manual's three scenarios:

<details><summary>1. Connectivity issue: a PC lost connectivity because of a wrong VLAN</summary>

HR-PC3 (on SW-HR Fa0/3) gets a **192.168.10.x** (SALES) address and can't use HR resources.
- **Find it:** `ipconfig` on HR-PC3; `tracert` shows gateway 192.168.10.1;
  `SW-HR# show vlan brief` shows Fa0/3 in VLAN 10.
- **Fix:** `SW-HR(config)# interface fa0/3` → `switchport access vlan 20`, then on the PC
  switch IP Configuration Static → DHCP to renew.

</details>

<details><summary>2. IP conflict: two devices with the same address</summary>

HR-PC2 was given a **static** 192.168.20.11, which is inside the DHCP range, so DHCP can hand
the same address to another PC. Packet Tracer shows a duplicate-IP warning, or replies go to
the wrong PC.
- **Find it:** `R1# show ip dhcp conflict`; `arp -a` on PCs; Packet Tracer's IP conflict message.
- **Fix:** set HR-PC2 back to DHCP, or give it a static address inside the excluded range
  (.2–.10), or add `ip dhcp excluded-address 192.168.20.11`. Then `clear ip dhcp conflict *`.

</details>

<details><summary>3. Slow performance: one link overloaded (QoS)</summary>

Not reproducible in a ping test. Explain it: a single uplink carries all departments' traffic,
so file transfers delay voice/interactive traffic.
- **Fixes:**
  - QoS: classify traffic with ACLs or NBAR, mark it with DSCP, and give priority/bandwidth
    with `policy-map` + `service-policy`.
  - Add or bundle links (EtherChannel).
  - Move the server closer, or segment further.
- **Packet Tracer demo:** Simulation mode shows the queue building on the busy link.

</details>

## Outcome / conclusion

The network grew from one LAN to three VLANs with central services, dynamic routing, DHCP per
department, NAT, and a redundant Internet path that fails over by itself. Structured design
(VLANs, subnet plan, routing protocol) made it scale, and the standard troubleshooting
sequence (physical → VLAN → IP → gateway → routing → NAT) found the faults quickly.
