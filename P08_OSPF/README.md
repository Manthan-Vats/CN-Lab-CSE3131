# Program 8: OSPF configuration and troubleshooting

**Aim:** configure OSPF on multiple routers and troubleshoot common OSPF configuration problems.

## Files

| File | What it is |
|---|---|
| `P08a_OSPF_Manual_2_Routers.pkt` | Manual figure (page 31): R1 and R2 on a serial link 20.0.0.0/8; PC1 10.0.0.2, PC2 30.0.0.2 |
| `P08b_OSPF_3_Routers_Video.pkt` | The YouTube tutorial (Breezy Codes): 3 routers in a serial triangle, 3 switches, 6 PCs |
| `P08c_OSPF_Troubleshooting_BROKEN.pkt` | The same as P08b with **3 planted faults** to find and fix |
| `configs/<file>/<device>.txt` | Commands for each router and switch |
| `<file>.results.md` | Addressing, cabling, OSPF routing tables, expected pings |

## P08a: manual topology

```
 PC1 10.0.0.2 --- Gig0/0 10.0.0.1  R1  Se0/0/0 20.0.0.1 (DCE) ==== 20.0.0.2 Se0/0/0  R2  Gig0/0 30.0.0.1 --- PC2 30.0.0.2
```
```
R1(config)# router ospf 1
R1(config-router)# network 10.0.0.0 0.255.255.255 area 0
R1(config-router)# network 20.0.0.0 0.255.255.255 area 0
R2(config)# router ospf 1
R2(config-router)# network 20.0.0.0 0.255.255.255 area 0
R2(config-router)# network 30.0.0.0 0.255.255.255 area 0
```

## P08b: the YouTube tutorial (https://youtu.be/jF2VXoYY-X8)

```
              10.0.0.0/8
     R0 ========================= R1
      \\                          //
 12.0.0.0/8 \\              // 11.0.0.0/8
               \\        //
                    R2
 Each router: Gig0/0 → its switch Fa0/24; two PCs on Fa0/1, Fa0/2
 R0 LAN 192.168.1.0/24 (PC0 .10, PC1 .11)   R1 LAN 192.168.2.0/24 (PC2 .12, PC3 .13)
 R2 LAN 192.168.3.0/24 (PC4 .14, PC5 .15)   gateway = .1 of each LAN
```

The addresses, networks and OSPF commands match the video exactly. The only difference is the
router model. The video uses *Router-PT-Empty* with modules added by hand; this file uses the
lab's standard **2911 + HWIC-2T**, so the interface names change:

| Video (Router-PT-Empty) | This file (2911) | Used for |
|---|---|---|
| FastEthernet2/0 | GigabitEthernet0/0 | LAN / switch |
| Serial0/0 | Serial0/0/0 | first serial link |
| Serial1/0 | Serial0/0/1 | second serial link |

| Link | Ends | DCE (clock rate 64000) |
|---|---|---|
| 10.0.0.0/8 | R0 Se0/0/0 10.0.0.1 ↔ R1 Se0/0/0 10.0.0.2 | R0 |
| 11.0.0.0/8 | R1 Se0/0/1 11.0.0.1 ↔ R2 Se0/0/0 11.0.0.2 | R1 |
| 12.0.0.0/8 | R0 Se0/0/1 12.0.0.1 ↔ R2 Se0/0/1 12.0.0.2 | R0 |

R0 configuration (the same pattern on R1 and R2; full text in `configs/P08b_OSPF_3_Routers_Video/`):
```
enable
configure terminal
hostname R0
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
 exit
interface Serial0/0/0
 ip address 10.0.0.1 255.0.0.0
 clock rate 64000
 no shutdown
 exit
interface Serial0/0/1
 ip address 12.0.0.1 255.0.0.0
 clock rate 64000
 no shutdown
 exit
router ospf 1                                   ! 1 = process ID, local to this router
 network 192.168.1.0 0.0.0.255 area 0           ! wildcard = inverse of the subnet mask
 network 10.0.0.0 0.255.255.255 area 0
 network 12.0.0.0 0.255.255.255 area 0
 exit
end
write memory
```
The triangle gives redundancy. Shut R0 Se0/0/0 and PC0 still reaches PC2 through R2. OSPF
recomputes the path (the simulator checks this case too).

## Verification

```
R0# show ip ospf neighbor          ! 2 neighbours, State FULL
R0# show ip route ospf
O    11.0.0.0/8 [110/128] via 10.0.0.2, Serial0/0/0  [110/128] via 12.0.0.2, Serial0/0/1
O    192.168.2.0/24 [110/65] via 10.0.0.2, Serial0/0/0
O    192.168.3.0/24 [110/65] via 12.0.0.2, Serial0/0/1
R0# show ip protocols              ! router ID, networks, area
R0# show ip ospf interface brief   ! cost 64 on serial (10^8 / 1.544 Mbps), 1 on Gig
PC0> tracert 192.168.3.14
```
`[110/65]`: 110 = OSPF administrative distance; 65 = cost (64 serial + 1 Gigabit).
OSPF needs about 40 s after the file opens to form adjacencies. Press Fast Forward Time if the
first pings fail.

## P08c: troubleshooting exercise

Open `P08c_OSPF_Troubleshooting_BROKEN.pkt`. Symptoms: PC0 can't reach PC2/PC3, and PC5 can't
reach anything outside its own LAN. Find the three faults before you look below.

<details><summary>Faults and fixes</summary>

| # | Fault | How you find it | Fix |
|---|---|---|---|
| 1 | R1 doesn't advertise its LAN | `show ip route` on R0 has no 192.168.2.0; `show ip protocols` on R1 lists only 10.0.0.0 and 11.0.0.0 | `R1(config)# router ospf 1` → `network 192.168.2.0 0.0.0.255 area 0` |
| 2 | Area mismatch on the R0–R2 link (R2 says area 1) | `show ip ospf neighbor` on R0 shows only R1; `debug ip ospf adj` shows "mismatch area ID" | `R2(config-router)# no network 12.0.0.0 0.255.255.255 area 1` → `network 12.0.0.0 0.255.255.255 area 0` |
| 3 | PC5 default gateway is 192.168.3.100 | `ipconfig` on PC5; `ping 192.168.3.1` works but nothing beyond | set gateway 192.168.3.1 |

</details>

Other common OSPF faults:
- **Wrong wildcard** (e.g. 255.0.0.0 instead of 0.255.255.255): the interface isn't matched.
- **Mismatched hello/dead timers:** `ip ospf hello-interval` differs on the two ends.
- **Passive interface on a link:** no neighbour forms.
- **Interface shut down, or serial without clock:** the link stays down.
- **Duplicate router IDs.**

## Viva answers

1. **OSPF vs RIP:** RIP is distance-vector and OSPF is link-state.

   | | RIP | OSPF |
   |---|---|---|
   | What a router knows | only neighbours' tables | the whole topology (LSDB) |
   | Metric | hop count, max 15 | cost from bandwidth, no hop limit |
   | Updates | full table every 30 s | only on change (LSAs) |
   | Convergence | slow | fast |
   | Scale | small networks | large networks (areas) |
   | AD | 120 | 110 |

2. **Best route:** each router builds a link-state database from the LSAs, then runs
   **Dijkstra's SPF** algorithm with itself as the root. The path with the lowest total cost
   wins, where cost = 10^8 / interface bandwidth (bps). Serial 1.544 Mbps = 64,
   FastEthernet = 1, Gigabit = 1 by default.
3. **Areas and area 0:**
   - An area groups routers that share one LSDB. This limits LSA flooding and SPF work, and
     lets ABRs summarise routes.
   - **Area 0 is the backbone.** Every other area must connect to it, and all inter-area
     traffic passes through it, which prevents routing loops between areas.
4. **Broadcast vs non-broadcast networks:**
   - **Broadcast** (Ethernet) discovers neighbours automatically by multicast hellos to
     224.0.0.5 and elects a DR/BDR.
   - **NBMA** (Frame Relay, X.25) can't multicast, so neighbours are configured by hand
     (`neighbor`), with longer timers (30/120 s) and still a DR/BDR.
   - **Point-to-point** (serial, as here) needs no DR.
5. **Hello and dead intervals:**
   - Hello (10 s on broadcast/P2P) is how often a router sends hellos to find and keep neighbours.
   - Dead (4 × hello = 40 s) is how long to wait without a hello before declaring the neighbour down.
   - Both must match on the two ends or no adjacency forms. They decide how fast a failure is noticed.
