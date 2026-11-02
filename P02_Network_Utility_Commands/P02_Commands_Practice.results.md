### Simulated results for `P02_Commands_Practice.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC0 | 192.168.1.11 | reply | as expected |
| PC0 | 192.168.2.10 | reply | as expected |
| PC0 | 192.168.2.100 | reply | as expected |
| PC1 | 192.168.1.10 | reply | as expected |
| PC1 | 192.168.2.10 | reply | as expected |
| PC1 | 192.168.2.100 | reply | as expected |
| PC2 | 192.168.1.10 | reply | as expected |
| PC2 | 192.168.1.11 | reply | as expected |
| PC2 | 192.168.2.100 | reply | as expected |
| DNS-Server | 192.168.1.10 | reply | as expected |
| DNS-Server | 192.168.1.11 | reply | as expected |
| DNS-Server | 192.168.2.10 | reply | as expected |

Expected routing tables:

```
R1# show ip route   (connected / static / OSPF / RIP part)
C    10.1.1.0/30 is directly connected, GigabitEthernet0/1
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
S    192.168.2.0/24 [1/0] via 10.1.1.2, GigabitEthernet0/1

R2# show ip route   (connected / static / OSPF / RIP part)
C    10.1.1.0/30 is directly connected, GigabitEthernet0/1
S    192.168.1.0/24 [1/0] via 10.1.1.1, GigabitEthernet0/1
C    192.168.2.0/24 is directly connected, GigabitEthernet0/0

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| R1 | GigabitEthernet0/0 | 192.168.1.1 | 255.255.255.0 |  |
| R1 | GigabitEthernet0/1 | 10.1.1.1 | 255.255.255.252 |  |
| R2 | GigabitEthernet0/0 | 192.168.2.1 | 255.255.255.0 |  |
| R2 | GigabitEthernet0/1 | 10.1.1.2 | 255.255.255.252 |  |
| PC0 | FastEthernet0 | 192.168.1.10 | 255.255.255.0 | 192.168.1.1, DNS 192.168.2.100 |
| PC1 | FastEthernet0 | 192.168.1.11 | 255.255.255.0 | 192.168.1.1, DNS 192.168.2.100 |
| PC2 | FastEthernet0 | 192.168.2.10 | 255.255.255.0 | 192.168.2.1, DNS 192.168.2.100 |
| DNS-Server | FastEthernet0 | 192.168.2.100 | 255.255.255.0 | 192.168.2.1, DNS 192.168.2.100 |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| R1 | GigabitEthernet0/1 | R2 | GigabitEthernet0/1 | Copper cross-over |
| R1 | GigabitEthernet0/0 | SW1 | GigabitEthernet0/1 | Copper straight-through |
| R2 | GigabitEthernet0/0 | SW2 | GigabitEthernet0/1 | Copper straight-through |
| PC0 | FastEthernet0 | SW1 | FastEthernet0/1 | Copper straight-through |
| PC1 | FastEthernet0 | SW1 | FastEthernet0/2 | Copper straight-through |
| PC2 | FastEthernet0 | SW2 | FastEthernet0/1 | Copper straight-through |
| DNS-Server | FastEthernet0 | SW2 | FastEthernet0/2 | Copper straight-through |
