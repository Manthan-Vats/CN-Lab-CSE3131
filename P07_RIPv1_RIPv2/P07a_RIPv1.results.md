### Simulated results for `P07a_RIPv1.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC0 | 60.0.0.2 | reply | as expected |
| PC0 | 8.0.0.2 | reply | as expected |
| PC1 | 192.168.1.2 | reply | as expected |
| PC1 | 8.0.0.2 | reply | as expected |
| PC2 | 192.168.1.2 | reply | as expected |
| PC2 | 60.0.0.2 | reply | as expected |

Expected routing tables:

```
Router0# show ip route   (connected / static / OSPF / RIP part)
R    8.0.0.0/8 [120/1] via 20.0.0.2, GigabitEthernet0/1
C    20.0.0.0/8 is directly connected, GigabitEthernet0/1
C    30.0.0.0/8 is directly connected, GigabitEthernet0/2
R    40.0.0.0/8 [120/1] via 30.0.0.2, GigabitEthernet0/2
R    50.0.0.0/8 [120/1] via 20.0.0.2, GigabitEthernet0/1
R    60.0.0.0/8 [120/2] via 20.0.0.2, GigabitEthernet0/1
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0

Router1# show ip route   (connected / static / OSPF / RIP part)
R    8.0.0.0/8 [120/2] via 30.0.0.1, GigabitEthernet0/0
R    20.0.0.0/8 [120/1] via 30.0.0.1, GigabitEthernet0/0
C    30.0.0.0/8 is directly connected, GigabitEthernet0/0
C    40.0.0.0/8 is directly connected, GigabitEthernet0/1
R    50.0.0.0/8 [120/1] via 40.0.0.2, GigabitEthernet0/1
R    60.0.0.0/8 [120/1] via 40.0.0.2, GigabitEthernet0/1
R    192.168.1.0/24 [120/1] via 30.0.0.1, GigabitEthernet0/0

Router2# show ip route   (connected / static / OSPF / RIP part)
R    8.0.0.0/8 [120/1] via 50.0.0.2, GigabitEthernet0/1
R    20.0.0.0/8 [120/1] via 50.0.0.2, GigabitEthernet0/1
R    30.0.0.0/8 [120/1] via 40.0.0.1, GigabitEthernet0/0
C    40.0.0.0/8 is directly connected, GigabitEthernet0/0
C    50.0.0.0/8 is directly connected, GigabitEthernet0/1
C    60.0.0.0/8 is directly connected, GigabitEthernet0/2
R    192.168.1.0/24 [120/2] via 40.0.0.1, GigabitEthernet0/0

Router3# show ip route   (connected / static / OSPF / RIP part)
C    8.0.0.0/8 is directly connected, GigabitEthernet0/2
C    20.0.0.0/8 is directly connected, GigabitEthernet0/1
R    30.0.0.0/8 [120/1] via 20.0.0.1, GigabitEthernet0/1
R    40.0.0.0/8 [120/1] via 50.0.0.1, GigabitEthernet0/0
C    50.0.0.0/8 is directly connected, GigabitEthernet0/0
R    60.0.0.0/8 [120/1] via 50.0.0.1, GigabitEthernet0/0
R    192.168.1.0/24 [120/1] via 20.0.0.1, GigabitEthernet0/1

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| Router0 | GigabitEthernet0/0 | 192.168.1.1 | 255.255.255.0 | PC0 LAN |
| Router0 | GigabitEthernet0/1 | 20.0.0.1 | 255.0.0.0 |  |
| Router0 | GigabitEthernet0/2 | 30.0.0.1 | 255.0.0.0 |  |
| Router1 | GigabitEthernet0/0 | 30.0.0.2 | 255.0.0.0 |  |
| Router1 | GigabitEthernet0/1 | 40.0.0.1 | 255.0.0.0 |  |
| Router2 | GigabitEthernet0/0 | 40.0.0.2 | 255.0.0.0 |  |
| Router2 | GigabitEthernet0/1 | 50.0.0.1 | 255.0.0.0 |  |
| Router2 | GigabitEthernet0/2 | 60.0.0.1 | 255.0.0.0 | PC1 LAN |
| Router3 | GigabitEthernet0/0 | 50.0.0.2 | 255.0.0.0 |  |
| Router3 | GigabitEthernet0/1 | 20.0.0.2 | 255.0.0.0 |  |
| Router3 | GigabitEthernet0/2 | 8.0.0.1 | 255.0.0.0 | PC2 LAN |
| PC0 | FastEthernet0 | 192.168.1.2 | 255.255.255.0 | 192.168.1.1 |
| PC1 | FastEthernet0 | 60.0.0.2 | 255.0.0.0 | 60.0.0.1 |
| PC2 | FastEthernet0 | 8.0.0.2 | 255.0.0.0 | 8.0.0.1 |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| Router0 | GigabitEthernet0/0 | PC0 | FastEthernet0 | Copper cross-over |
| Router0 | GigabitEthernet0/1 | Router3 | GigabitEthernet0/1 | Copper cross-over |
| Router0 | GigabitEthernet0/2 | Router1 | GigabitEthernet0/0 | Copper cross-over |
| Router1 | GigabitEthernet0/1 | Router2 | GigabitEthernet0/0 | Copper cross-over |
| Router2 | GigabitEthernet0/1 | Router3 | GigabitEthernet0/0 | Copper cross-over |
| Router2 | GigabitEthernet0/2 | PC1 | FastEthernet0 | Copper cross-over |
| Router3 | GigabitEthernet0/2 | PC2 | FastEthernet0 | Copper cross-over |
