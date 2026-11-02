### Simulated results for `P10c_PAT_Overload.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC0 | 192.168.1.11 | reply | as expected |
| PC0 | 192.168.1.100 | reply | as expected |
| Internet-Server | 192.168.1.10 | no reply | as expected |
| PC0 | 198.51.100.10 | reply | as expected |
| PC1 | 198.51.100.10 | reply | as expected |
| PC2 | 198.51.100.10 | reply | as expected |
| Web-Server | 198.51.100.10 | reply | as expected |
| Internet-Server | 203.0.113.10 | reply | as expected |

Expected routing tables:

```
R1# show ip route   (connected / static / OSPF / RIP part)
S    0.0.0.0/0 [1/0] via 203.0.113.2, Serial0/0/0
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
C    203.0.113.0/30 is directly connected, Serial0/0/0

ISP# show ip route   (connected / static / OSPF / RIP part)
C    198.51.100.0/24 is directly connected, GigabitEthernet0/0
S    203.0.113.0/24 [1/0] via 203.0.113.1, Serial0/0/0
C    203.0.113.0/30 is directly connected, Serial0/0/0

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| R1 | GigabitEthernet0/0 | 192.168.1.1 | 255.255.255.0 | Inside LAN |
| R1 | Serial0/0/0 | 203.0.113.1 | 255.255.255.252 | To ISP |
| ISP | Serial0/0/0 | 203.0.113.2 | 255.255.255.252 |  |
| ISP | GigabitEthernet0/0 | 198.51.100.1 | 255.255.255.0 | Internet |
| Internet-Server | FastEthernet0 | 198.51.100.10 | 255.255.255.0 | 198.51.100.1 |
| PC0 | FastEthernet0 | 192.168.1.10 | 255.255.255.0 | 192.168.1.1 |
| PC1 | FastEthernet0 | 192.168.1.11 | 255.255.255.0 | 192.168.1.1 |
| PC2 | FastEthernet0 | 192.168.1.12 | 255.255.255.0 | 192.168.1.1 |
| Web-Server | FastEthernet0 | 192.168.1.100 | 255.255.255.0 | 192.168.1.1 |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| R1 | Serial0/0/0 | ISP | Serial0/0/0 | Serial DCE (DCE end: R1) |
| R1 | GigabitEthernet0/0 | Switch0 | GigabitEthernet0/1 | Copper straight-through |
| ISP | GigabitEthernet0/0 | Internet-Server | FastEthernet0 | Copper cross-over |
| PC0 | FastEthernet0 | Switch0 | FastEthernet0/1 | Copper straight-through |
| PC1 | FastEthernet0 | Switch0 | FastEthernet0/2 | Copper straight-through |
| PC2 | FastEthernet0 | Switch0 | FastEthernet0/3 | Copper straight-through |
| Web-Server | FastEthernet0 | Switch0 | FastEthernet0/10 | Copper straight-through |
