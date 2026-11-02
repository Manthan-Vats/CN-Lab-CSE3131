### Simulated results for `P12_Device_Security_ACL_SSH.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| Staff-PC1 | 192.168.30.100 | reply | as expected |
| Admin-PC | 192.168.30.100 | reply | as expected |
| Guest-PC | 192.168.30.100 | no reply | as expected |
| Guest-PC | 192.168.10.10 | reply | as expected |
| Staff-PC2 | 192.168.20.10 | reply | as expected |

Expected routing tables:

```
R1# show ip route   (connected / static / OSPF / RIP part)
C    192.168.10.0/24 is directly connected, GigabitEthernet0/0
C    192.168.20.0/24 is directly connected, GigabitEthernet0/1
C    192.168.30.0/24 is directly connected, GigabitEthernet0/2

```

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| R1 | GigabitEthernet0/0 | 192.168.10.1 | 255.255.255.0 | Staff LAN |
| R1 | GigabitEthernet0/1 | 192.168.20.1 | 255.255.255.0 | Guest LAN |
| R1 | GigabitEthernet0/2 | 192.168.30.1 | 255.255.255.0 | Server LAN |
| Server0 | FastEthernet0 | 192.168.30.100 | 255.255.255.0 | 192.168.30.1 |
| Staff-PC1 | FastEthernet0 | 192.168.10.10 | 255.255.255.0 | 192.168.10.1 |
| Staff-PC2 | FastEthernet0 | 192.168.10.11 | 255.255.255.0 | 192.168.10.1 |
| Admin-PC | FastEthernet0 | 192.168.10.20 | 255.255.255.0 | 192.168.10.1 |
| Guest-PC | FastEthernet0 | 192.168.20.10 | 255.255.255.0 | 192.168.20.1 |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| R1 | GigabitEthernet0/0 | SW1 | GigabitEthernet0/1 | Copper straight-through |
| R1 | GigabitEthernet0/1 | SW2 | GigabitEthernet0/1 | Copper straight-through |
| R1 | GigabitEthernet0/2 | Server0 | FastEthernet0 | Copper cross-over |
| Staff-PC1 | FastEthernet0 | SW1 | FastEthernet0/1 | Copper straight-through |
| Staff-PC2 | FastEthernet0 | SW1 | FastEthernet0/2 | Copper straight-through |
| Admin-PC | FastEthernet0 | SW1 | FastEthernet0/3 | Copper straight-through |
| Guest-PC | FastEthernet0 | SW2 | FastEthernet0/1 | Copper straight-through |
