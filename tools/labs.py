"""Every Packet Tracer lab in the CN Lab manual (CSE3131), as code.

Each function returns (Lab, folder, stem, expectations). An expectation is
(source host, destination IP, should_succeed); build.py checks every one with
netsim.py against the finished .pkt file.
"""

from pktgen import Lab

G0, G1, G2 = "GigabitEthernet0/0", "GigabitEthernet0/1", "GigabitEthernet0/2"
S0, S1 = "Serial0/0/0", "Serial0/0/1"
F0 = "FastEthernet0"


def fa(n):
    return "FastEthernet0/%d" % n


def all_pairs(hosts, ok=True):
    return [(a, ip, ok) for a in hosts for b, ip in hosts.items() if a != b]


# ------------------------------------------------------------------ P01

def p01():
    L = Lab("Program 1 - Packet Tracer device tour",
            "Router, switch, hub, PCs and a server, joined with every cable type "
            "(straight-through, cross-over, serial DCE). Every PC can ping every other PC "
            "and the server.")
    r1 = L.router("R1", 420, 120, ifaces={
        G0: {"ip": "192.168.1.1/24", "desc": "LAN-A"},
        S0: {"ip": "10.0.0.1/30", "clock": 64000, "desc": "WAN to R2"}},
        post=["ip route 192.168.2.0 255.255.255.0 10.0.0.2"])
    r2 = L.router("R2", 720, 120, ifaces={
        G0: {"ip": "192.168.2.1/24", "desc": "LAN-B"},
        S0: {"ip": "10.0.0.2/30", "desc": "WAN to R1"}},
        post=["ip route 192.168.1.0 255.255.255.0 10.0.0.1"])
    sw = L.switch("SW1", 300, 260)
    hub = L.hub("HUB1", 520, 260)
    pcs = {}
    for i, (x, dev, port) in enumerate([(160, sw, fa(1)), (300, sw, fa(2))]):
        p = L.pc("PC%d" % i, x, 400, ip="192.168.1.%d/24" % (10 + i), gw="192.168.1.1")
        L.link(p, F0, dev, port)
        pcs[p.name] = "192.168.1.%d" % (10 + i)
    for i, x in enumerate([460, 580]):
        p = L.pc("PC%d" % (i + 2), x, 400, ip="192.168.1.%d/24" % (20 + i), gw="192.168.1.1")
        L.link(p, F0, hub, "FastEthernet%d" % (i + 1))
        pcs[p.name] = "192.168.1.%d" % (20 + i)
    srv = L.server("Server0", 160, 260, ip="192.168.1.100/24", gw="192.168.1.1", dns="192.168.1.100",
                   dns_records={"www.cnlab.local": "192.168.1.100"})
    pcb = L.pc("PC4", 720, 300, ip="192.168.2.10/24", gw="192.168.2.1")
    L.link(r1, G0, sw, G1)
    L.link(srv, F0, sw, fa(10))
    L.link(hub, "FastEthernet0", sw, fa(24))
    L.link(r1, S0, r2, S0, dce=r1)
    L.link(r2, G0, pcb, F0)
    pcs.update({"Server0": "192.168.1.100", "PC4": "192.168.2.10"})
    L.note(300, 60, "LAN-A 192.168.1.0/24 (switch + hub)")
    L.note(720, 60, "LAN-B 192.168.2.0/24")
    L.note(570, 95, "Serial 10.0.0.0/30 (DCE at R1)")
    return L, "P01_Intro_PacketTracer_NetSim", "P01_Device_Tour", all_pairs(pcs)


# ------------------------------------------------------------------ P02

def p02():
    L = Lab("Program 2 - Network utility commands (practice network)",
            "Two LANs joined by two routers, plus a DNS server. Open any PC > Desktop > "
            "Command Prompt and try ping, tracert, ipconfig /all, arp -a, nslookup, netstat.")
    r1 = L.router("R1", 350, 150, ifaces={G0: {"ip": "192.168.1.1/24"}, G1: {"ip": "10.1.1.1/30"}},
                  post=["ip route 192.168.2.0 255.255.255.0 10.1.1.2"])
    r2 = L.router("R2", 650, 150, ifaces={G0: {"ip": "192.168.2.1/24"}, G1: {"ip": "10.1.1.2/30"}},
                  post=["ip route 192.168.1.0 255.255.255.0 10.1.1.1"])
    s1, s2 = L.switch("SW1", 350, 280), L.switch("SW2", 650, 280)
    L.link(r1, G1, r2, G1)
    L.link(r1, G0, s1, G1)
    L.link(r2, G0, s2, G1)
    hosts = {}
    for i, x in enumerate([250, 350]):
        p = L.pc("PC%d" % i, x, 420, ip="192.168.1.%d/24" % (10 + i), gw="192.168.1.1", dns="192.168.2.100")
        L.link(p, F0, s1, fa(i + 1))
        hosts[p.name] = "192.168.1.%d" % (10 + i)
    p = L.pc("PC2", 600, 420, ip="192.168.2.10/24", gw="192.168.2.1", dns="192.168.2.100")
    L.link(p, F0, s2, fa(1))
    hosts["PC2"] = "192.168.2.10"
    srv = L.server("DNS-Server", 740, 420, ip="192.168.2.100/24", gw="192.168.2.1", dns="192.168.2.100",
                   dns_records={"www.cnlab.local": "192.168.2.100", "pc0.cnlab.local": "192.168.1.10"})
    L.link(srv, F0, s2, fa(2))
    hosts["DNS-Server"] = "192.168.2.100"
    L.note(500, 115, "10.1.1.0/30")
    L.note(300, 470, "LAN 192.168.1.0/24")
    L.note(680, 470, "LAN 192.168.2.0/24  (DNS: www.cnlab.local)")
    return L, "P02_Network_Utility_Commands", "P02_Commands_Practice", all_pairs(hosts)


# ------------------------------------------------------------------ P03

def p03():
    L = Lab("Program 3 - Star topology with a switch and with a hub",
            "Left: switch star, 6 PCs in 192.168.1.0/24. Right: hub star, 4 PCs in 192.168.2.0/24. "
            "Switch has hostname, enable secret, console/vty passwords, banner, and the config is saved.")
    sw = L.switch("Switch0", 260, 200, secret="class", console="cisco", vty="cisco",
                  banner="Authorised access only - CN Lab")
    hub = L.hub("Hub0", 760, 200)
    sw_hosts, hub_hosts = {}, {}
    pos = [(110, 90), (260, 60), (410, 90), (110, 330), (260, 360), (410, 330)]
    for i, (x, y) in enumerate(pos):
        p = L.pc("PC%d" % i, x, y, ip="192.168.1.%d/24" % (i + 1))
        L.link(p, F0, sw, fa(i + 1))
        sw_hosts[p.name] = "192.168.1.%d" % (i + 1)
    pos = [(640, 90), (880, 90), (640, 330), (880, 330)]
    for i, (x, y) in enumerate(pos):
        p = L.pc("PC%d" % (i + 6), x, y, ip="192.168.2.%d/24" % (i + 1))
        L.link(p, F0, hub, "FastEthernet%d" % i)
        hub_hosts[p.name] = "192.168.2.%d" % (i + 1)
    L.note(260, 430, "SWITCH star - 192.168.1.0/24")
    L.note(760, 430, "HUB star - 192.168.2.0/24")
    exp = all_pairs(sw_hosts) + all_pairs(hub_hosts)
    exp += [("PC0", "192.168.2.1", False)]  # two separate LANs, no router between them
    return L, "P03_Star_Topology_Hub_Switch", "P03_Star_Hub_and_Switch", exp


# ------------------------------------------------------------------ P04

def p04():
    L = Lab("Program 4 - DHCP on a router",
            "Router0 is the DHCP server for 192.168.1.0/24 (pool MY_POOL, .1-.10 excluded). "
            "All PCs are set to DHCP and get .11, .12, ... automatically.")
    r = L.router("Router0", 500, 100, ifaces={G0: {"ip": "192.168.1.1/24", "desc": "LAN"}},
                 pre=["ip dhcp excluded-address 192.168.1.1 192.168.1.10",
                      "ip dhcp pool MY_POOL\n network 192.168.1.0 255.255.255.0\n"
                      " default-router 192.168.1.1\n dns-server 8.8.8.8"])
    sw = L.switch("Switch0", 500, 230)
    L.link(r, G0, sw, G1)
    names = []
    for i, x in enumerate([260, 420, 580, 740]):
        p = L.pc("PC%d" % i, x, 380, dhcp=True)
        L.link(p, F0, sw, fa(i + 1))
        names.append(p.name)
    L.note(500, 40, "DHCP server: pool MY_POOL 192.168.1.0/24, excluded .1-.10")
    exp = [(n, "192.168.1.1", True) for n in names]
    exp += [(names[0], "192.168.1.%d" % (12 + i), True) for i in range(3)]
    return L, "P04_DHCP_Configuration", "P04_DHCP_Router", exp


# ------------------------------------------------------------------ P05

def p05():
    L = Lab("Program 5 - Router modes and basic router/switch commands",
            "MyRouter (hostname, passwords, banner, interface IP) and MySwitch (hostname, "
            "VLAN 10 'Sales' on Fa0/1, Fa0/2 and the uplink).")
    r = L.router("MyRouter", 500, 100, secret="class", console="cisco", vty="cisco", encrypt=True,
                 banner="MyRouter - CN Lab Program 5",
                 ifaces={G0: {"ip": "192.168.1.1/24", "desc": "Link to MySwitch"}})
    sw = L.switch("MySwitch", 500, 240, secret="class", console="cisco", vty="cisco", encrypt=True,
                  vlans={10: "Sales"},
                  ports={fa(1): {"access": 10}, fa(2): {"access": 10},
                         fa(24): {"access": 10, "desc": "Uplink to MyRouter"}},
                  svi={}, gw=None)
    p0 = L.pc("PC0", 380, 380, ip="192.168.1.10/24", gw="192.168.1.1")
    p1 = L.pc("PC1", 620, 380, ip="192.168.1.11/24", gw="192.168.1.1")
    L.link(r, G0, sw, fa(24))
    L.link(p0, F0, sw, fa(1))
    L.link(p1, F0, sw, fa(2))
    L.note(500, 40, "enable secret: class | console/vty password: cisco")
    exp = [("PC0", "192.168.1.11", True), ("PC1", "192.168.1.10", True),
           ("PC0", "192.168.1.1", True), ("PC1", "192.168.1.1", True)]
    return L, "P05_Router_Modes_Basic_Commands", "P05_Router_Switch_Basics", exp


# ------------------------------------------------------------------ P06

def p06():
    L = Lab("Program 6 - Static routing",
            "Two routers joined by a serial link (11.0.0.0/8). Each router has one LAN. "
            "Each router has one static route to the other LAN.")
    r0 = L.router("Router0", 300, 100, ifaces={
        G0: {"ip": "192.168.1.1/24"}, S0: {"ip": "11.0.0.1/8", "clock": 64000}},
        post=["ip route 192.168.2.0 255.255.255.0 11.0.0.2"])
    r1 = L.router("Router1", 700, 100, ifaces={
        G0: {"ip": "192.168.2.1/24"}, S0: {"ip": "11.0.0.2/8"}},
        post=["ip route 192.168.1.0 255.255.255.0 11.0.0.1"])
    s0, s1 = L.switch("Switch0", 300, 230), L.switch("Switch1", 700, 230)
    L.link(r0, S0, r1, S0, dce=r0)
    L.link(r0, G0, s0, G1)
    L.link(r1, G0, s1, G1)
    hosts = {}
    for sw, net, xs, base in ((s0, 1, (220, 380), 0), (s1, 2, (620, 780), 2)):
        for j, x in enumerate(xs):
            p = L.pc("PC%d" % (base + j), x, 370, ip="192.168.%d.%d/24" % (net, j + 2), gw="192.168.%d.1" % net)
            L.link(p, F0, sw, fa(j + 1))
            hosts[p.name] = "192.168.%d.%d" % (net, j + 2)
    L.note(500, 70, "11.0.0.0/8 (serial, DCE = Router0)")
    L.note(300, 430, "192.168.1.0/24  gateway 192.168.1.1")
    L.note(700, 430, "192.168.2.0/24  gateway 192.168.2.1")
    return L, "P06_Static_Routing", "P06_Static_Routing", all_pairs(hosts)


# ------------------------------------------------------------------ P07

def _rip(version):
    v2 = version == 2
    lan0 = "192.168.1.1/16" if v2 else "192.168.1.1/24"
    pc0 = "192.168.1.2/16" if v2 else "192.168.1.2/24"

    def rip(*nets):
        body = "router rip\n" + (" version 2\n" if v2 else "")
        body += "\n".join(" network " + n for n in nets)
        if v2:
            body += "\n no auto-summary"
        return body
    L = Lab("Program 7 - RIP version %d" % version,
            "Four 2911 routers in a ring (manual figure 'RIP routing with multiple paths'). "
            "RIPv%d on every router. PC0, PC1 and PC2 can all ping each other." % version)
    r0 = L.router("Router0", 640, 360, ifaces={
        G0: {"ip": lan0, "desc": "PC0 LAN"}, G1: {"ip": "20.0.0.1/8"}, G2: {"ip": "30.0.0.1/8"}},
        post=[rip("192.168.1.0", "20.0.0.0", "30.0.0.0")])
    r1 = L.router("Router1", 300, 360, ifaces={G0: {"ip": "30.0.0.2/8"}, G1: {"ip": "40.0.0.1/8"}},
                  post=[rip("30.0.0.0", "40.0.0.0")])
    r2 = L.router("Router2", 300, 160, ifaces={
        G0: {"ip": "40.0.0.2/8"}, G1: {"ip": "50.0.0.1/8"}, G2: {"ip": "60.0.0.1/8", "desc": "PC1 LAN"}},
        post=[rip("40.0.0.0", "50.0.0.0", "60.0.0.0")])
    r3 = L.router("Router3", 640, 160, ifaces={
        G0: {"ip": "50.0.0.2/8"}, G1: {"ip": "20.0.0.2/8"}, G2: {"ip": "8.0.0.1/8", "desc": "PC2 LAN"}},
        post=[rip("50.0.0.0", "20.0.0.0", "8.0.0.0")])
    pc0 = L.pc("PC0", 860, 360, ip=pc0, gw="192.168.1.1")
    pc1 = L.pc("PC1", 100, 160, ip="60.0.0.2/8", gw="60.0.0.1")
    pc2 = L.pc("PC2", 640, 30, ip="8.0.0.2/8", gw="8.0.0.1")
    L.link(r0, G0, pc0, F0)
    L.link(r0, G1, r3, G1)
    L.link(r0, G2, r1, G0)
    L.link(r1, G1, r2, G0)
    L.link(r2, G1, r3, G0)
    L.link(r2, G2, pc1, F0)
    L.link(r3, G2, pc2, F0)
    for x, y, t in ((470, 390, "30.0.0.0/8"), (250, 260, "40.0.0.0/8"), (470, 130, "50.0.0.0/8"),
                    (690, 260, "20.0.0.0/8"), (190, 130, "60.0.0.0/8"), (690, 80, "8.0.0.0/8"),
                    (760, 400, "192.168.1.0/%s" % ("16" if v2 else "24"))):
        L.note(x, y, t)
    hosts = {"PC0": pc0.ip.split("/")[0], "PC1": "60.0.0.2", "PC2": "8.0.0.2"}
    return L, "P07_RIPv1_RIPv2", "P07%s_RIPv%d" % ("b" if v2 else "a", version), all_pairs(hosts)


def p07a():
    return _rip(1)


def p07b():
    return _rip(2)


# ------------------------------------------------------------------ P08

def p08a():
    L = Lab("Program 8 - OSPF (manual topology)",
            "R1 and R2 joined by a serial link 20.0.0.0/8; PC1 on 10.0.0.0/8, PC2 on 30.0.0.0/8. "
            "OSPF process 1, area 0 on both routers.")
    r1 = L.router("R1", 330, 120, ifaces={G0: {"ip": "10.0.0.1/8"}, S0: {"ip": "20.0.0.1/8", "clock": 64000}},
                  post=["router ospf 1\n log-adjacency-changes\n network 10.0.0.0 0.255.255.255 area 0\n"
                        " network 20.0.0.0 0.255.255.255 area 0"])
    r2 = L.router("R2", 670, 120, ifaces={G0: {"ip": "30.0.0.1/8"}, S0: {"ip": "20.0.0.2/8"}},
                  post=["router ospf 1\n log-adjacency-changes\n network 20.0.0.0 0.255.255.255 area 0\n"
                        " network 30.0.0.0 0.255.255.255 area 0"])
    p1 = L.pc("PC1", 180, 320, ip="10.0.0.2/8", gw="10.0.0.1")
    p2 = L.pc("PC2", 820, 320, ip="30.0.0.2/8", gw="30.0.0.1")
    L.link(r1, S0, r2, S0, dce=r1)
    L.link(r1, G0, p1, F0)
    L.link(r2, G0, p2, F0)
    L.note(500, 90, "N/W 20.0.0.0/8")
    L.note(220, 220, "N/W 10.0.0.0/8")
    L.note(780, 220, "N/W 30.0.0.0/8")
    return L, "P08_OSPF", "P08a_OSPF_Manual_2_Routers", all_pairs({"PC1": "10.0.0.2", "PC2": "30.0.0.2"})


def _ospf3(broken=False):
    title = "Program 8 - OSPF, 3 routers (YouTube tutorial topology)"
    if broken:
        title = "Program 8 - OSPF TROUBLESHOOTING (3 faults planted)"

    def ospf(*nets):
        return "router ospf 1\n log-adjacency-changes\n" + "\n".join(" network %s %s area %s" % n for n in nets)
    r0_nets = [("192.168.1.0", "0.0.0.255", "0"), ("10.0.0.0", "0.255.255.255", "0"), ("12.0.0.0", "0.255.255.255", "0")]
    r1_nets = [("192.168.2.0", "0.0.0.255", "0"), ("10.0.0.0", "0.255.255.255", "0"), ("11.0.0.0", "0.255.255.255", "0")]
    r2_nets = [("192.168.3.0", "0.0.0.255", "0"), ("11.0.0.0", "0.255.255.255", "0"), ("12.0.0.0", "0.255.255.255", "0")]
    pc5_gw = "192.168.3.1"
    if broken:
        r1_nets = r1_nets[1:]                                   # fault 1: R1 LAN not advertised
        r2_nets[2] = ("12.0.0.0", "0.255.255.255", "1")          # fault 2: area mismatch R0-R2
        pc5_gw = "192.168.3.100"                                  # fault 3: wrong gateway on PC5
    L = Lab(title, "R0, R1, R2 in a triangle of serial links (10/11/12.0.0.0/8); one switch and two PCs "
                   "per router; OSPF process 1 area 0." + (" Find and fix the 3 faults - see README." if broken else ""))
    r0 = L.router("R0", 300, 100, ifaces={G0: {"ip": "192.168.1.1/24"}, S0: {"ip": "10.0.0.1/8", "clock": 64000},
                                          S1: {"ip": "12.0.0.1/8", "clock": 64000}}, post=[ospf(*r0_nets)])
    r1 = L.router("R1", 700, 100, ifaces={G0: {"ip": "192.168.2.1/24"}, S0: {"ip": "10.0.0.2/8"},
                                          S1: {"ip": "11.0.0.1/8", "clock": 64000}}, post=[ospf(*r1_nets)])
    r2 = L.router("R2", 500, 300, ifaces={G0: {"ip": "192.168.3.1/24"}, S0: {"ip": "11.0.0.2/8"},
                                          S1: {"ip": "12.0.0.2/8"}}, post=[ospf(*r2_nets)])
    L.link(r0, S0, r1, S0, dce=r0)
    L.link(r1, S1, r2, S0, dce=r1)
    L.link(r0, S1, r2, S1, dce=r0)
    hosts = {}
    k = 0
    for r, net, (sx, sy) in ((r0, 1, (120, 220)), (r1, 2, (880, 220)), (r2, 3, (500, 450))):
        sw = L.switch("S%d" % (net - 1), sx, sy)
        L.link(r, G0, sw, fa(24))
        for j in range(2):
            gw = "192.168.%d.1" % net
            if broken and k == 5:
                gw = pc5_gw
            p = L.pc("PC%d" % k, sx - 70 + 140 * j, sy + 130, ip="192.168.%d.%d/24" % (net, 10 + k), gw=gw)
            L.link(p, F0, sw, fa(j + 1))
            hosts[p.name] = "192.168.%d.%d" % (net, 10 + k)
            k += 1
    L.note(500, 70, "10.0.0.0/8  (R0 Se0/0/0 - R1 Se0/0/0)")
    L.note(660, 210, "11.0.0.0/8  (R1 Se0/0/1 - R2 Se0/0/0)")
    L.note(330, 210, "12.0.0.0/8  (R0 Se0/0/1 - R2 Se0/0/1)")
    if not broken:
        return L, "P08_OSPF", "P08b_OSPF_3_Routers_Video", all_pairs(hosts)
    exp = [("PC0", "192.168.2.12", False),   # R1 LAN missing from OSPF
           ("PC5", "192.168.3.14", True),    # same LAN still fine
           ("PC5", "192.168.1.10", False),   # bad gateway
           ("PC0", "192.168.1.11", True)]
    return L, "P08_OSPF", "P08c_OSPF_Troubleshooting_BROKEN", exp


def p08b():
    return _ospf3(False)


def p08c():
    return _ospf3(True)


# ------------------------------------------------------------------ P09

def p09a():
    L = Lab("Program 9 - VLANs across two switches (manual topology)",
            "VLAN 10 STUDENT and VLAN 20 FACULTY on Switch0 and Switch1, trunk on Gig0/1. "
            "All 12 PCs are in 192.168.10.0/24, but only PCs in the same VLAN can talk.")
    vl = {10: "STUDENT", 20: "FACULTY"}
    plan = {"Switch0": [10, 10, 10, 10, 20, 20], "Switch1": [10, 10, 10, 20, 20, 20]}
    sws = {}
    for name, x in (("Switch0", 300), ("Switch1", 700)):
        ports = {fa(i + 1): {"access": v} for i, v in enumerate(plan[name])}
        ports[G1] = {"trunk": True}
        sws[name] = L.switch(name, x, 120, vlans=vl, ports=ports)
    L.link(sws["Switch0"], G1, sws["Switch1"], G1)
    hosts = {}
    vlan_of = {}
    n = 1
    for name, x0 in (("Switch0", 120), ("Switch1", 520)):
        for i, v in enumerate(plan[name]):
            p = L.pc("PC%d" % (n - 1), x0 + i * 72, 300 + (i % 2) * 70, ip="192.168.10.%d/24" % n)
            L.link(p, F0, sws[name], fa(i + 1))
            hosts[p.name] = "192.168.10.%d" % n
            vlan_of[p.name] = v
            n += 1
    L.note(300, 60, "LAN-A: VLAN 10 STUDENT Fa0/1-4, VLAN 20 FACULTY Fa0/5-6")
    L.note(700, 60, "LAN-B: VLAN 10 STUDENT Fa0/1-3, VLAN 20 FACULTY Fa0/4-6")
    L.note(500, 100, "trunk Gig0/1")
    exp = [(a, ip, vlan_of[a] == vlan_of[b]) for a in hosts for b, ip in hosts.items() if a != b]
    return L, "P09_VLAN", "P09a_VLAN_Two_Switches_Trunk", exp


def p09b():
    L = Lab("Program 9 - Inter-VLAN routing (router-on-a-stick)",
            "Same two switches, but each VLAN gets its own subnet and Router0 routes between them "
            "using sub-interfaces Gig0/0.10 and Gig0/0.20. Everyone can ping everyone.")
    vl = {10: "STUDENT", 20: "FACULTY"}
    r = L.router("Router0", 300, 60, ifaces={
        G0: {"desc": "trunk to Switch0"},
        G0 + ".10": {"vlan": 10, "ip": "192.168.10.1/24"},
        G0 + ".20": {"vlan": 20, "ip": "192.168.20.1/24"}})
    plan = {"Switch0": [10, 10, 20, 20], "Switch1": [10, 10, 20, 20]}
    sws = {}
    for name, x in (("Switch0", 300), ("Switch1", 700)):
        ports = {fa(i + 1): {"access": v} for i, v in enumerate(plan[name])}
        ports[G1] = {"trunk": True}
        if name == "Switch0":
            ports[G2] = {"trunk": True}
        sws[name] = L.switch(name, x, 180, vlans=vl, ports=ports)
    L.link(sws["Switch0"], G1, sws["Switch1"], G1)
    L.link(r, G0, sws["Switch0"], G2)
    hosts = {}
    k = 0
    for name, x0 in (("Switch0", 150), ("Switch1", 550)):
        cnt = {10: 10, 20: 10}
        for i, v in enumerate(plan[name]):
            cnt[v] += 1
            host = cnt[v] + (0 if name == "Switch0" else 10)
            ip = "192.168.%d.%d" % (v, host)
            p = L.pc("PC%d" % k, x0 + i * 100, 360, ip=ip + "/24", gw="192.168.%d.1" % v)
            L.link(p, F0, sws[name], fa(i + 1))
            hosts[p.name] = ip
            k += 1
    L.note(300, 20, "Gig0/0.10 = 192.168.10.1   Gig0/0.20 = 192.168.20.1")
    L.note(500, 420, "VLAN 10 STUDENT 192.168.10.0/24 | VLAN 20 FACULTY 192.168.20.0/24")
    return L, "P09_VLAN", "P09b_InterVLAN_Router_on_a_Stick", all_pairs(hosts)


# ------------------------------------------------------------------ P10

def _nat(kind):
    rules = {
        "static": ["ip nat inside source static 192.168.1.100 203.0.113.10",
                   "ip nat inside source static 192.168.1.10 203.0.113.11",
                   "ip nat inside source static 192.168.1.11 203.0.113.12",
                   "ip route 0.0.0.0 0.0.0.0 203.0.113.2"],
        "dynamic": ["ip nat pool PUBLIC_POOL 203.0.113.20 203.0.113.30 netmask 255.255.255.0",
                    "ip nat inside source list 1 pool PUBLIC_POOL",
                    "ip route 0.0.0.0 0.0.0.0 203.0.113.2",
                    "access-list 1 permit 192.168.1.0 0.0.0.255"],
        "pat": ["ip nat inside source list 1 interface Serial0/0/0 overload",
                "ip nat inside source static 192.168.1.100 203.0.113.10",
                "ip route 0.0.0.0 0.0.0.0 203.0.113.2",
                "access-list 1 permit 192.168.1.0 0.0.0.255"],
    }[kind]
    title = {"static": "Static NAT", "dynamic": "Dynamic NAT (pool)", "pat": "PAT / NAT overload"}[kind]
    L = Lab("Program 10 - " + title,
            "Inside LAN 192.168.1.0/24 behind R1. R1 translates to public 203.0.113.x before the "
            "ISP router. The ISP has no route to 192.168.x, so only translated traffic gets a reply.")
    r1 = L.router("R1", 420, 150, ifaces={
        G0: {"ip": "192.168.1.1/24", "nat": "inside", "desc": "Inside LAN"},
        S0: {"ip": "203.0.113.1/30", "nat": "outside", "clock": 64000, "desc": "To ISP"}}, post=rules)
    isp = L.router("ISP", 760, 150, ifaces={
        S0: {"ip": "203.0.113.2/30"}, G0: {"ip": "198.51.100.1/24", "desc": "Internet"}},
        post=["ip route 203.0.113.0 255.255.255.0 203.0.113.1"])
    sw = L.switch("Switch0", 420, 290)
    web = L.server("Internet-Server", 920, 290, ip="198.51.100.10/24", gw="198.51.100.1")
    L.link(r1, S0, isp, S0, dce=r1)
    L.link(r1, G0, sw, G1)
    L.link(isp, G0, web, F0)
    inside = {}
    for i, x in enumerate([260, 380, 500]):
        p = L.pc("PC%d" % i, x, 430, ip="192.168.1.%d/24" % (10 + i), gw="192.168.1.1")
        L.link(p, F0, sw, fa(i + 1))
        inside[p.name] = "192.168.1.%d" % (10 + i)
    srv = L.server("Web-Server", 620, 430, ip="192.168.1.100/24", gw="192.168.1.1")
    L.link(srv, F0, sw, fa(10))
    L.note(420, 80, "INSIDE (private) 192.168.1.0/24")
    L.note(590, 120, "203.0.113.0/30")
    L.note(860, 80, "OUTSIDE (Internet) 198.51.100.0/24")
    out = "198.51.100.10"
    exp = [("PC0", "192.168.1.11", True), ("PC0", "192.168.1.100", True)]
    exp += [("Internet-Server", "192.168.1.10", False)]   # private addresses are not routable
    if kind == "static":
        exp += [("PC0", out, True), ("PC1", out, True), ("PC2", out, False),   # PC2 has no mapping
                ("Web-Server", out, True), ("Internet-Server", "203.0.113.10", True)]
    elif kind == "dynamic":
        exp += [(n, out, True) for n in inside] + [("Web-Server", out, True)]
    else:
        exp += [(n, out, True) for n in inside] + [("Web-Server", out, True),
                                                   ("Internet-Server", "203.0.113.10", True)]
    stem = {"static": "P10a_Static_NAT", "dynamic": "P10b_Dynamic_NAT", "pat": "P10c_PAT_Overload"}[kind]
    return L, "P10_NAT", stem, exp


def p10a():
    return _nat("static")


def p10b():
    return _nat("dynamic")


def p10c():
    return _nat("pat")


# ------------------------------------------------------------------ P12

def p12():
    L = Lab("Program 12 - Device security and attack mitigation",
            "R1 hardened: enable secret, encrypted passwords, banner, SSH-only VTY limited to the "
            "Admin PC, and ACL 110 that blocks the Guest LAN from the server. SW1 uses port-security.")
    r1 = L.router("R1", 500, 100, secret="Str0ngEnable!", console="Con$ole1", encrypt=True,
                  banner="Unauthorised access is prohibited",
                  ssh={"domain": "cnlab.local", "user": "admin", "password": "Adm1n@123"}, vty_acl="10",
                  ifaces={G0: {"ip": "192.168.10.1/24", "desc": "Staff LAN"},
                          G1: {"ip": "192.168.20.1/24", "desc": "Guest LAN", "acl_in": "110"},
                          G2: {"ip": "192.168.30.1/24", "desc": "Server LAN"}},
                  post=["access-list 10 permit host 192.168.10.20",
                        "access-list 110 deny ip 192.168.20.0 0.0.0.255 host 192.168.30.100",
                        "access-list 110 permit ip any any"])
    ps = {"max": 1, "sticky": True, "violation": "shutdown"}
    sw1 = L.switch("SW1", 300, 240, secret="Str0ngEnable!", console="Con$ole1", encrypt=True,
                   ports={fa(1): {"access": 1, "portsec": ps}, fa(2): {"access": 1, "portsec": ps},
                          fa(3): {"access": 1, "portsec": ps}})
    sw2 = L.switch("SW2", 700, 240)
    srv = L.server("Server0", 500, 260, ip="192.168.30.100/24", gw="192.168.30.1")
    L.link(r1, G0, sw1, G1)
    L.link(r1, G1, sw2, G1)
    L.link(r1, G2, srv, F0)
    a = L.pc("Staff-PC1", 180, 400, ip="192.168.10.10/24", gw="192.168.10.1")
    b = L.pc("Staff-PC2", 300, 400, ip="192.168.10.11/24", gw="192.168.10.1")
    c = L.pc("Admin-PC", 420, 400, ip="192.168.10.20/24", gw="192.168.10.1")
    g = L.pc("Guest-PC", 700, 400, ip="192.168.20.10/24", gw="192.168.20.1")
    for i, p in enumerate((a, b, c)):
        L.link(p, F0, sw1, fa(i + 1))
    L.link(g, F0, sw2, fa(1))
    L.note(300, 460, "Staff 192.168.10.0/24 (port-security on Fa0/1-3)")
    L.note(700, 460, "Guest 192.168.20.0/24 (ACL 110 in on R1 Gig0/1)")
    L.note(500, 320, "Server 192.168.30.100")
    exp = [("Staff-PC1", "192.168.30.100", True), ("Admin-PC", "192.168.30.100", True),
           ("Guest-PC", "192.168.30.100", False), ("Guest-PC", "192.168.10.10", True),
           ("Staff-PC2", "192.168.20.10", True)]
    return L, "P12_Network_Security", "P12_Device_Security_ACL_SSH", exp


# ------------------------------------------------------------------ P13

def p13a():
    L = Lab("Program 13 - Case study, phase 1: small office",
            "One router (DHCP server + PAT to the ISP), one switch, two PCs. Both PCs get an "
            "address by DHCP, can share files with each other and reach the Internet server.")
    r1 = L.router("R1", 420, 140, ifaces={
        G0: {"ip": "192.168.1.1/24", "nat": "inside"},
        S0: {"ip": "203.0.113.1/30", "nat": "outside", "clock": 64000}},
        pre=["ip dhcp excluded-address 192.168.1.1 192.168.1.10",
             "ip dhcp pool OFFICE\n network 192.168.1.0 255.255.255.0\n default-router 192.168.1.1\n"
             " dns-server 198.51.100.10"],
        post=["ip nat inside source list 1 interface Serial0/0/0 overload",
              "ip route 0.0.0.0 0.0.0.0 203.0.113.2", "access-list 1 permit 192.168.1.0 0.0.0.255"])
    isp = L.router("ISP", 760, 140, ifaces={S0: {"ip": "203.0.113.2/30"}, G0: {"ip": "198.51.100.1/24"}})
    web = L.server("Internet-Server", 900, 290, ip="198.51.100.10/24", gw="198.51.100.1", dns="198.51.100.10",
                   dns_records={"www.example.com": "198.51.100.10"})
    sw = L.switch("SW1", 420, 280)
    L.link(r1, S0, isp, S0, dce=r1)
    L.link(isp, G0, web, F0)
    L.link(r1, G0, sw, G1)
    p0 = L.pc("PC0", 330, 420, dhcp=True)
    p1 = L.pc("PC1", 510, 420, dhcp=True)
    L.link(p0, F0, sw, fa(1))
    L.link(p1, F0, sw, fa(2))
    L.note(420, 480, "192.168.1.0/24 via DHCP (pool OFFICE)")
    exp = [("PC0", "192.168.1.12", True), ("PC1", "192.168.1.11", True),
           ("PC0", "198.51.100.10", True), ("PC1", "198.51.100.10", True)]
    return L, "P13_Case_Study_Scaling_Network", "P13a_Phase1_Small_Office", exp


def _p13b(broken=False):
    vl = {10: "SALES", 20: "HR", 99: "SERVERS"}
    pools = []
    for v, nm in ((10, "SALES"), (20, "HR")):
        pools += ["ip dhcp excluded-address 192.168.%d.1 192.168.%d.10" % (v, v),
                  "ip dhcp pool %s\n network 192.168.%d.0 255.255.255.0\n default-router 192.168.%d.1\n"
                  " dns-server 192.168.99.10" % (nm, v, v)]
    L = Lab("Program 13 - Case study, phase 2: scaled network" + (" (TROUBLESHOOTING copy)" if broken else ""),
            "Departments in VLANs (10 SALES, 20 HR, 99 SERVERS) with router-on-a-stick on R1, DHCP per "
            "VLAN, a file server, OSPF between R1 and backup router R2, PAT to a public pool, and a "
            "floating default route through R2 if R1's own ISP link fails.")
    r1 = L.router("R1", 420, 120, ifaces={
        G0: {"desc": "trunk to SW-Core"},
        G0 + ".10": {"vlan": 10, "ip": "192.168.10.1/24", "nat": "inside"},
        G0 + ".20": {"vlan": 20, "ip": "192.168.20.1/24", "nat": "inside"},
        G0 + ".99": {"vlan": 99, "ip": "192.168.99.1/24", "nat": "inside"},
        G1: {"ip": "10.0.12.1/30", "nat": "outside", "desc": "to backup router R2"},
        S0: {"ip": "203.0.113.1/30", "nat": "outside", "clock": 64000, "desc": "primary ISP link"}},
        pre=pools,
        post=["router ospf 1\n log-adjacency-changes\n network 10.0.12.0 0.0.0.3 area 0\n"
              " network 192.168.10.0 0.0.0.255 area 0\n network 192.168.20.0 0.0.0.255 area 0\n"
              " network 192.168.99.0 0.0.0.255 area 0",
              "ip nat pool PUBLIC 203.0.113.65 203.0.113.70 netmask 255.255.255.248",
              "ip nat inside source list 1 pool PUBLIC overload",
              "ip route 0.0.0.0 0.0.0.0 203.0.113.2",
              "ip route 0.0.0.0 0.0.0.0 10.0.12.2 5",
              "access-list 1 permit 192.168.0.0 0.0.255.255"])
    r2 = L.router("R2", 420, 20, ifaces={
        G0: {"ip": "10.0.12.2/30", "desc": "to R1"},
        S0: {"ip": "203.0.113.5/30", "clock": 64000, "desc": "backup ISP link"}},
        post=["router ospf 1\n log-adjacency-changes\n network 10.0.12.0 0.0.0.3 area 0",
              "ip route 0.0.0.0 0.0.0.0 203.0.113.6",
              "ip route 203.0.113.64 255.255.255.248 10.0.12.1"])
    isp = L.router("ISP", 780, 70, ifaces={
        S0: {"ip": "203.0.113.2/30"}, S1: {"ip": "203.0.113.6/30"}, G0: {"ip": "198.51.100.1/24"}},
        post=["ip route 203.0.113.64 255.255.255.248 203.0.113.1",
              "ip route 203.0.113.64 255.255.255.248 203.0.113.5 10"])
    web = L.server("Internet-Server", 950, 200, ip="198.51.100.10/24", gw="198.51.100.1")
    core = L.switch("SW-Core", 420, 240, vlans=vl, ports={
        G1: {"trunk": True}, fa(1): {"trunk": True}, fa(2): {"trunk": True}, fa(10): {"access": 99}})
    sales_ports = {fa(24): {"trunk": True}}
    hr_ports = {fa(24): {"trunk": True}}
    for i in range(3):
        sales_ports[fa(i + 1)] = {"access": 10}
        hr_ports[fa(i + 1)] = {"access": 20}
    if broken:
        hr_ports[fa(3)] = {"access": 10}                       # fault: HR-PC3 put in the SALES VLAN
    sw_s = L.switch("SW-Sales", 200, 360, vlans=vl, ports=sales_ports)
    sw_h = L.switch("SW-HR", 640, 360, vlans=vl, ports=hr_ports)
    fs = L.server("File-Server", 420, 380, ip="192.168.99.10/24", gw="192.168.99.1", dns="192.168.99.10",
                  dns_records={"files.company.local": "192.168.99.10", "www.example.com": "198.51.100.10"})
    L.link(r1, S0, isp, S0, dce=r1)
    L.link(r2, S0, isp, S1, dce=r2)
    L.link(r1, G1, r2, G0)
    L.link(isp, G0, web, F0)
    L.link(r1, G0, core, G1)
    L.link(core, fa(1), sw_s, fa(24))
    L.link(core, fa(2), sw_h, fa(24))
    L.link(fs, F0, core, fa(10))
    for i in range(3):
        p = L.pc("Sales-PC%d" % (i + 1), 90 + i * 110, 500, dhcp=True)
        L.link(p, F0, sw_s, fa(i + 1))
    for i in range(3):
        if broken and i == 1:
            p = L.pc("HR-PC%d" % (i + 1), 530 + i * 110, 500, ip="192.168.20.11/24", gw="192.168.20.1")
        else:
            p = L.pc("HR-PC%d" % (i + 1), 530 + i * 110, 500, dhcp=True)
        L.link(p, F0, sw_h, fa(i + 1))
    L.note(200, 560, "VLAN 10 SALES 192.168.10.0/24 (DHCP)")
    L.note(640, 560, "VLAN 20 HR 192.168.20.0/24 (DHCP)")
    L.note(420, 430, "VLAN 99 SERVERS 192.168.99.0/24")
    L.note(600, 30, "primary 203.0.113.0/30 | backup 203.0.113.4/30")
    if not broken:
        exp = [("Sales-PC1", "192.168.99.10", True), ("HR-PC1", "192.168.99.10", True),
               ("Sales-PC1", "192.168.20.11", True), ("HR-PC3", "192.168.10.11", True),
               ("Sales-PC2", "198.51.100.10", True), ("HR-PC2", "198.51.100.10", True),
               ("File-Server", "198.51.100.10", True), ("Internet-Server", "192.168.99.10", False)]
        return L, "P13_Case_Study_Scaling_Network", "P13b_Phase2_Scaled_Network", exp
    exp = [("HR-PC3", "192.168.99.10", True),       # works, but from the wrong VLAN/subnet
           ("HR-PC1", "192.168.99.10", True),
           ("Sales-PC1", "192.168.99.10", True)]
    return L, "P13_Case_Study_Scaling_Network", "P13c_Phase3_Troubleshooting_BROKEN", exp


def p13b():
    return _p13b(False)


def p13c():
    return _p13b(True)


ALL = [p01, p02, p03, p04, p05, p06, p07a, p07b, p08a, p08b, p08c, p09a, p09b,
       p10a, p10b, p10c, p12, p13a, p13b, p13c]
