### Simulated results for `P08c_OSPF_Troubleshooting_BROKEN.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC0 | 192.168.2.12 | no reply | as expected |
| PC5 | 192.168.3.14 | reply | as expected |
| PC5 | 192.168.1.10 | no reply | as expected |
| PC0 | 192.168.1.11 | reply | as expected |

Expected routing tables:

```
R0# show ip route   (connected / static / OSPF / RIP part)
C    10.0.0.0/8 is directly connected, Serial0/0/0
O    11.0.0.0/8 [110/128] via 10.0.0.2, Serial0/0/0
C    12.0.0.0/8 is directly connected, Serial0/0/1
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
O    192.168.3.0/24 [110/129] via 10.0.0.2, Serial0/0/0

R1# show ip route   (connected / static / OSPF / RIP part)
C    10.0.0.0/8 is directly connected, Serial0/0/0
C    11.0.0.0/8 is directly connected, Serial0/0/1
O    12.0.0.0/8 [110/128] via 10.0.0.1, Serial0/0/0
O    192.168.1.0/24 [110/65] via 10.0.0.1, Serial0/0/0
C    192.168.2.0/24 is directly connected, GigabitEthernet0/0
O    192.168.3.0/24 [110/65] via 11.0.0.2, Serial0/0/1

R2# show ip route   (connected / static / OSPF / RIP part)
O    10.0.0.0/8 [110/128] via 11.0.0.1, Serial0/0/0
C    11.0.0.0/8 is directly connected, Serial0/0/0
C    12.0.0.0/8 is directly connected, Serial0/0/1
O    192.168.1.0/24 [110/129] via 11.0.0.1, Serial0/0/0
C    192.168.3.0/24 is directly connected, GigabitEthernet0/0

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| R0 | GigabitEthernet0/0 | 192.168.1.1 | 255.255.255.0 |  |
| R0 | Serial0/0/0 | 10.0.0.1 | 255.0.0.0 |  |
| R0 | Serial0/0/1 | 12.0.0.1 | 255.0.0.0 |  |
| R1 | GigabitEthernet0/0 | 192.168.2.1 | 255.255.255.0 |  |
| R1 | Serial0/0/0 | 10.0.0.2 | 255.0.0.0 |  |
| R1 | Serial0/0/1 | 11.0.0.1 | 255.0.0.0 |  |
| R2 | GigabitEthernet0/0 | 192.168.3.1 | 255.255.255.0 |  |
| R2 | Serial0/0/0 | 11.0.0.2 | 255.0.0.0 |  |
| R2 | Serial0/0/1 | 12.0.0.2 | 255.0.0.0 |  |
| PC0 | FastEthernet0 | 192.168.1.10 | 255.255.255.0 | 192.168.1.1 |
| PC1 | FastEthernet0 | 192.168.1.11 | 255.255.255.0 | 192.168.1.1 |
| PC2 | FastEthernet0 | 192.168.2.12 | 255.255.255.0 | 192.168.2.1 |
| PC3 | FastEthernet0 | 192.168.2.13 | 255.255.255.0 | 192.168.2.1 |
| PC4 | FastEthernet0 | 192.168.3.14 | 255.255.255.0 | 192.168.3.1 |
| PC5 | FastEthernet0 | 192.168.3.15 | 255.255.255.0 | 192.168.3.100 |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| R0 | Serial0/0/0 | R1 | Serial0/0/0 | Serial DCE (DCE end: R0) |
| R1 | Serial0/0/1 | R2 | Serial0/0/0 | Serial DCE (DCE end: R1) |
| R0 | Serial0/0/1 | R2 | Serial0/0/1 | Serial DCE (DCE end: R0) |
| R0 | GigabitEthernet0/0 | S0 | FastEthernet0/24 | Copper straight-through |
| PC0 | FastEthernet0 | S0 | FastEthernet0/1 | Copper straight-through |
| PC1 | FastEthernet0 | S0 | FastEthernet0/2 | Copper straight-through |
| R1 | GigabitEthernet0/0 | S1 | FastEthernet0/24 | Copper straight-through |
| PC2 | FastEthernet0 | S1 | FastEthernet0/1 | Copper straight-through |
| PC3 | FastEthernet0 | S1 | FastEthernet0/2 | Copper straight-through |
| R2 | GigabitEthernet0/0 | S2 | FastEthernet0/24 | Copper straight-through |
| PC4 | FastEthernet0 | S2 | FastEthernet0/1 | Copper straight-through |
| PC5 | FastEthernet0 | S2 | FastEthernet0/2 | Copper straight-through |
