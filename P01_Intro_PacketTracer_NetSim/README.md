# Program 1: Introduction to Packet Tracer, NetSim and networking device components

**Aim (1A):** get to know Packet Tracer and the networking devices it simulates.
**Aim (1B):** study the NetSim simulation environment and its device components.

## Files

| File | What it is |
|---|---|
| `P01_Device_Tour.pkt` | One small network that uses every basic device and every cable type, fully configured |
| `configs/P01_Device_Tour/R1.txt`, `configs/P01_Device_Tour/R2.txt` | Router commands (paste into the CLI to rebuild) |
| `P01_Device_Tour.results.md` | Addressing, cabling, routing tables, expected pings |

## What is in the tour file

```
                 Serial DCE (10.0.0.0/30)
         R1 ===================================== R2
          | Gig0/0 192.168.1.1                    | Gig0/0 192.168.2.1
          | straight-through                      | cross-over (router to PC)
        SW1 (2960) ---- cross-over ---- HUB1      PC4 192.168.2.10
       /   |    \                      /    \
   PC0   PC1   Server0              PC2     PC3
   .10   .11   .100 (DNS)           .20     .21        LAN-A 192.168.1.0/24
```

| Device in the file | Category in Packet Tracer | Layer | What it does here |
|---|---|---|---|
| R1, R2 (Cisco 2911) | Network Devices > Routers | 3 | Join LAN-A and LAN-B; static routes |
| SW1 (Cisco 2960) | Network Devices > Switches | 2 | Sends each frame only to the port of the destination MAC |
| HUB1 (Hub-PT) | Network Devices > Hubs | 1 | Repeats every frame out of every port |
| PC0–PC4 (PC-PT) | End Devices | 1–7 | Hosts with static IPs |
| Server0 (Server-PT) | End Devices | 1–7 | Answers DNS for `www.cnlab.local` and serves a web page |
| Copper straight-through | Connections | 1 | Unlike devices: PC↔switch, router↔switch, PC↔hub |
| Copper cross-over | Connections | 1 | Like devices: switch↔hub, router↔PC (PC and router both transmit on the same pins) |
| Serial DCE | Connections | 1 | Router WAN link; the DCE end (R1) supplies the clock (`clock rate 64000`) |

Things to try after opening the file:
1. PC0 > Command Prompt > `ping 192.168.2.10` (crosses both routers).
2. PC2 > Web Browser > `www.cnlab.local` (DNS lookup on Server0, then HTTP).
3. Switch to **Simulation** mode (bottom-right), filter ICMP, ping PC0 → PC2, and press
   *Capture/Forward*. The hub floods the frame to PC3, but the switch does not flood to PC1
   once it has learned the MACs.
4. Hover over a link to see the port names; click a router > **Physical** to see the HWIC-2T serial card.

## Packet Tracer basics (for the write-up)

- **Workspace:** *Logical* (topology) and *Physical* (city > building > wiring closet > rack).
- **Modes:** *Realtime* (things happen live) and *Simulation* (step packet by packet, see each PDU's OSI layers).
- **Device tabs:** *Physical* (power, modules), *Config* (GUI settings), *CLI* (IOS command line),
  *Desktop* (on PCs: IP Configuration, Command Prompt, Web Browser…), *Services* (on servers: HTTP, DNS, DHCP, FTP…).
- **Cable colours:** solid black = straight-through, dashed = cross-over, red zig-zag = serial.
  A clock icon marks the DCE end.
- **Link lights:** green = up; orange = the switch port is in STP listening/learning (wait ~30 s); red = down/shut.
- Save with **File > Save As (.pkt)**. Router configs survive only if saved inside the device
  (`copy running-config startup-config`) *and* the .pkt is saved.

## 1B: NetSim (Tetcos) (write-up)

NetSim is a commercial network simulator and emulator from Tetcos. It's licensed, so there's
no file here. Use the college copy for this part.

**Components:** routers (static, RIP, OSPF), switches (Ethernet, VLAN), end nodes (PCs,
servers, workstations), wireless access points and mobile nodes (IEEE 802.11, mobility
models), links (Ethernet, wireless, fibre, point-to-point, serial; each with bandwidth, delay
and error rate), the Internet cloud (WAN), application/traffic generators (FTP, HTTP, Email,
Video, VoIP, custom/CBR), the simulation engine (discrete-event: packet generation, routing,
queueing, collisions) and the performance analyser.

**Procedure:**
1. Open NetSim and choose a scenario (e.g. *Internetworks*).
2. Drag 2 routers, 2 switches and 4 nodes, and connect them with wired links.
3. Set IPs (NetSim auto-assigns by default).
4. Click *Application* and add a CBR or FTP flow from Node A to Node B.
5. Set the simulation time to 10 s and run.
6. Open the *Results Dashboard* and note throughput, delay, packet loss and jitter.
7. Enable *Packet Trace / Event Trace* and *Animation* to watch packets move.
8. Compare runs, e.g. change the link speed from 100 to 10 Mbps and see delay rise.

**Metrics NetSim reports:**
- **Throughput:** bits delivered per second.
- **End-to-end delay:** time from sending to receiving.
- **PDR:** received ÷ sent packets.
- **Packet loss:** 1 − PDR.
- **Jitter:** variation in delay.
- **Utilisation:** how busy each link is.

**Packet Tracer vs NetSim:**

| | Packet Tracer | NetSim |
|---|---|---|
| Focus | Cisco configuration (IOS CLI) | Protocol performance analysis |
| Output | Working configs, ping/traceroute, PDU view | Graphs: throughput, delay, PDR, jitter |
| Technologies | Cisco LAN/WAN, IoT | Wired, Wi-Fi, LTE/5G, IoT, MANET, SDN |
| Cost | Free (Cisco Networking Academy login) | Paid licence |

## Viva answers

1. **Role of a switch:** it connects devices in one LAN, learns which MAC address is on which
   port (MAC address table), and forwards each frame only to the right port. Every port is
   its own collision domain. It works at Layer 2.
2. **Router vs switch:** a switch forwards frames by **MAC** inside one network (L2). A router
   forwards packets by **IP** between different networks (L3), keeps a routing table, and each
   port is its own broadcast domain. A switch connects devices; a router connects networks.
3. **Cables and connectors:**
   - Straight-through (UTP, RJ-45, same pin order at both ends): unlike devices (PC–switch, router–switch).
   - Cross-over (pins 1-2 ↔ 3-6 swapped): like devices (switch–switch, PC–PC, router–PC).
   - Rollover/console (RJ-45 ↔ DB-9/USB): PC to a device's console port.
   - Serial (DB-60/Smart-Serial, DCE/DTE): router WAN links.
   - Fibre (LC/SC): long distances, no EMI.
   - Coaxial (BNC/F): older Ethernet and cable modems.
4. **Bridge vs brouter:** a bridge is a Layer-2 device that joins two LAN segments and filters
   frames by MAC. A brouter (bridge + router) *routes* packets of routable protocols (like IP)
   and *bridges* everything else, working at Layers 2 and 3.
