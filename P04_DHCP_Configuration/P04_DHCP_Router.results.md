### Simulated results for `P04_DHCP_Router.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC0 | 192.168.1.1 | reply | as expected |
| PC1 | 192.168.1.1 | reply | as expected |
| PC2 | 192.168.1.1 | reply | as expected |
| PC3 | 192.168.1.1 | reply | as expected |
| PC0 | 192.168.1.12 | reply | as expected |
| PC0 | 192.168.1.13 | reply | as expected |
| PC0 | 192.168.1.14 | reply | as expected |

DHCP leases the simulator expects (Packet Tracer may hand them out in a different order):

| PC | IP address | Gateway |
|---|---|---|
| PC0 | 192.168.1.11 | 192.168.1.1 |
| PC1 | 192.168.1.12 | 192.168.1.1 |
| PC2 | 192.168.1.13 | 192.168.1.1 |
| PC3 | 192.168.1.14 | 192.168.1.1 |

Expected routing tables:

```
Router0# show ip route   (connected / static / OSPF / RIP part)
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| Router0 | GigabitEthernet0/0 | 192.168.1.1 | 255.255.255.0 | LAN |
| PC0 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |
| PC1 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |
| PC2 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |
| PC3 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| Router0 | GigabitEthernet0/0 | Switch0 | GigabitEthernet0/1 | Copper straight-through |
| PC0 | FastEthernet0 | Switch0 | FastEthernet0/1 | Copper straight-through |
| PC1 | FastEthernet0 | Switch0 | FastEthernet0/2 | Copper straight-through |
| PC2 | FastEthernet0 | Switch0 | FastEthernet0/3 | Copper straight-through |
| PC3 | FastEthernet0 | Switch0 | FastEthernet0/4 | Copper straight-through |
