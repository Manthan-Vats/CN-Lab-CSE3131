### Simulated results for `P01_Device_Tour.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC0 | 192.168.1.11 | reply | as expected |
| PC0 | 192.168.1.20 | reply | as expected |
| PC0 | 192.168.1.21 | reply | as expected |
| PC0 | 192.168.1.100 | reply | as expected |
| PC0 | 192.168.2.10 | reply | as expected |
| PC1 | 192.168.1.10 | reply | as expected |
| PC1 | 192.168.1.20 | reply | as expected |
| PC1 | 192.168.1.21 | reply | as expected |
| PC1 | 192.168.1.100 | reply | as expected |
| PC1 | 192.168.2.10 | reply | as expected |
| PC2 | 192.168.1.10 | reply | as expected |
| PC2 | 192.168.1.11 | reply | as expected |
| PC2 | 192.168.1.21 | reply | as expected |
| PC2 | 192.168.1.100 | reply | as expected |
| PC2 | 192.168.2.10 | reply | as expected |
| PC3 | 192.168.1.10 | reply | as expected |
| PC3 | 192.168.1.11 | reply | as expected |
| PC3 | 192.168.1.20 | reply | as expected |
| PC3 | 192.168.1.100 | reply | as expected |
| PC3 | 192.168.2.10 | reply | as expected |
| Server0 | 192.168.1.10 | reply | as expected |
| Server0 | 192.168.1.11 | reply | as expected |
| Server0 | 192.168.1.20 | reply | as expected |
| Server0 | 192.168.1.21 | reply | as expected |
| Server0 | 192.168.2.10 | reply | as expected |
| PC4 | 192.168.1.10 | reply | as expected |
| PC4 | 192.168.1.11 | reply | as expected |
| PC4 | 192.168.1.20 | reply | as expected |
| PC4 | 192.168.1.21 | reply | as expected |
| PC4 | 192.168.1.100 | reply | as expected |

Expected routing tables:

```
R1# show ip route   (connected / static / OSPF / RIP part)
C    10.0.0.0/30 is directly connected, Serial0/0/0
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
S    192.168.2.0/24 [1/0] via 10.0.0.2, Serial0/0/0

R2# show ip route   (connected / static / OSPF / RIP part)
C    10.0.0.0/30 is directly connected, Serial0/0/0
S    192.168.1.0/24 [1/0] via 10.0.0.1, Serial0/0/0
C    192.168.2.0/24 is directly connected, GigabitEthernet0/0

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| R1 | GigabitEthernet0/0 | 192.168.1.1 | 255.255.255.0 | LAN-A |
| R1 | Serial0/0/0 | 10.0.0.1 | 255.255.255.252 | WAN to R2 |
| R2 | GigabitEthernet0/0 | 192.168.2.1 | 255.255.255.0 | LAN-B |
| R2 | Serial0/0/0 | 10.0.0.2 | 255.255.255.252 | WAN to R1 |
| PC0 | FastEthernet0 | 192.168.1.10 | 255.255.255.0 | 192.168.1.1 |
| PC1 | FastEthernet0 | 192.168.1.11 | 255.255.255.0 | 192.168.1.1 |
| PC2 | FastEthernet0 | 192.168.1.20 | 255.255.255.0 | 192.168.1.1 |
| PC3 | FastEthernet0 | 192.168.1.21 | 255.255.255.0 | 192.168.1.1 |
| Server0 | FastEthernet0 | 192.168.1.100 | 255.255.255.0 | 192.168.1.1, DNS 192.168.1.100 |
| PC4 | FastEthernet0 | 192.168.2.10 | 255.255.255.0 | 192.168.2.1 |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| PC0 | FastEthernet0 | SW1 | FastEthernet0/1 | Copper straight-through |
| PC1 | FastEthernet0 | SW1 | FastEthernet0/2 | Copper straight-through |
| PC2 | FastEthernet0 | HUB1 | FastEthernet1 | Copper straight-through |
| PC3 | FastEthernet0 | HUB1 | FastEthernet2 | Copper straight-through |
| R1 | GigabitEthernet0/0 | SW1 | GigabitEthernet0/1 | Copper straight-through |
| Server0 | FastEthernet0 | SW1 | FastEthernet0/10 | Copper straight-through |
| HUB1 | FastEthernet0 | SW1 | FastEthernet0/24 | Copper cross-over |
| R1 | Serial0/0/0 | R2 | Serial0/0/0 | Serial DCE (DCE end: R1) |
| R2 | GigabitEthernet0/0 | PC4 | FastEthernet0 | Copper cross-over |
