# Program 3: Star topology using a hub and a switch

**Aim:** build a star topology using a hub and a switch, configure IP addresses on the end
devices, and on the switch use show commands, the copy command, a password and a hostname.

## Files

| File | What it is |
|---|---|
| `P03_Star_Hub_and_Switch.pkt` | Both stars, fully configured |
| `configs/P03_Star_Hub_and_Switch/Switch0.txt` | Switch commands (hostname, passwords, banner, save) |
| `P03_Star_Hub_and_Switch.results.md` | Addressing, cabling, expected pings |

## Topology

```
   PC0 .1   PC1 .2   PC2 .3              PC6 .1        PC7 .2
       \      |      /                       \          /
          Switch0  (2960)                       Hub0  (Hub-PT)
       /      |      \                       /          \
   PC3 .4   PC4 .5   PC5 .6              PC8 .3        PC9 .4
   SWITCH star: 192.168.1.0/24            HUB star: 192.168.2.0/24
```

The two stars are separate LANs with no router between them, so a PC on the switch can't
reach a PC on the hub. That's expected.

## Procedure (to build it yourself)

1. Place a **2960** switch and 6 **PC-PT**. Connect each PC's FastEthernet0 to Switch0 Fa0/1–Fa0/6
   with a **copper straight-through** cable.
2. Place a **Hub-PT** and 4 PCs. Connect them to hub ports Fa0–Fa3 (straight-through).
3. On each PC: **Desktop > IP Configuration > Static**. Enter the IP and mask
   `255.255.255.0` (switch side 192.168.1.1–6, hub side 192.168.2.1–4). No gateway needed.
4. Configure the switch: **Switch0 > CLI**, then paste `configs/P03_Star_Hub_and_Switch/Switch0.txt`:

```
enable
configure terminal
hostname Switch0
enable secret class                    ! password for privileged mode
line console 0
 password cisco                        ! password for the console
 login
 exit
line vty 0 4
 password cisco                        ! password for telnet
 login
 exit
banner motd #Authorised access only - CN Lab#
end
write memory                           ! same as: copy running-config startup-config
```

5. Ping between PCs (PC0 > Command Prompt > `ping 192.168.1.4`).

## Show and copy commands to run on the switch (and what you'll see)

| Command | Shows |
|---|---|
| `show running-config` | The config in RAM: hostname, enable secret, line passwords |
| `show startup-config` | The config saved in NVRAM (the same after `write memory`) |
| `show version` | IOS version, uptime, model, memory |
| `show interfaces status` / `show ip interface brief` | Every port: connected/notconnect, speed, VLAN |
| `show mac address-table` | MAC addresses learned on each port (ping first, then look) |
| `show vlan brief` | All ports in VLAN 1 (default) |
| `copy running-config startup-config` | Save RAM config to NVRAM so it survives a reload |
| `copy startup-config running-config` | Load the saved config back into RAM |
| `erase startup-config` then `reload` | Factory reset |

## Hub vs switch: see it in Simulation mode

1. Click **Simulation**, then **Edit Filters**, and keep only ICMP.
2. Add a simple PDU from PC6 to PC7 (envelope icon: click PC6, then PC7). Press **Capture/Forward**.
   The hub copies the frame to **PC8 and PC9 too**. They drop it because the MAC isn't theirs.
3. Do the same from PC0 to PC1. The switch sends the frame **only to PC1** once it has learned
   the MACs. (The very first ARP broadcast floods; after that, unicast.)

## Expected result

All 6 switch PCs ping each other, and all 4 hub PCs ping each other (42 successful pings,
checked in `P03_Star_Hub_and_Switch.results.md`).

## Viva answers

1. **Switch vs hub forwarding:** a hub is a Layer-1 repeater. It sends every bit out of every
   port, so all ports share one collision domain and bandwidth. A switch is Layer 2. It learns
   source MACs into its MAC table and forwards each frame only to the destination port
   (flooding only unknown and broadcast frames). Every port is a separate collision domain
   and runs full duplex.
2. **Saving the running config:** `copy running-config startup-config` (or `write memory`)
   copies the config from RAM to NVRAM.
3. **Why set passwords:** to stop anyone with console or telnet access from viewing or changing
   the configuration. `enable secret` protects privileged mode (stored as an MD5 hash), and line
   passwords protect console and VTY access.
4. **How subnetting helps:** it splits one large network into smaller ones. This means smaller
   broadcast domains (less broadcast traffic), better security and separation between groups,
   efficient use of addresses, and easier management and troubleshooting.
