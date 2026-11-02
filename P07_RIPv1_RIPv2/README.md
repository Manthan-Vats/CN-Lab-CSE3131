# Program 7: RIPv1 and RIPv2

**Aim:** configure the Routing Information Protocol on a set of routers for dynamic routing
between networks.

This is the manual's figure *"RIP routing with multiple paths"* (page 29): four 2911 routers in
a ring, three PCs, every link its own network.

## Files

| File | What it is |
|---|---|
| `P07a_RIPv1.pkt` | RIP version 1 on all routers |
| `P07b_RIPv2.pkt` | RIP version 2, `no auto-summary` |
| `configs/P07a_RIPv1/`, `configs/P07b_RIPv2/` | Router commands for each version |
| `P07a_RIPv1.results.md`, `P07b_RIPv2.results.md` | Addressing, cabling, routing tables, expected pings |

```
                        PC2 8.0.0.2
                          | 8.0.0.0/8
   PC1 --- Router2 ---------------- Router3
 60.0.0.2  60.0.0.1  50.0.0.0/8    |
              |                    | 20.0.0.0/8
   40.0.0.0/8 |                    |
              |                    |
           Router1 ---------------- Router0 --- PC0
                     30.0.0.0/8         192.168.1.1   192.168.1.2
```

| Router | Gig0/0 | Gig0/1 | Gig0/2 |
|---|---|---|---|
| Router0 | 192.168.1.1 → PC0 | 20.0.0.1/8 → Router3 | 30.0.0.1/8 → Router1 |
| Router1 | 30.0.0.2/8 → Router0 | 40.0.0.1/8 → Router2 | – |
| Router2 | 40.0.0.2/8 → Router1 | 50.0.0.1/8 → Router3 | 60.0.0.1/8 → PC1 |
| Router3 | 50.0.0.2/8 → Router2 | 20.0.0.2/8 → Router0 | 8.0.0.1/8 → PC2 |

Router↔router and router↔PC links are Ethernet with **cross-over** cables.

**One difference between the two files.** The manual's figure puts PC0 on 192.168.1.0/**16**.
That works in the **v2** file (classless, sends the mask). In the **v1** file, PC0's LAN is
192.168.1.0/**24**, because RIPv1 is classful: it never sends masks, so it can't advertise a
/16 inside a Class C address. Every other router would ignore it and PC0 would be unreachable.
`tools/selftest.py` demonstrates exactly this failure, and it's a good viva point.

## Commands

RIPv1, Router0 (the others are the same pattern with their own networks):
```
router rip
 network 192.168.1.0
 network 20.0.0.0
 network 30.0.0.0
```
RIPv2, Router0:
```
router rip
 version 2
 network 192.168.1.0
 network 20.0.0.0
 network 30.0.0.0
 no auto-summary
```
`network` takes the **classful** network of each directly connected interface you want RIP to
run on and advertise. There's no mask; IOS converts it to the class boundary.

To change a router from v1 to v2 later: `router rip` → `version 2` → `no auto-summary`.

## Verification

```
Router0# show ip route
R    8.0.0.0/8 [120/1] via 20.0.0.2, GigabitEthernet0/1
C    20.0.0.0/8 is directly connected, GigabitEthernet0/1
C    30.0.0.0/8 is directly connected, GigabitEthernet0/2
R    40.0.0.0/8 [120/1] via 30.0.0.2, GigabitEthernet0/2
R    50.0.0.0/8 [120/1] via 20.0.0.2, GigabitEthernet0/1
R    60.0.0.0/8 [120/2] via 30.0.0.2, ...  [120/2] via 20.0.0.2   (equal-cost paths)
Router0# show ip protocols          ! version sent/received, networks, timers 30/180/180/240
Router0# show ip rip database
Router0# debug ip rip               ! watch updates every 30 s; "undebug all" to stop
PC0> tracert 60.0.0.2               ! 3 hops through the ring
```
`[120/2]` means administrative distance 120 (RIP) and metric 2 (hop count). In Packet
Tracer, RIP takes up to ~30 s after opening the file to learn every route. Use Fast Forward
Time if the first pings fail.

## Viva answers

1. **Maximum hop count:** 15. A metric of 16 means unreachable, so RIP suits small networks only.
2. **RIPv1 vs RIPv2:**

   | RIPv1 | RIPv2 |
   |---|---|
   | Classful: no subnet mask in updates | Classless: mask in every update (VLSM/CIDR) |
   | Updates by broadcast 255.255.255.255 | Updates by multicast 224.0.0.9 |
   | No authentication | MD5/plain-text authentication |
   | Always auto-summarises at class boundaries | Auto-summary can be turned off |
   | No next-hop or route-tag fields | Next-hop and route-tag fields |

3. **Why RIPv1 is classful:** its update format has no subnet-mask field. The receiver has to
   guess the mask from the address class (A /8, B /16, C /24) or from its own interface in the
   same major network.
4. **Limitations of RIPv1 today:**
   - no VLSM/CIDR, so it can't route discontiguous subnets correctly
   - broadcasts disturb every host
   - no authentication, so it's easy to inject routes
   - slow convergence (30 s updates, hold-down)
   - 15-hop limit
   - counting-to-infinity loops, only partly fixed by split horizon and poison reverse
