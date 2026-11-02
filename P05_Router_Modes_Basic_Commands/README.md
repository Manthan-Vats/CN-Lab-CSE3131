# Program 5: Router modes and basic router/switch commands

**Aim:** understand the router's command modes and use the basic commands for configuring and
managing routers and switches.

## Files

| File | What it is |
|---|---|
| `P05_Router_Switch_Basics.pkt` | MyRouter + MySwitch (VLAN 10 "Sales") + 2 PCs, all configured |
| `configs/P05_Router_Switch_Basics/MyRouter.txt`, `configs/P05_Router_Switch_Basics/MySwitch.txt` | The commands |
| `P05_Router_Switch_Basics.results.md` | Addressing, cabling, expected pings |

```
            MyRouter  Gig0/0 192.168.1.1
               |  (Fa0/24, VLAN 10)
            MySwitch      VLAN 10 "Sales" = Fa0/1, Fa0/2, Fa0/24
            /      \
     PC0 .10        PC1 .11        (192.168.1.0/24, gateway .1)
```

Passwords: `enable` → **class**, console / telnet → **cisco**.

## The modes

| Mode | Prompt | How to get in | How to get out | What you can do |
|---|---|---|---|---|
| User EXEC | `MyRouter>` | start / press Enter | `exit` | ping, traceroute, basic `show` |
| Privileged EXEC | `MyRouter#` | `enable` | `disable` | all `show`, `debug`, `copy`, `reload`, `write` |
| Global config | `MyRouter(config)#` | `configure terminal` | `exit` / `end` / Ctrl+Z | hostname, passwords, routing, banner |
| Interface config | `MyRouter(config-if)#` | `interface Gig0/0` | `exit` | ip address, `no shutdown`, description |
| Line config | `MyRouter(config-line)#` | `line console 0` / `line vty 0 4` | `exit` | password, login |
| Router config | `MyRouter(config-router)#` | `router ospf 1` / `router rip` | `exit` | network statements |
| VLAN config (switch) | `MySwitch(config-vlan)#` | `vlan 10` | `exit` | name |

`end` (or Ctrl+Z) jumps from any config mode straight back to `#`. `?` lists the commands
allowed in the current mode, and Tab completes a word.

## Router commands used (from `configs/P05_Router_Switch_Basics/MyRouter.txt`)

```
Router> enable
Router# configure terminal
Router(config)# hostname MyRouter
MyRouter(config)# enable secret class
MyRouter(config)# line console 0
MyRouter(config-line)# password cisco
MyRouter(config-line)# login
MyRouter(config-line)# exit
MyRouter(config)# line vty 0 4
MyRouter(config-line)# password cisco
MyRouter(config-line)# login
MyRouter(config-line)# exit
MyRouter(config)# service password-encryption        ! hides the line passwords in show run
MyRouter(config)# banner motd #MyRouter - CN Lab Program 5#
MyRouter(config)# interface GigabitEthernet0/0
MyRouter(config-if)# description Link to MySwitch
MyRouter(config-if)# ip address 192.168.1.1 255.255.255.0
MyRouter(config-if)# no shutdown
MyRouter(config-if)# end
MyRouter# write memory
```

## Switch commands used (from `configs/P05_Router_Switch_Basics/MySwitch.txt`)

```
Switch(config)# hostname MySwitch
MySwitch(config)# vlan 10
MySwitch(config-vlan)# name Sales
MySwitch(config-vlan)# exit
MySwitch(config)# interface FastEthernet0/1
MySwitch(config-if)# switchport mode access
MySwitch(config-if)# switchport access vlan 10
   (same for Fa0/2 and Fa0/24)
```

## Show commands and what to look for

| Command | Expected |
|---|---|
| `show ip interface brief` | `GigabitEthernet0/0  192.168.1.1  YES manual up  up` |
| `show running-config` | hostname, `enable secret 5 $1$...` (hashed), encrypted line passwords |
| `show interfaces GigabitEthernet0/0` | up/up, MAC, MTU, counters |
| `show version` | IOS 15.1, 2911, uptime, config register 0x2102 |
| `show history` | your last commands |
| `MySwitch# show vlan brief` | `10  Sales  active  Fa0/1, Fa0/2, Fa0/24` |
| `MySwitch# show mac address-table` | PC MACs learned on Fa0/1, Fa0/2 |
| `ping 192.168.1.10` (from the router) | `!!!!!` |

## Viva answers

1. **User EXEC vs Privileged EXEC:** user EXEC (`>`) allows only limited monitoring commands
   and can't change or view the full config. Privileged EXEC (`#`, entered with `enable`)
   allows every show/debug/copy/reload command and the way into configuration mode.
2. **Why `no shutdown`:** router interfaces are administratively down by default. `no shutdown`
   turns the interface on so it can pass traffic (status up/up). Switch ports are up by default.
3. **Default gateway:** the router interface address that hosts send to when the destination
   is outside their subnet. On a router itself, a "gateway of last resort"
   (`ip route 0.0.0.0 0.0.0.0 <next hop>`) is where it sends packets for networks not in its
   routing table, usually towards the ISP.
