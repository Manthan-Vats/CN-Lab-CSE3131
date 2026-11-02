### Simulated results for `P13a_Phase1_Small_Office.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC0 | 192.168.1.12 | reply | as expected |
| PC1 | 192.168.1.11 | reply | as expected |
| PC0 | 198.51.100.10 | reply | as expected |
| PC1 | 198.51.100.10 | reply | as expected |

DHCP leases the simulator expects (Packet Tracer may hand them out in a different order):

| PC | IP address | Gateway |
|---|---|---|
| PC0 | 192.168.1.11 | 192.168.1.1 |
| PC1 | 192.168.1.12 | 192.168.1.1 |

Expected routing tables:

```
R1# show ip route   (connected / static / OSPF / RIP part)
S    0.0.0.0/0 [1/0] via 203.0.113.2, Serial0/0/0
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
C    203.0.113.0/30 is directly connected, Serial0/0/0

ISP# show ip route   (connected / static / OSPF / RIP part)
C    198.51.100.0/24 is directly connected, GigabitEthernet0/0
C    203.0.113.0/30 is directly connected, Serial0/0/0

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| R1 | GigabitEthernet0/0 | 192.168.1.1 | 255.255.255.0 |  |
| R1 | Serial0/0/0 | 203.0.113.1 | 255.255.255.252 |  |
| ISP | Serial0/0/0 | 203.0.113.2 | 255.255.255.252 |  |
| ISP | GigabitEthernet0/0 | 198.51.100.1 | 255.255.255.0 |  |
| Internet-Server | FastEthernet0 | 198.51.100.10 | 255.255.255.0 | 198.51.100.1, DNS 198.51.100.10 |
| PC0 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |
| PC1 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| R1 | Serial0/0/0 | ISP | Serial0/0/0 | Serial DCE (DCE end: R1) |
| ISP | GigabitEthernet0/0 | Internet-Server | FastEthernet0 | Copper cross-over |
| R1 | GigabitEthernet0/0 | SW1 | GigabitEthernet0/1 | Copper straight-through |
| PC0 | FastEthernet0 | SW1 | FastEthernet0/1 | Copper straight-through |
| PC1 | FastEthernet0 | SW1 | FastEthernet0/2 | Copper straight-through |
