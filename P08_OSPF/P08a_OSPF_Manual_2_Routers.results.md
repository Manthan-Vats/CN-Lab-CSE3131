### Simulated results for `P08a_OSPF_Manual_2_Routers.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC1 | 30.0.0.2 | reply | as expected |
| PC2 | 10.0.0.2 | reply | as expected |

Expected routing tables:

```
R1# show ip route   (connected / static / OSPF / RIP part)
C    10.0.0.0/8 is directly connected, GigabitEthernet0/0
C    20.0.0.0/8 is directly connected, Serial0/0/0
O    30.0.0.0/8 [110/65] via 20.0.0.2, Serial0/0/0

R2# show ip route   (connected / static / OSPF / RIP part)
O    10.0.0.0/8 [110/65] via 20.0.0.1, Serial0/0/0
C    20.0.0.0/8 is directly connected, Serial0/0/0
C    30.0.0.0/8 is directly connected, GigabitEthernet0/0

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| R1 | GigabitEthernet0/0 | 10.0.0.1 | 255.0.0.0 |  |
| R1 | Serial0/0/0 | 20.0.0.1 | 255.0.0.0 |  |
| R2 | GigabitEthernet0/0 | 30.0.0.1 | 255.0.0.0 |  |
| R2 | Serial0/0/0 | 20.0.0.2 | 255.0.0.0 |  |
| PC1 | FastEthernet0 | 10.0.0.2 | 255.0.0.0 | 10.0.0.1 |
| PC2 | FastEthernet0 | 30.0.0.2 | 255.0.0.0 | 30.0.0.1 |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| R1 | Serial0/0/0 | R2 | Serial0/0/0 | Serial DCE (DCE end: R1) |
| R1 | GigabitEthernet0/0 | PC1 | FastEthernet0 | Copper cross-over |
| R2 | GigabitEthernet0/0 | PC2 | FastEthernet0 | Copper cross-over |
