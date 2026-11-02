### Simulated results for `P06_Static_Routing.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC0 | 192.168.1.3 | reply | as expected |
| PC0 | 192.168.2.2 | reply | as expected |
| PC0 | 192.168.2.3 | reply | as expected |
| PC1 | 192.168.1.2 | reply | as expected |
| PC1 | 192.168.2.2 | reply | as expected |
| PC1 | 192.168.2.3 | reply | as expected |
| PC2 | 192.168.1.2 | reply | as expected |
| PC2 | 192.168.1.3 | reply | as expected |
| PC2 | 192.168.2.3 | reply | as expected |
| PC3 | 192.168.1.2 | reply | as expected |
| PC3 | 192.168.1.3 | reply | as expected |
| PC3 | 192.168.2.2 | reply | as expected |

Expected routing tables:

```
Router0# show ip route   (connected / static / OSPF / RIP part)
C    11.0.0.0/8 is directly connected, Serial0/0/0
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
S    192.168.2.0/24 [1/0] via 11.0.0.2, Serial0/0/0

Router1# show ip route   (connected / static / OSPF / RIP part)
C    11.0.0.0/8 is directly connected, Serial0/0/0
S    192.168.1.0/24 [1/0] via 11.0.0.1, Serial0/0/0
C    192.168.2.0/24 is directly connected, GigabitEthernet0/0

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| Router0 | GigabitEthernet0/0 | 192.168.1.1 | 255.255.255.0 |  |
| Router0 | Serial0/0/0 | 11.0.0.1 | 255.0.0.0 |  |
| Router1 | GigabitEthernet0/0 | 192.168.2.1 | 255.255.255.0 |  |
| Router1 | Serial0/0/0 | 11.0.0.2 | 255.0.0.0 |  |
| PC0 | FastEthernet0 | 192.168.1.2 | 255.255.255.0 | 192.168.1.1 |
| PC1 | FastEthernet0 | 192.168.1.3 | 255.255.255.0 | 192.168.1.1 |
| PC2 | FastEthernet0 | 192.168.2.2 | 255.255.255.0 | 192.168.2.1 |
| PC3 | FastEthernet0 | 192.168.2.3 | 255.255.255.0 | 192.168.2.1 |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| Router0 | Serial0/0/0 | Router1 | Serial0/0/0 | Serial DCE (DCE end: Router0) |
| Router0 | GigabitEthernet0/0 | Switch0 | GigabitEthernet0/1 | Copper straight-through |
| Router1 | GigabitEthernet0/0 | Switch1 | GigabitEthernet0/1 | Copper straight-through |
| PC0 | FastEthernet0 | Switch0 | FastEthernet0/1 | Copper straight-through |
| PC1 | FastEthernet0 | Switch0 | FastEthernet0/2 | Copper straight-through |
| PC2 | FastEthernet0 | Switch1 | FastEthernet0/1 | Copper straight-through |
| PC3 | FastEthernet0 | Switch1 | FastEthernet0/2 | Copper straight-through |
