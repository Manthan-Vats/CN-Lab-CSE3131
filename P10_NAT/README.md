# Program 10: NAT configuration and troubleshooting

**Aim:** implement Network Address Translation, understand how it works, and troubleshoot it.

## Files

| File | NAT type |
|---|---|
| `P10a_Static_NAT.pkt` | Static NAT: fixed 1:1 mappings |
| `P10b_Dynamic_NAT.pkt` | Dynamic NAT: a pool of public addresses |
| `P10c_PAT_Overload.pkt` | PAT (NAT overload): everyone shares R1's one public IP, plus a static mapping for the web server |
| `configs/<file>/<device>.txt` | Commands |
| `<file>.results.md` | Addressing, cabling, expected pings |

## Topology (the same in all three)

```
   INSIDE (private)                                   OUTSIDE ("Internet")
 PC0 192.168.1.10 \                Se0/0/0            Se0/0/0
 PC1 192.168.1.11  > Switch0 - Gig0/0  R1 ==203.0.113.0/30== ISP - Gig0/0 - Internet-Server
 PC2 192.168.1.12 /   192.168.1.1  (inside) (outside)          198.51.100.1    198.51.100.10
 Web-Server 192.168.1.100
```
The ISP router has **no route to 192.168.x.x** (private addresses aren't routed on the
Internet). It only knows `203.0.113.0/24 → R1`. So a reply gets back only if R1 translated the
source to a 203.0.113.x address. That's how you can tell NAT is working.

Common to all three on R1:
```
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 ip nat inside
interface Serial0/0/0
 ip address 203.0.113.1 255.255.255.252
 ip nat outside
ip route 0.0.0.0 0.0.0.0 203.0.113.2          ! default route to the ISP
```

### P10a: static NAT
```
ip nat inside source static 192.168.1.100 203.0.113.10   ! Web-Server
ip nat inside source static 192.168.1.10  203.0.113.11   ! PC0
ip nat inside source static 192.168.1.11  203.0.113.12   ! PC1
```
PC0, PC1 and the Web-Server reach 198.51.100.10. **PC2 has no mapping, so it can't** (on
purpose). The Internet server can ping 203.0.113.10 to reach the inside web server. Static
NAT works in both directions.

### P10b: dynamic NAT
```
access-list 1 permit 192.168.1.0 0.0.0.255                       ! who may be translated
ip nat pool PUBLIC_POOL 203.0.113.20 203.0.113.30 netmask 255.255.255.0
ip nat inside source list 1 pool PUBLIC_POOL
```
Each inside host that sends traffic gets the next free pool address. When the pool runs
out, further hosts fail until entries time out. The outside can't start a connection inward.

### P10c: PAT / overload
```
access-list 1 permit 192.168.1.0 0.0.0.255
ip nat inside source list 1 interface Serial0/0/0 overload
ip nat inside source static 192.168.1.100 203.0.113.10          ! publish the web server
```
All PCs share 203.0.113.1 and are told apart by **port numbers** (for ping, by ICMP ID).

## Verification (ping 198.51.100.10 from a PC first)

```
R1# show ip nat translations
Pro  Inside global      Inside local       Outside local      Outside global
icmp 203.0.113.1:1      192.168.1.10:1     198.51.100.10:1    198.51.100.10:1    (PAT)
---  203.0.113.10       192.168.1.100      ---                ---                (static)
R1# show ip nat statistics      ! inside/outside interfaces, hits, misses, pool usage
R1# clear ip nat translation *  ! clear dynamic entries
R1# debug ip nat                ! shows each translation (undebug all to stop)
```
In Simulation mode, click the ICMP packet before and after R1 and compare the source IP in
the IP header.

**NAT terms:**
- *Inside local*: the private address of the inside host.
- *Inside global*: the public address it's translated to.
- *Outside local / outside global*: the outside host's address as seen from inside / outside (the same here).

## Troubleshooting

| Symptom | Cause |
|---|---|
| No translations appear | `ip nat inside` or `ip nat outside` missing or on the wrong interface |
| PCs not translated | ACL doesn't match their subnet (wrong wildcard) |
| "Destination host unreachable" from R1 | no default route to the ISP |
| Dynamic NAT works for the first hosts only | pool exhausted; use a bigger pool or `overload` |
| Outside can't reach the server | needs a static mapping (dynamic/PAT entries are created only from inside) |

## Viva answers

1. **Purpose of NAT:** lets many private (RFC 1918) addresses share a few public IPv4
   addresses. This saves IPv4 space, hides the internal addressing, and lets you change
   ISP without renumbering.
2. **Static vs dynamic NAT:** static is a permanent one-to-one private↔public mapping that
   works in both directions (for servers). Dynamic maps inside hosts to the next free address
   from a pool, temporarily, one-to-one while in use, and only for traffic started from inside.
3. **PAT:** many inside hosts share **one** public IP. The router rewrites the source port
   (or ICMP ID) to a unique number and keeps a table of (inside IP:port ↔ public IP:port).
   It's useful because a whole LAN needs only one public address. This is what home routers do.
4. **NAT pros and cons:**

   | Advantages | Disadvantages |
   |---|---|
   | Saves public IPv4 addresses | Breaks true end-to-end connectivity |
   | Hides internal addresses | Some protocols break (IPsec AH, SIP, FTP active) without helpers |
   | Flexible renumbering | Adds router CPU work and a little delay |
   | | Makes tracing and troubleshooting harder |
   | | Inbound connections need static maps or port forwarding |

5. **Configuration steps:**
   - Mark interfaces `ip nat inside` / `ip nat outside`.
   - Define who gets translated (`access-list`).
   - Choose the type: `static`, a `pool` + `list`, or `list ... interface ... overload`.
   - Add a default route to the ISP.
   - Verify with `show ip nat translations` / `statistics`.
