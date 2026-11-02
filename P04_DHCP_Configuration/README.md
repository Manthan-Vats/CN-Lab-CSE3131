# Program 4: DHCP configuration on a router

**Aim:** configure a router as a DHCP server so PCs get their IP address, mask, gateway and DNS
automatically, and verify the leases.

## Files

| File | What it is |
|---|---|
| `P04_DHCP_Router.pkt` | Router0 as DHCP server, Switch0, 4 PCs set to DHCP |
| `configs/P04_DHCP_Router/Router0.txt` | Router commands |
| `P04_DHCP_Router.results.md` | Addressing, cabling, expected leases and pings |

## Topology

```
              Router0  Gig0/0 192.168.1.1   (DHCP server, pool MY_POOL)
                 |
              Switch0
          /    |     |    \
       PC0    PC1   PC2   PC3      all on DHCP -> 192.168.1.11, .12, .13, .14
```

## Procedure

1. Place a **2911** router, a **2960** switch and 4 PCs. Connect Router0 Gig0/0 → Switch0 Gig0/1, and
   PCs → Fa0/1–Fa0/4, all with straight-through cables.
2. Router0 > CLI, then paste `configs/P04_DHCP_Router/Router0.txt`:

```
enable
configure terminal
hostname Router0
ip dhcp excluded-address 192.168.1.1 192.168.1.10   ! keep .1-.10 for router/servers/printers
ip dhcp pool MY_POOL
 network 192.168.1.0 255.255.255.0                   ! which addresses to lease
 default-router 192.168.1.1                          ! gateway handed to clients
 dns-server 8.8.8.8                                  ! DNS handed to clients
 exit
interface GigabitEthernet0/0
 description LAN
 ip address 192.168.1.1 255.255.255.0
 no shutdown
 exit
end
write memory
```

3. On each PC: **Desktop > IP Configuration > DHCP**. You'll see "DHCP request successful" and
   an address from .11 upwards. (In the .pkt the PCs are already set to DHCP; they ask for an
   address when the file opens. If one shows 169.254.x.x, click Static and then DHCP again.)

## Verification

```
Router0# show ip dhcp binding
IP address       Client-ID/              Lease expiration        Type
                 Hardware address
192.168.1.11     00E0.xxxx.xxxx           --                     Automatic
192.168.1.12     0001.xxxx.xxxx           --                     Automatic
...
Router0# show ip dhcp pool
Pool MY_POOL :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0
 Total addresses                : 254
 Leased addresses               : 4
 ...
Router0# show ip dhcp conflict      ! should be empty
PC0> ipconfig /all                  ! shows DHCP Enabled, IP, gateway 192.168.1.1, DNS 8.8.8.8
PC0> ping 192.168.1.1
```

The order of the leases (.11 to PC0 or PC2) depends on which PC asks first, so it doesn't matter.

## DORA (what to say in the viva)

| Step | Message | Sent from → to | How |
|---|---|---|---|
| D | DHCP **Discover** | client → everyone | broadcast, src 0.0.0.0, dst 255.255.255.255, UDP 68→67 |
| O | DHCP **Offer** | server → client | "you can have 192.168.1.11, mask, gw, DNS, lease" |
| R | DHCP **Request** | client → everyone | broadcast: "I take the offer from server X" (tells other servers no) |
| A | DHCP **Ack** | server → client | confirms; the client now configures the address |

Watch it in **Simulation** mode with the DHCP filter. On PC0, click DHCP in IP Configuration
and step through the four packets.

## Viva answers

1. **Role of a DHCP server:** it gives out IP addresses (plus mask, gateway, DNS, lease time)
   automatically from a pool. This avoids manual setup and duplicate-IP mistakes, and lets
   addresses be reused when leases expire.
2. **Discover and Offer:** the client has no IP, so it broadcasts a DISCOVER to find any DHCP
   server. Each server that has a free address replies with an OFFER containing the proposed
   IP and options (by broadcast or unicast to the client's MAC).
3. **`default-router`:** sets the default gateway the clients receive. Without it, PCs can talk
   only inside their own subnet and can't reach other networks.
4. **`ip dhcp excluded-address`:** stops the server from leasing addresses that are already
   used statically (router interface, servers, printers), which prevents IP conflicts.
