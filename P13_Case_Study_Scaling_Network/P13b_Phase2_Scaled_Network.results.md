### Simulated results for `P13b_Phase2_Scaled_Network.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| Sales-PC1 | 192.168.99.10 | reply | as expected |
| HR-PC1 | 192.168.99.10 | reply | as expected |
| Sales-PC1 | 192.168.20.11 | reply | as expected |
| HR-PC3 | 192.168.10.11 | reply | as expected |
| Sales-PC2 | 198.51.100.10 | reply | as expected |
| HR-PC2 | 198.51.100.10 | reply | as expected |
| File-Server | 198.51.100.10 | reply | as expected |
| Internet-Server | 192.168.99.10 | no reply | as expected |

DHCP leases the simulator expects (Packet Tracer may hand them out in a different order):

| PC | IP address | Gateway |
|---|---|---|
| Sales-PC1 | 192.168.10.11 | 192.168.10.1 |
| Sales-PC2 | 192.168.10.12 | 192.168.10.1 |
| Sales-PC3 | 192.168.10.13 | 192.168.10.1 |
| HR-PC1 | 192.168.20.11 | 192.168.20.1 |
| HR-PC2 | 192.168.20.12 | 192.168.20.1 |
| HR-PC3 | 192.168.20.13 | 192.168.20.1 |

Expected routing tables:

```
R1# show ip route   (connected / static / OSPF / RIP part)
S    0.0.0.0/0 [1/0] via 203.0.113.2, Serial0/0/0
C    10.0.12.0/30 is directly connected, GigabitEthernet0/1
C    192.168.10.0/24 is directly connected, GigabitEthernet0/0.10
C    192.168.20.0/24 is directly connected, GigabitEthernet0/0.20
C    192.168.99.0/24 is directly connected, GigabitEthernet0/0.99
C    203.0.113.0/30 is directly connected, Serial0/0/0

R2# show ip route   (connected / static / OSPF / RIP part)
S    0.0.0.0/0 [1/0] via 203.0.113.6, Serial0/0/0
C    10.0.12.0/30 is directly connected, GigabitEthernet0/0
O    192.168.10.0/24 [110/2] via 10.0.12.1, GigabitEthernet0/0
O    192.168.20.0/24 [110/2] via 10.0.12.1, GigabitEthernet0/0
O    192.168.99.0/24 [110/2] via 10.0.12.1, GigabitEthernet0/0
C    203.0.113.4/30 is directly connected, Serial0/0/0
S    203.0.113.64/29 [1/0] via 10.0.12.1, GigabitEthernet0/0

ISP# show ip route   (connected / static / OSPF / RIP part)
C    198.51.100.0/24 is directly connected, GigabitEthernet0/0
C    203.0.113.0/30 is directly connected, Serial0/0/0
C    203.0.113.4/30 is directly connected, Serial0/0/1
S    203.0.113.64/29 [1/0] via 203.0.113.1, Serial0/0/0

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| R1 | GigabitEthernet0/0.10 | 192.168.10.1 | 255.255.255.0 | VLAN 10 sub-interface |
| R1 | GigabitEthernet0/0.20 | 192.168.20.1 | 255.255.255.0 | VLAN 20 sub-interface |
| R1 | GigabitEthernet0/0.99 | 192.168.99.1 | 255.255.255.0 | VLAN 99 sub-interface |
| R1 | GigabitEthernet0/1 | 10.0.12.1 | 255.255.255.252 | to backup router R2 |
| R1 | Serial0/0/0 | 203.0.113.1 | 255.255.255.252 | primary ISP link |
| R2 | GigabitEthernet0/0 | 10.0.12.2 | 255.255.255.252 | to R1 |
| R2 | Serial0/0/0 | 203.0.113.5 | 255.255.255.252 | backup ISP link |
| ISP | Serial0/0/0 | 203.0.113.2 | 255.255.255.252 |  |
| ISP | Serial0/0/1 | 203.0.113.6 | 255.255.255.252 |  |
| ISP | GigabitEthernet0/0 | 198.51.100.1 | 255.255.255.0 |  |
| Internet-Server | FastEthernet0 | 198.51.100.10 | 255.255.255.0 | 198.51.100.1 |
| File-Server | FastEthernet0 | 192.168.99.10 | 255.255.255.0 | 192.168.99.1, DNS 192.168.99.10 |
| Sales-PC1 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |
| Sales-PC2 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |
| Sales-PC3 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |
| HR-PC1 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |
| HR-PC2 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |
| HR-PC3 | FastEthernet0 | DHCP | (from DHCP) | (from DHCP) |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| R1 | Serial0/0/0 | ISP | Serial0/0/0 | Serial DCE (DCE end: R1) |
| R2 | Serial0/0/0 | ISP | Serial0/0/1 | Serial DCE (DCE end: R2) |
| R1 | GigabitEthernet0/1 | R2 | GigabitEthernet0/0 | Copper cross-over |
| ISP | GigabitEthernet0/0 | Internet-Server | FastEthernet0 | Copper cross-over |
| R1 | GigabitEthernet0/0 | SW-Core | GigabitEthernet0/1 | Copper straight-through |
| SW-Core | FastEthernet0/1 | SW-Sales | FastEthernet0/24 | Copper cross-over |
| SW-Core | FastEthernet0/2 | SW-HR | FastEthernet0/24 | Copper cross-over |
| File-Server | FastEthernet0 | SW-Core | FastEthernet0/10 | Copper straight-through |
| Sales-PC1 | FastEthernet0 | SW-Sales | FastEthernet0/1 | Copper straight-through |
| Sales-PC2 | FastEthernet0 | SW-Sales | FastEthernet0/2 | Copper straight-through |
| Sales-PC3 | FastEthernet0 | SW-Sales | FastEthernet0/3 | Copper straight-through |
| HR-PC1 | FastEthernet0 | SW-HR | FastEthernet0/1 | Copper straight-through |
| HR-PC2 | FastEthernet0 | SW-HR | FastEthernet0/2 | Copper straight-through |
| HR-PC3 | FastEthernet0 | SW-HR | FastEthernet0/3 | Copper straight-through |
