### Simulated results for `P05_Router_Switch_Basics.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC0 | 192.168.1.11 | reply | as expected |
| PC1 | 192.168.1.10 | reply | as expected |
| PC0 | 192.168.1.1 | reply | as expected |
| PC1 | 192.168.1.1 | reply | as expected |

Expected routing tables:

```
MyRouter# show ip route   (connected / static / OSPF / RIP part)
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| MyRouter | GigabitEthernet0/0 | 192.168.1.1 | 255.255.255.0 | Link to MySwitch |
| PC0 | FastEthernet0 | 192.168.1.10 | 255.255.255.0 | 192.168.1.1 |
| PC1 | FastEthernet0 | 192.168.1.11 | 255.255.255.0 | 192.168.1.1 |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| MyRouter | GigabitEthernet0/0 | MySwitch | FastEthernet0/24 | Copper straight-through |
| PC0 | FastEthernet0 | MySwitch | FastEthernet0/1 | Copper straight-through |
| PC1 | FastEthernet0 | MySwitch | FastEthernet0/2 | Copper straight-through |
