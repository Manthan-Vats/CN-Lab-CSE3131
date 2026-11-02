### Simulated results for `P03_Star_Hub_and_Switch.pkt`

Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.

| From | Ping to | Result | Check |
|---|---|---|---|
| PC0 | 192.168.1.2 | reply | as expected |
| PC0 | 192.168.1.3 | reply | as expected |
| PC0 | 192.168.1.4 | reply | as expected |
| PC0 | 192.168.1.5 | reply | as expected |
| PC0 | 192.168.1.6 | reply | as expected |
| PC1 | 192.168.1.1 | reply | as expected |
| PC1 | 192.168.1.3 | reply | as expected |
| PC1 | 192.168.1.4 | reply | as expected |
| PC1 | 192.168.1.5 | reply | as expected |
| PC1 | 192.168.1.6 | reply | as expected |
| PC2 | 192.168.1.1 | reply | as expected |
| PC2 | 192.168.1.2 | reply | as expected |
| PC2 | 192.168.1.4 | reply | as expected |
| PC2 | 192.168.1.5 | reply | as expected |
| PC2 | 192.168.1.6 | reply | as expected |
| PC3 | 192.168.1.1 | reply | as expected |
| PC3 | 192.168.1.2 | reply | as expected |
| PC3 | 192.168.1.3 | reply | as expected |
| PC3 | 192.168.1.5 | reply | as expected |
| PC3 | 192.168.1.6 | reply | as expected |
| PC4 | 192.168.1.1 | reply | as expected |
| PC4 | 192.168.1.2 | reply | as expected |
| PC4 | 192.168.1.3 | reply | as expected |
| PC4 | 192.168.1.4 | reply | as expected |
| PC4 | 192.168.1.6 | reply | as expected |
| PC5 | 192.168.1.1 | reply | as expected |
| PC5 | 192.168.1.2 | reply | as expected |
| PC5 | 192.168.1.3 | reply | as expected |
| PC5 | 192.168.1.4 | reply | as expected |
| PC5 | 192.168.1.5 | reply | as expected |
| PC6 | 192.168.2.2 | reply | as expected |
| PC6 | 192.168.2.3 | reply | as expected |
| PC6 | 192.168.2.4 | reply | as expected |
| PC7 | 192.168.2.1 | reply | as expected |
| PC7 | 192.168.2.3 | reply | as expected |
| PC7 | 192.168.2.4 | reply | as expected |
| PC8 | 192.168.2.1 | reply | as expected |
| PC8 | 192.168.2.2 | reply | as expected |
| PC8 | 192.168.2.4 | reply | as expected |
| PC9 | 192.168.2.1 | reply | as expected |
| PC9 | 192.168.2.2 | reply | as expected |
| PC9 | 192.168.2.3 | reply | as expected |
| PC0 | 192.168.2.1 | no reply | as expected |

#### Addressing

| Device | Interface | IP address | Subnet mask | Gateway / notes |
|---|---|---|---|---|
| PC0 | FastEthernet0 | 192.168.1.1 | 255.255.255.0 | - |
| PC1 | FastEthernet0 | 192.168.1.2 | 255.255.255.0 | - |
| PC2 | FastEthernet0 | 192.168.1.3 | 255.255.255.0 | - |
| PC3 | FastEthernet0 | 192.168.1.4 | 255.255.255.0 | - |
| PC4 | FastEthernet0 | 192.168.1.5 | 255.255.255.0 | - |
| PC5 | FastEthernet0 | 192.168.1.6 | 255.255.255.0 | - |
| PC6 | FastEthernet0 | 192.168.2.1 | 255.255.255.0 | - |
| PC7 | FastEthernet0 | 192.168.2.2 | 255.255.255.0 | - |
| PC8 | FastEthernet0 | 192.168.2.3 | 255.255.255.0 | - |
| PC9 | FastEthernet0 | 192.168.2.4 | 255.255.255.0 | - |

#### Cabling

| From | Port | To | Port | Cable |
|---|---|---|---|---|
| PC0 | FastEthernet0 | Switch0 | FastEthernet0/1 | Copper straight-through |
| PC1 | FastEthernet0 | Switch0 | FastEthernet0/2 | Copper straight-through |
| PC2 | FastEthernet0 | Switch0 | FastEthernet0/3 | Copper straight-through |
| PC3 | FastEthernet0 | Switch0 | FastEthernet0/4 | Copper straight-through |
| PC4 | FastEthernet0 | Switch0 | FastEthernet0/5 | Copper straight-through |
| PC5 | FastEthernet0 | Switch0 | FastEthernet0/6 | Copper straight-through |
| PC6 | FastEthernet0 | Hub0 | FastEthernet0 | Copper straight-through |
| PC7 | FastEthernet0 | Hub0 | FastEthernet1 | Copper straight-through |
| PC8 | FastEthernet0 | Hub0 | FastEthernet2 | Copper straight-through |
| PC9 | FastEthernet0 | Hub0 | FastEthernet3 | Copper straight-through |
