# Program 2: Basic network utility commands

**Aim:** use the basic network commands (`ipconfig`, `ping`, `tracert`, `pathping`, `nslookup`,
`arp`, `netstat`, `hostname`) to check and troubleshoot a network, on a real Windows PC and
inside Packet Tracer.

## Files

| File | What it is |
|---|---|
| `P02_Commands_Practice.pkt` | A small network for practising the commands: 2 LANs, a router, and a DNS server (`www.cnlab.local`) |
| `configs/P02_Commands_Practice/` | Router commands |
| `P02_Commands_Practice.results.md` | Addressing, cabling, expected pings |

## Commands

| Command | What it does | Useful options |
|---|---|---|
| `ipconfig` | Shows the IP address, subnet mask and default gateway of each adapter | `/all` (MAC, DHCP, DNS servers, lease), `/release`, `/renew`, `/flushdns`, `/displaydns` |
| `ping <host>` | Sends ICMP echo requests and measures replies (reachability, round-trip time, loss) | `-n 10` (count), `-t` (until Ctrl+C), `-l 1000` (size), `-a` (resolve name) |
| `tracert <host>` | Lists every router on the path, using rising TTL values | `-d` (no names, faster), `-h 15` (max hops) |
| `pathping <host>` | tracert plus per-hop packet loss statistics | `-q 25` (queries per hop), `-n` |
| `nslookup <name>` | Asks a DNS server for a name's address | `nslookup <name> 8.8.8.8` (pick a server), `set type=mx` |
| `arp -a` | Shows the ARP cache (IP → MAC) | `-d` (delete entries, admin) |
| `netstat` | Shows connections, listening ports and statistics | `-an` (all, numeric), `-b` (program, admin), `-e` (Ethernet stats), `-r` (route table), `-s` (per protocol) |
| `hostname` | Prints the computer's name | |
| `getmac` | Lists MAC addresses | `/v` |
| `route print` | Same as `netstat -r` | |

## Real outputs (taken on a Windows 11 laptop, private details masked with `x`)

**ipconfig**
```
Wireless LAN adapter Wi-Fi:
   Link-local IPv6 Address . . . . . : fe80::xxxx:xxxx:xxxx:xxxx%8
   IPv4 Address. . . . . . . . . . . : 10.176.x.x
   Subnet Mask . . . . . . . . . . . : 255.255.0.0
   Default Gateway . . . . . . . . . : 10.176.0.1
```
The adapter has a private class-A address with a /16 mask, so the gateway 10.176.0.1 is on the same subnet.

**ping -n 4 8.8.8.8**
```
Reply from 8.8.8.8: bytes=32 time=63ms TTL=116
Reply from 8.8.8.8: bytes=32 time=18ms TTL=116
Reply from 8.8.8.8: bytes=32 time=18ms TTL=116
Reply from 8.8.8.8: bytes=32 time=22ms TTL=116
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
    Minimum = 18ms, Maximum = 63ms, Average = 30ms
```
TTL=116 means the reply started at 128 and crossed 12 routers. The first reply is slower
because ARP and route lookups happen first.

**nslookup google.com**
```
Non-authoritative answer:
Server:  family.cloudflare-dns.com
Address:  1.1.1.3
Name:    google.com
Addresses:  2404:6800:4002:817::200e
          192.178.158.139
          192.178.158.138  ... (6 IPv4 addresses)
```
*Non-authoritative* means the answer came from the resolver's cache, not from Google's own
DNS servers. The several addresses are used for load balancing.

**tracert -h 15 google.com**
```
Tracing route to google.com [192.178.158.101]
  1     2 ms     2 ms     2 ms  10.176.0.1           (local gateway)
  2-6   2-24 ms                 x.x.x.x              (ISP routers, hidden)
  7     *       19 ms     *     72.14.243.2          (Google's network edge)
  ...
```
`*` means that hop didn't answer in time (often rate-limited ICMP), not that the path is broken.

**arp -a**
```
Interface: 10.176.x.x --- 0x8
  Internet Address      Physical Address      Type
  10.176.0.1            xx-xx-xx-xx-xx-xx     dynamic
  10.176.x.x            xx-xx-xx-xx-xx-xx     dynamic
  ...
  224.0.0.22            01-00-5e-00-00-16     static
  255.255.255.255       ff-ff-ff-ff-ff-ff     static
```
*Dynamic* entries were learned by ARP and expire. *Static* entries are the multicast and broadcast MACs.

**netstat -an** (a few lines)
```
  Proto  Local Address          Foreign Address        State
  TCP    0.0.0.0:3306           0.0.0.0:0              LISTENING    (MySQL server)
  TCP    0.0.0.0:5433           0.0.0.0:0              LISTENING    (PostgreSQL)
  TCP    0.0.0.0:49666          0.0.0.0:0              LISTENING    (Windows RPC dynamic port)
  TCP    10.176.x.x:7680        10.176.x.x:5xxxx       ESTABLISHED  (Windows Update delivery optimisation)
```
`0.0.0.0:port LISTENING` means a service is waiting on every interface. `ESTABLISHED` is a live connection.

**netstat -e**
```
                           Received            Sent
Bytes                    2489160102      1376624310
Unicast packets            46520814        41349366
Non-unicast packets       175758906          876564
Discards                          0               0
Errors                            0               0
```

**netstat -r** (IPv4 route table)
```
Network Destination        Netmask          Gateway       Interface  Metric
          0.0.0.0          0.0.0.0       10.176.0.1    10.176.x.x      35   <- default route
       10.176.0.0      255.255.0.0         On-link     10.176.x.x     291   <- local subnet
        127.0.0.0        255.0.0.0         On-link      127.0.0.1     331   <- loopback
        224.0.0.0        240.0.0.0         On-link     10.176.x.x     291   <- multicast
```

## Practice in Packet Tracer (`P02_Commands_Practice.pkt`)

Click a PC, open **Desktop > Command Prompt**, and try:
```
ipconfig /all              ! IP, mask, gateway, DNS server 192.168.2.100, MAC
ping 192.168.2.100         ! DNS server on the other LAN, through the router
nslookup www.cnlab.local   ! answered by DNS-Server
ping www.cnlab.local       ! name resolved first, then pinged
tracert 192.168.2.100      ! hop 1 = the gateway, hop 2 = the server
arp -a                     ! after the pings: the gateway's MAC
```
Also open **Web Browser** and go to `www.cnlab.local`. On the router, try `show ip interface brief`,
`show arp` and `ping`.

## Viva answers

1. **ping vs tracert:** ping checks that a host is reachable and measures RTT and loss.
   tracert shows *where* the path goes: it sends packets with TTL 1, 2, 3… and each router that
   drops a packet at TTL 0 sends back an ICMP Time Exceeded, which reveals its address.
2. **What ipconfig /all adds:** the MAC (physical address), DHCP enabled/server, lease
   times, DNS servers, host name, adapter description and IPv6 details.
3. **What nslookup is for:** checking DNS. It shows which DNS server answered and the
   addresses for a name, so you can tell a DNS problem ("ping 8.8.8.8 works but ping
   google.com fails") from a connectivity problem.
4. **What netstat shows:** active TCP connections and their states (LISTENING,
   ESTABLISHED, TIME_WAIT), listening ports, the routing table (`-r`), and interface and
   protocol statistics (`-e`, `-s`). It's used to find which services are open and to spot
   unknown connections.

**Troubleshooting order:**
1. `ipconfig`: do you have an address?
2. `ping 127.0.0.1`: is TCP/IP working?
3. `ping` the gateway.
4. `ping 8.8.8.8`: can you reach the Internet?
5. `nslookup`: does DNS work?
6. `tracert`: where does the path stop?
