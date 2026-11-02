### Simulated results for `P09b_InterVLAN_Router_on_a_Stick.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC0 | 192.168.10.12 | reply | as expected |
| PC0 | 192.168.20.11 | reply | as expected |
| PC0 | 192.168.20.12 | reply | as expected |
| PC0 | 192.168.10.21 | reply | as expected |
| PC0 | 192.168.10.22 | reply | as expected |
| PC0 | 192.168.20.21 | reply | as expected |
| PC0 | 192.168.20.22 | reply | as expected |
| PC1 | 192.168.10.11 | reply | as expected |
| PC1 | 192.168.20.11 | reply | as expected |
| PC1 | 192.168.20.12 | reply | as expected |
| PC1 | 192.168.10.21 | reply | as expected |
| PC1 | 192.168.10.22 | reply | as expected |
| PC1 | 192.168.20.21 | reply | as expected |
| PC1 | 192.168.20.22 | reply | as expected |
| PC2 | 192.168.10.11 | reply | as expected |
| PC2 | 192.168.10.12 | reply | as expected |
| PC2 | 192.168.20.12 | reply | as expected |
| PC2 | 192.168.10.21 | reply | as expected |
| PC2 | 192.168.10.22 | reply | as expected |
| PC2 | 192.168.20.21 | reply | as expected |
| PC2 | 192.168.20.22 | reply | as expected |
| PC3 | 192.168.10.11 | reply | as expected |
| PC3 | 192.168.10.12 | reply | as expected |
| PC3 | 192.168.20.11 | reply | as expected |
| PC3 | 192.168.10.21 | reply | as expected |
| PC3 | 192.168.10.22 | reply | as expected |
| PC3 | 192.168.20.21 | reply | as expected |
| PC3 | 192.168.20.22 | reply | as expected |
| PC4 | 192.168.10.11 | reply | as expected |
| PC4 | 192.168.10.12 | reply | as expected |
| PC4 | 192.168.20.11 | reply | as expected |
| PC4 | 192.168.20.12 | reply | as expected |
| PC4 | 192.168.10.22 | reply | as expected |
| PC4 | 192.168.20.21 | reply | as expected |
| PC4 | 192.168.20.22 | reply | as expected |
| PC5 | 192.168.10.11 | reply | as expected |
| PC5 | 192.168.10.12 | reply | as expected |
| PC5 | 192.168.20.11 | reply | as expected |
| PC5 | 192.168.20.12 | reply | as expected |
| PC5 | 192.168.10.21 | reply | as expected |
| PC5 | 192.168.20.21 | reply | as expected |
| PC5 | 192.168.20.22 | reply | as expected |
| PC6 | 192.168.10.11 | reply | as expected |
| PC6 | 192.168.10.12 | reply | as expected |
| PC6 | 192.168.20.11 | reply | as expected |
| PC6 | 192.168.20.12 | reply | as expected |
| PC6 | 192.168.10.21 | reply | as expected |
| PC6 | 192.168.10.22 | reply | as expected |
| PC6 | 192.168.20.22 | reply | as expected |
| PC7 | 192.168.10.11 | reply | as expected |
| PC7 | 192.168.10.12 | reply | as expected |
| PC7 | 192.168.20.11 | reply | as expected |
| PC7 | 192.168.20.12 | reply | as expected |
| PC7 | 192.168.10.21 | reply | as expected |
| PC7 | 192.168.10.22 | reply | as expected |
| PC7 | 192.168.20.21 | reply | as expected |

Expected routing tables:

```
Router0# show ip route   (connected / static / OSPF / RIP part)
C    192.168.10.0/24 is directly connected, GigabitEthernet0/0.10
C    192.168.20.0/24 is directly connected, GigabitEthernet0/0.20

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| Router0 | GigabitEthernet0/0.10 | 192.168.10.1 | 255.255.255.0 | VLAN 10 sub-interface |
| Router0 | GigabitEthernet0/0.20 | 192.168.20.1 | 255.255.255.0 | VLAN 20 sub-interface |
| PC0 | FastEthernet0 | 192.168.10.11 | 255.255.255.0 | 192.168.10.1 |
| PC1 | FastEthernet0 | 192.168.10.12 | 255.255.255.0 | 192.168.10.1 |
| PC2 | FastEthernet0 | 192.168.20.11 | 255.255.255.0 | 192.168.20.1 |
| PC3 | FastEthernet0 | 192.168.20.12 | 255.255.255.0 | 192.168.20.1 |
| PC4 | FastEthernet0 | 192.168.10.21 | 255.255.255.0 | 192.168.10.1 |
| PC5 | FastEthernet0 | 192.168.10.22 | 255.255.255.0 | 192.168.10.1 |
| PC6 | FastEthernet0 | 192.168.20.21 | 255.255.255.0 | 192.168.20.1 |
| PC7 | FastEthernet0 | 192.168.20.22 | 255.255.255.0 | 192.168.20.1 |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| Switch0 | GigabitEthernet0/1 | Switch1 | GigabitEthernet0/1 | Copper cross-over |
| Router0 | GigabitEthernet0/0 | Switch0 | GigabitEthernet0/2 | Copper straight-through |
| PC0 | FastEthernet0 | Switch0 | FastEthernet0/1 | Copper straight-through |
| PC1 | FastEthernet0 | Switch0 | FastEthernet0/2 | Copper straight-through |
| PC2 | FastEthernet0 | Switch0 | FastEthernet0/3 | Copper straight-through |
| PC3 | FastEthernet0 | Switch0 | FastEthernet0/4 | Copper straight-through |
| PC4 | FastEthernet0 | Switch1 | FastEthernet0/1 | Copper straight-through |
| PC5 | FastEthernet0 | Switch1 | FastEthernet0/2 | Copper straight-through |
| PC6 | FastEthernet0 | Switch1 | FastEthernet0/3 | Copper straight-through |
| PC7 | FastEthernet0 | Switch1 | FastEthernet0/4 | Copper straight-through |
