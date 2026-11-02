# Program 6: Static routing

**Aim:** configure static routing on two routers so packets reach the other network over a
manually defined path.

This is the topology from the manual (page 27): two routers joined by a serial link
11.0.0.0/8, one LAN behind each.

## Files

| File | What it is |
|---|---|
| `P06_Static_Routing.pkt` | Fully configured; every PC pings every PC |
| `configs/P06_Static_Routing/Router0.txt`, `configs/P06_Static_Routing/Router1.txt` | Router commands |
| `P06_Static_Routing.results.md` | Addressing, cabling, routing tables, expected pings |

```
            Se0/0/0 11.0.0.1 (DCE)        Se0/0/0 11.0.0.2
  Router0 ====================================== Router1
     | Gig0/0 192.168.1.1                         | Gig0/0 192.168.2.1
  Switch0                                       Switch1
   /    \                                        /    \
 PC0     PC1                                   PC2     PC3
 .2      .3     192.168.1.0/24    192.168.2.0/24  .2      .3
```

## Procedure

1. Place 2 × **2911**, 2 × **2960**, 4 PCs.
2. Cables: Router0 Se0/0/0 ↔ Router1 Se0/0/0 with **Serial DCE**, clicking Router0 first so
   Router0 is the DCE end. Router Gig0/0 ↔ switch Gig0/1 and PCs ↔ switch Fa0/1–2 with
   **straight-through** cables.
3. PCs: IP / mask / gateway, e.g. PC0 = 192.168.1.2 / 255.255.255.0 / 192.168.1.1.
4. Router0:
```
enable
configure terminal
hostname Router0
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
 exit
interface Serial0/0/0
 ip address 11.0.0.1 255.0.0.0
 clock rate 64000                ! only on the DCE end
 no shutdown
 exit
ip route 192.168.2.0 255.255.255.0 11.0.0.2      ! "to reach 192.168.2.0/24, hand it to 11.0.0.2"
end
write memory
```
5. Router1: the same idea, with `ip address 11.0.0.2 255.0.0.0` on Se0/0/0 (no clock rate) and
   `ip route 192.168.1.0 255.255.255.0 11.0.0.1`.

The syntax is `ip route <destination network> <mask> <next-hop IP | exit interface> [admin distance]`.
Each router needs a route to every network it isn't directly connected to, in **both
directions**. Without the return route, the ping reaches the far end but the reply is lost.

## Verification

```
Router0# show ip route
Gateway of last resort is not set
C    11.0.0.0/8 is directly connected, Serial0/0/0
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
S    192.168.2.0/24 [1/0] via 11.0.0.2
Router0# show ip interface brief        ! Serial0/0/0 up/up
Router0# show controllers serial 0/0/0  ! "DCE V.35, clock rate 64000"
PC0> ping 192.168.2.2                   ! first one may time out (ARP), then replies
PC0> tracert 192.168.2.2                ! 192.168.1.1 -> 11.0.0.2 -> 192.168.2.2
```

## Troubleshooting checklist

| Symptom | Likely cause | Fix |
|---|---|---|
| Serial is up/down | no clock on the DCE end, or the other end is shut | `clock rate 64000` on DCE, `no shutdown` both ends |
| "Destination host unreachable" from 192.168.1.1 | Router0 has no route | add the `ip route` |
| Request timed out (no reply at all) | the return route is missing on Router1 | add the route back |
| PC can't ping its own gateway | wrong PC gateway/IP, or Gig0/0 shut | fix the IP, `no shutdown` |

## Viva answers

1. **Static vs dynamic routing:** static routes are typed in by the administrator and never
   change on their own. Dynamic protocols (RIP, OSPF, EIGRP) let routers exchange routes and
   adapt automatically when links change.
2. **Advantages:**
   - no CPU or bandwidth used for routing updates
   - secure (nothing advertised)
   - predictable path
   - fine for small or stub networks

   **Disadvantages:**
   - doesn't scale
   - error-prone
   - doesn't react to failures unless you configure floating routes
   - every change must be made by hand on every router
3. **Next-hop address:** the IP of the neighbouring router's interface (on a directly connected
   network) that should receive the packet next. Here Router0 sends 192.168.2.0/24 traffic to
   11.0.0.2.
4. **Verifying a static route:**
   - `show ip route`: look for an `S` entry with [1/0]
   - `show ip route static`
   - `ping` and `tracert` end to end
   - `show running-config | include ip route`
