# Program 12: Security threats, network attacks, mitigation and device security

**Aim:** identify security threats and vulnerabilities, categorise network attacks, plan
mitigation, and secure individual devices. The manual's tasks are written analysis; the `.pkt`
puts the device-security and mitigation part into practice.

## Files

| File | What it is |
|---|---|
| `P12_Device_Security_ACL_SSH.pkt` | Hardened router and switch, with an ACL that blocks the guest LAN from the server |
| `configs/P12_Device_Security_ACL_SSH/` | R1, SW1, SW2 commands |
| `P12_Device_Security_ACL_SSH.results.md` | Addressing, cabling, expected pings |

```
                          R1 (2911)
         Gig0/0 /     Gig0/2 |       \ Gig0/1 (ACL 110 in)
   Staff 192.168.10.0/24    Server0         Guest 192.168.20.0/24
        SW1 (port-security)  192.168.30.100   SW2
   Staff-PC1 .10  Staff-PC2 .11  Admin-PC .20     Guest-PC .10
```

## Security applied (and why)

| Control | Command(s) | Stops |
|---|---|---|
| Encrypted enable password | `enable secret Str0ngEnable!` | Reading the privileged password from the config |
| Hide line passwords | `service password-encryption` | Shoulder-surfing `show run` |
| Console password | `line con 0` / `password Con$ole1` / `login` | Walk-up console access |
| Legal banner | `banner motd #Unauthorised access is prohibited#` | Gives legal grounds to act against intruders |
| SSH instead of telnet | `ip domain-name cnlab.local`, `username admin secret Adm1n@123`, `crypto key generate rsa general-keys modulus 1024`, `ip ssh version 2`, `line vty 0 4` / `login local` / `transport input ssh` | Sniffing telnet passwords in clear text |
| Only Admin-PC may manage R1 | `access-list 10 permit host 192.168.10.20`, `line vty 0 4` / `access-class 10 in` | Remote login attempts from any other host |
| Guest LAN can't reach the server | `access-list 110 deny ip 192.168.20.0 0.0.0.255 host 192.168.30.100`, `access-list 110 permit ip any any`, `interface Gig0/1` / `ip access-group 110 in` | Unauthorised access to and scanning of the server |
| Port security on staff ports | `switchport port-security` / `maximum 1` / `mac-address sticky` / `violation shutdown` | MAC flooding, rogue devices plugged into a staff port |

**One step after opening the file:** RSA keys can't be saved inside a .pkt, so on R1 run
```
R1(config)# crypto key generate rsa general-keys modulus 1024
R1(config)# ip ssh version 2
```
Then from Admin-PC, open Command Prompt and run `ssh -l admin 192.168.10.1` (password `Adm1n@123`).
The same command from Staff-PC1 is refused, because of the access-class.

## Tests (expected)

| Test | Result |
|---|---|
| Staff-PC1 / Admin-PC `ping 192.168.30.100` | reply |
| Guest-PC `ping 192.168.30.100` | "Destination host unreachable" (ACL 110) |
| Guest-PC `ping 192.168.10.10` | reply (only the server is protected) |
| `R1# show access-lists` | match counters go up on the deny line |
| Plug a new PC into SW1 Fa0/1 in place of Staff-PC1 and ping | port goes err-disabled; `SW1# show port-security interface fa0/1` shows the violation |
| `R1# show ip ssh`, `show ssh` | SSH v2 enabled, session from 192.168.10.20 |

## Analysis part (manual tasks 1–3)

**Threats vs vulnerabilities:** a *vulnerability* is a weakness (default password, unpatched
IOS, open telnet, flat network). A *threat* is something that can exploit it (attacker,
malware, insider). *Risk* = likelihood × impact. Assets here: the server data, the router and
switch configs, staff PCs.

| Attack | How it works | Mitigation |
|---|---|---|
| Reconnaissance (ping sweep, port scan) | map hosts and open ports | ACLs, firewall, IPS, disable unused services |
| Password / brute force | guess telnet/SSH passwords | strong `secret`, SSH, `login block-for`, AAA |
| Eavesdropping / sniffing | capture clear-text traffic | SSH/HTTPS/VPN encryption |
| MAC flooding | fill the switch CAM table so it floods like a hub | port security |
| DHCP spoofing / starvation | rogue DHCP server, exhaust the pool | DHCP snooping, port security |
| ARP spoofing (MitM) | fake ARP replies redirect traffic | Dynamic ARP Inspection |
| DoS / DDoS | flood a service until it stops | rate limiting, ACLs, ISP scrubbing, redundancy |
| Malware / phishing | user runs malicious code or gives credentials | antivirus, patching, training, email filtering |
| VLAN hopping | double tagging, DTP abuse | disable DTP (`switchport nonegotiate`), unused native VLAN |

**Mitigation plan:**
- Firewall and ACLs at the edge.
- IDS/IPS.
- Patch management.
- Least privilege.
- Network segmentation (VLANs).
- Encrypted management (SSH).
- Backups.
- Logging and monitoring (syslog/SNMP).
- An incident response plan: prepare → detect → contain → eradicate → recover → lessons learned.
- User training.

## Viva answers

1. **Main threats:** malware (viruses, worms, ransomware), phishing/social engineering,
   DoS/DDoS, man-in-the-middle/sniffing, password attacks, reconnaissance, insider threats,
   unpatched vulnerabilities.
2. **Vulnerability vs threat:** a vulnerability is a weakness in the system. A threat is a
   potential event or actor that can exploit it. Without a vulnerability a threat can't
   succeed; a vulnerability with no threat is low risk.
3. **DoS:** flooding a target (SYN flood, ICMP flood) so real users can't get service. DDoS
   uses many machines (a botnet). The impact is downtime, lost revenue, and sometimes cover
   for another attack.
4. **Mitigation strategies:** firewalls, ACLs, IPS, segmentation/VLANs, strong authentication
   (AAA, SSH, `enable secret`), port security, DHCP snooping, patching, encryption, monitoring.
5. **Protecting devices:**
   - change default credentials
   - strong encrypted passwords
   - disable unused services and ports (`shutdown`)
   - SSH only
   - banners
   - patch IOS and OS
   - antivirus and host firewall
   - encrypt sensitive data
   - restrict management by ACL
6. **User education:** most breaches start with people (phishing, weak passwords, plugged-in
   USB drives). Trained users recognise and report attacks.
7. **Incident response plan:** a ready, agreed procedure to detect, contain and recover
   quickly, which limits damage and downtime, keeps evidence, and improves defences afterwards.
8. **Tools:** Wireshark, Nmap, Snort/Suricata (IDS/IPS), firewalls (ASA, pfSense), SIEM
   (Splunk, ELK), vulnerability scanners (Nessus, OpenVAS), antivirus/EDR.
