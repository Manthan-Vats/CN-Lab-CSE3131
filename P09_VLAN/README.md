# Program 9: VLAN configuration and troubleshooting

**Aim:** configure VLANs on switches, assign ports to them, verify the segmentation, and
troubleshoot VLAN problems.

## Files

| File | What it is |
|---|---|
| `P09a_VLAN_Two_Switches_Trunk.pkt` | Manual figure (page 33): Switch0 and Switch1, VLAN 10 STUDENT and VLAN 20 FACULTY, trunk, 12 PCs in 192.168.10.0/24 |
| `P09b_InterVLAN_Router_on_a_Stick.pkt` | Viva Q3: the same switches, each VLAN its own subnet, Router0 routes between them |
| `configs/<file>/<device>.txt` | Commands |
| `<file>.results.md` | Addressing, cabling, all expected pings (132 in P09a, 56 in P09b) |

## P09a: VLANs and a trunk

```
          LAN-A  Switch0  Gig0/1 ======= trunk ======= Gig0/1  Switch1  LAN-B
   Fa0/1-4 VLAN 10 STUDENT: PC0-PC3 (.1-.4)      Fa0/1-3 VLAN 10 STUDENT: PC6-PC8 (.7-.9)
   Fa0/5-6 VLAN 20 FACULTY: PC4-PC5 (.5-.6)      Fa0/4-6 VLAN 20 FACULTY: PC9-PC11 (.10-.12)
   all PCs 192.168.10.x / 255.255.255.0
```
```
Switch0(config)# vlan 10
Switch0(config-vlan)# name STUDENT
Switch0(config)# vlan 20
Switch0(config-vlan)# name FACULTY
Switch0(config)# interface range FastEthernet0/1 - 4
Switch0(config-if-range)# switchport mode access
Switch0(config-if-range)# switchport access vlan 10
Switch0(config)# interface range FastEthernet0/5 - 6
Switch0(config-if-range)# switchport mode access
Switch0(config-if-range)# switchport access vlan 20
Switch0(config)# interface GigabitEthernet0/1
Switch0(config-if)# switchport mode trunk
```
Switch1 is the same, with STUDENT on Fa0/1–3 and FACULTY on Fa0/4–6. The switches are joined with a **cross-over** cable.

**Result:** STUDENT PCs ping each other across both switches, and so do FACULTY PCs.
**STUDENT ↔ FACULTY fails**, even though all PCs are in the same IP subnet. Each VLAN is a
separate broadcast domain, so the ARP request never reaches the other VLAN. That's the point
of the experiment.

## P09b: inter-VLAN routing (router-on-a-stick)

```
                     Router0  Gig0/0.10 = 192.168.10.1  (dot1Q 10)
                        |     Gig0/0.20 = 192.168.20.1  (dot1Q 20)
                     trunk
          Switch0 Gig0/2 ... Gig0/1 ==trunk== Gig0/1 Switch1
     VLAN 10: 192.168.10.0/24, gateway .1     VLAN 20: 192.168.20.0/24, gateway .1
```
```
Router0(config)# interface GigabitEthernet0/0
Router0(config-if)# no shutdown
Router0(config)# interface GigabitEthernet0/0.10
Router0(config-subif)# encapsulation dot1Q 10
Router0(config-subif)# ip address 192.168.10.1 255.255.255.0
Router0(config)# interface GigabitEthernet0/0.20
Router0(config-subif)# encapsulation dot1Q 20
Router0(config-subif)# ip address 192.168.20.1 255.255.255.0
Switch0(config)# interface GigabitEthernet0/2
Switch0(config-if)# switchport mode trunk
```
Now every PC pings every PC. A cross-VLAN ping goes PC → switch → trunk (tagged) → router
sub-interface → back down the trunk with the other tag.

## Verification

```
Switch0# show vlan brief                 ! 10 STUDENT Fa0/1-4, 20 FACULTY Fa0/5-6
Switch0# show interfaces trunk           ! Gig0/1 trunking, native 1, allowed 1-4094
Switch0# show interfaces fa0/1 switchport
Switch0# show mac address-table
Router0# show ip interface brief         ! Gig0/0.10 and Gig0/0.20 up/up
Router0# show vlans                      ! (router) sub-interfaces per VLAN
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| PC can't reach others in its own VLAN on the other switch | uplink is an access port, not a trunk | `switchport mode trunk` on both ends |
| One PC is isolated | its port is in the wrong VLAN | `switchport access vlan <n>` |
| Port is inactive | the VLAN doesn't exist on that switch | create it with `vlan <n>` |
| Inter-VLAN fails | wrong `encapsulation dot1Q` tag, wrong PC gateway, or router port shut | check `show run` on the router and the PC IP config |
| Native VLAN mismatch messages | different native VLANs at the two trunk ends | make them the same |

## Viva answers

1. **How a switch handles VLAN traffic:** each port belongs to a VLAN, and frames are forwarded
   or flooded only to ports in the same VLAN (separate MAC table space and broadcast domain per
   VLAN). Frames leaving on a trunk get an 802.1Q tag with the VLAN ID.
2. **Access port vs trunk port:** an access port carries one VLAN, untagged, and connects end
   devices. A trunk port carries many VLANs, tagged with 802.1Q (except the native VLAN), and
   connects switch↔switch or switch↔router.
3. **Inter-VLAN routing:** three ways.
   - Router-on-a-stick: one trunk link plus sub-interfaces with `encapsulation dot1Q`, as in P09b.
   - One physical router port per VLAN.
   - A Layer-3 switch with SVIs (`interface vlan 10`, `ip routing`).
4. **Verify VLANs:** `show vlan brief` (also `show vlan`, `show interfaces trunk`,
   `show interfaces <port> switchport`).
5. **Why trunking between switches:** without a trunk you'd need a separate cable per VLAN. A
   trunk carries all VLANs on one link and keeps them apart with tags.
6. **Tagged vs untagged:** tagged frames carry a 4-byte 802.1Q header (TPID 0x8100, 3-bit
   priority, 12-bit VLAN ID) on trunks. Untagged frames are normal Ethernet frames on access
   ports, plus the native VLAN on a trunk.
