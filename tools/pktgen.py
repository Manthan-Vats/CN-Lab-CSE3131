"""Build Packet Tracer .pkt files from a short Python description of a lab.

Every device is cloned from a template that a real Packet Tracer 8.2.1 saved
(see make_templates.py), so all the fields PT expects are present. Per device we
change only what must be unique or lab-specific: name, save-ref-id, MAC
addresses, serial number, canvas position, physical-workspace node, the
running/startup config, port IP fields and (switches) the VLAN database.

Packet Tracer rebuilds a router/switch by replaying its saved running-config
(OSPF, RIP, NAT, sub-interfaces exist nowhere else in a saved file), so the
config text below is the source of truth; the port fields are kept consistent
with it.

The same description also produces the paste-into-CLI scripts in configs/.
"""

import copy
import ipaddress
import os
import random
import uuid as uuidlib
import xml.etree.ElementTree as ET

import ptfile

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "templates")

# Physical interface names in the order the template stores its <PORT> elements.
PORTS = {
    "router2911": ["Serial0/0/0", "Serial0/0/1",
                   "GigabitEthernet0/0", "GigabitEthernet0/1", "GigabitEthernet0/2"],
    "switch2960": ["FastEthernet0/%d" % i for i in range(1, 25)]
                  + ["GigabitEthernet0/1", "GigabitEthernet0/2"],
    "pc": ["FastEthernet0", "Bluetooth"],
    "server": ["FastEthernet0"],
    "hub": ["FastEthernet%d" % i for i in range(6)],
}
OUIS = ["0001", "0002", "0003", "0004", "0005", "0006", "0007", "0009", "000A",
        "000B", "000C", "000D", "0010", "0030", "0040", "0050", "0060", "0090",
        "00D0", "00E0"]


def _mask(cidr):
    """'192.168.1.1/24' -> ('192.168.1.1', '255.255.255.0', IPv4Interface)."""
    itf = ipaddress.IPv4Interface(cidr)
    return str(itf.ip), str(itf.netmask), itf


def _eui64_ll(mac):
    h = mac.replace(".", "")
    b = [int(h[i:i + 2], 16) for i in range(0, 12, 2)]
    b[0] ^= 0x02
    words = [(b[0] << 8) | b[1], (b[2] << 8) | 0xFF, 0xFE00 | b[3], (b[4] << 8) | b[5]]
    return "FE80::" + ":".join("%X" % w for w in words)


def _set(el, tag, value):
    x = el.find(tag)
    if x is not None:
        x.text = value
    return x


# ---------------------------------------------------------------- devices

class Device:
    kind = None

    def __init__(self, lab, name, x, y):
        self.lab, self.name, self.x, self.y = lab, name, x, y
        self.ref = "save-ref-id:%d" % lab.rng.getrandbits(63)
        self.dev_addr = lab.rng.randrange(10 ** 11, 10 ** 12)
        self.mem_addr = lab.rng.randrange(10 ** 9, 2 * 10 ** 9)
        self.used = {}

    def port(self, name):
        if name not in PORTS[self.kind]:
            raise ValueError("%s (%s) has no port %s" % (self.name, self.kind, name))
        if name in self.used:
            raise ValueError("%s %s already cabled" % (self.name, name))
        return name

    # -- XML
    def to_xml(self, skel):
        tpl = ET.parse(os.path.join(TPL, self.kind + ".xml")).getroot()
        dev, node = copy.deepcopy(tpl[0]), copy.deepcopy(tpl[1])
        eng = dev.find("ENGINE")
        rng = self.lab.rng
        _set(eng, "NAME", self.name)
        _set(eng, "SAVE_REF_ID", self.ref)
        sn = eng.find("SERIALNUMBER")
        if sn is not None:
            sn.text = "PTT0810%04X-" % rng.getrandbits(16)
        duid = eng.find("DHCPV6_MAIN/PARTIAL_DUID")
        if duid is not None:
            duid.text = "%02X-%02X-%02X-%02X-" % tuple(rng.getrandbits(8) for _ in range(4))
        # fresh MACs for every port
        self.macs = {}
        for i, p in enumerate(self._ports(eng)):
            mac = "%s.%04X.%04X" % (rng.choice(OUIS), rng.getrandbits(16), rng.getrandbits(16))
            _set(p, "MACADDRESS", mac)
            _set(p, "BIA", mac)
            ll = p.find("IPV6_DEFAULT_LINK_LOCAL")
            if ll is not None and ll.text:
                ll.text = _eui64_ll(mac)
            if i < len(PORTS[self.kind]):
                self.macs[PORTS[self.kind][i]] = mac
        bia = eng.find("BUILD_IN_ADDR")
        if bia is not None:
            bia.text = "%s.%04X.%04X" % (rng.choice(OUIS), rng.getrandbits(16), rng.getrandbits(16))
        # logical workspace
        lg = dev.find("WORKSPACE/LOGICAL")
        _set(lg, "X", "%g" % self.x)
        _set(lg, "Y", "%g" % self.y)
        _set(lg, "MEM_ADDR", str(self.mem_addr))
        _set(lg, "DEV_ADDR", str(self.dev_addr))
        # physical workspace: rack devices go in the Rack, hosts on the office floor
        ws = dev.find("WORKSPACE")
        in_rack = len(ws.findtext("PHYSICAL").split(",")) == 6
        parent = skel.rack if in_rack else skel.office
        new_uuid = "{%s}" % uuidlib.UUID(int=rng.getrandbits(128), version=4)
        _set(ws, "PHYSICAL", ",".join(skel.path(parent) + [new_uuid]))
        cpur = ws.find("PHYSICAL_CPUR")
        _set(cpur, "PARENT_PATH", ",".join(skel.path(parent)[:-1]))
        _set(cpur, "CONTAINER_ID", parent.findtext("UUID_STR"))
        slot = skel.next_slot(in_rack)
        if in_rack:
            _set(cpur, "X", str(slot * 7))
            _set(node, "X", str(slot * 7))
        else:
            _set(cpur, "X", str(60 + (slot % 12) * 80))
            _set(cpur, "Y", str(215 + (slot // 12) * 120))
            _set(node, "X", str(60 + (slot % 12) * 80))
            _set(node, "Y", str(215 + (slot // 12) * 120))
        _set(node, "NAME", self.name)
        _set(node, "UUID_STR", new_uuid)
        parent.find("CHILDREN").append(node)
        self.customize(eng)
        return dev

    @staticmethod
    def _ports(eng):
        return [p for p in eng.iter("PORT") if p.find("TYPE") is not None
                and p.find("MACADDRESS") is not None and p.findtext("TYPE") != "eBluetooth"] + \
               [p for p in eng.iter("PORT") if p.findtext("TYPE") == "eBluetooth"]

    def customize(self, eng):
        pass

    def port_el(self, eng, name):
        return self._ports(eng)[PORTS[self.kind].index(name)]


def _config_lines(eng, text):
    for tag in ("RUNNINGCONFIG", "STARTUPCONFIG"):
        el = eng.find(tag)
        for c in list(el):
            el.remove(c)
        for line in text.split("\n"):
            ET.SubElement(el, "LINE").text = line


class Host(Device):
    """PC-PT / Server-PT. ip='192.168.1.2/24' or dhcp=True."""

    def __init__(self, lab, name, x, y, ip=None, gw="", dns="", dhcp=False):
        super().__init__(lab, name, x, y)
        self.ip, self.gw, self.dns, self.dhcp = ip, gw, dns, dhcp

    def customize(self, eng):
        p = self.port_el(eng, "FastEthernet0")
        if self.dhcp:
            ip = mask = gw = ""
        else:
            ip, mask, _ = _mask(self.ip)
            gw = self.gw
        _set(p, "IP", ip)
        _set(p, "SUBNET", mask)
        _set(p, "PORT_GATEWAY", gw)
        _set(p, "PORT_DNS", self.dns)
        _set(p, "PORT_DHCP_ENABLE", "true" if self.dhcp else "false")
        _set(eng, "GATEWAY", gw)
        dns = eng.find("DNS_CLIENT/SERVER_IP")
        if dns is not None:
            dns.text = self.dns
        dc = eng.find("DHCP_CLIENT/PORT_DATA_MAP")
        if dc is not None:
            for c in list(dc):
                dc.remove(c)
            ent = ET.SubElement(dc, "PORT_DATA_ENTRY")
            ET.SubElement(ent, "PORT").text = "FastEthernet0" if self.dhcp else "Bluetooth"

    def ip_table_row(self):
        if self.dhcp:
            return [self.name, "DHCP", "(from DHCP)", "(from DHCP)", "(from DHCP)"]
        ip, mask, _ = _mask(self.ip)
        return [self.name, ip, mask, self.gw or "-", self.dns or "-"]


class PC(Host):
    kind = "pc"


class Server(Host):
    kind = "server"

    def __init__(self, lab, name, x, y, dns_records=None, **kw):
        super().__init__(lab, name, x, y, **kw)
        self.dns_records = dns_records or {}

    def customize(self, eng):
        super().customize(eng)
        d = eng.find("DNS_SERVER")
        _set(d, "ENABLED", "1" if self.dns_records else "0")
        db = d.find("NAMESERVER-DATABASE")
        for c in list(db):
            db.remove(c)
        for host, ip in self.dns_records.items():
            rr = ET.SubElement(db, "RESOURCE-RECORD")
            ET.SubElement(rr, "TYPE").text = "A-REC"
            ET.SubElement(rr, "NAME").text = host
            ET.SubElement(rr, "TTL").text = "86400"
            ET.SubElement(rr, "IPADDRESS").text = ip


class Hub(Device):
    kind = "hub"


class IOSDevice(Device):
    """Shared bits of router and switch configs."""

    def __init__(self, lab, name, x, y, secret=None, console=None, vty=None,
                 encrypt=False, banner=None):
        super().__init__(lab, name, x, y)
        self.secret, self.console, self.vty = secret, console, vty
        self.encrypt, self.banner = encrypt, banner

    def _head(self, version):
        out = ["!", "version " + version,
               "no service timestamps log datetime msec",
               "no service timestamps debug datetime msec",
               ("service password-encryption" if self.encrypt else "no service password-encryption"),
               "!", "hostname " + self.name, "!"]
        if self.secret:
            out += ["enable secret " + self.secret, "!"]
        return out

    def _lines(self, aux=True, vty_extra=None):
        out = []
        if self.banner:
            out += ["banner motd ^C" + self.banner + "^C", "!"]
        out += ["line con 0"]
        if self.console:
            out += [" password " + self.console, " login"]
        out += ["!"]
        if aux:
            out += ["line aux 0", "!"]
        out += ["line vty 0 4"] + (vty_extra or ([" password " + self.vty, " login"] if self.vty else [" login"]))
        return out

    def _script_security(self):
        s = []
        if self.secret:
            s += ["enable secret " + self.secret]
        if self.console:
            s += ["line console 0", " password " + self.console, " login", " exit"]
        if self.vty:
            s += ["line vty 0 4", " password " + self.vty, " login", " exit"]
        if self.encrypt:
            s += ["service password-encryption"]
        if self.banner:
            s += ["banner motd #" + self.banner + "#"]
        return s


class Router(IOSDevice):
    """Cisco 2911 with an HWIC-2T card: Gig0/0-0/2, Serial0/0/0-0/0/1.

    ifaces: {name: {ip:'a.b.c.d/nn', desc, nat:'inside'|'outside', helper, clock,
                    shutdown, vlan (sub-interfaces only)}}
    pre:    global blocks shown before the interfaces (DHCP pools, excluded ranges)
    post:   global blocks after the interfaces (routing protocols, NAT, routes, ACLs)
    A block is a string; lines after the first that start with a space are sub-commands.
    """
    kind = "router2911"

    def __init__(self, lab, name, x, y, ifaces=None, pre=(), post=(), ssh=None, vty_acl=None, **kw):
        super().__init__(lab, name, x, y, **kw)
        self.ifaces = ifaces or {}
        self.pre, self.post, self.ssh, self.vty_acl = list(pre), list(post), ssh, vty_acl
        for n in self.ifaces:
            base = n.split(".")[0]
            if base not in PORTS[self.kind]:
                raise ValueError("%s: unknown interface %s" % (name, n))

    def _iface_block(self, n, c):
        sub = "." in n
        out = ["interface " + n]
        if c.get("desc"):
            out.append(" description " + c["desc"])
        if sub:
            out.append(" encapsulation dot1Q %d" % c["vlan"])
        if c.get("ip"):
            ip, mask, _ = _mask(c["ip"])
            out.append(" ip address %s %s" % (ip, mask))
        else:
            out.append(" no ip address")
        if c.get("helper"):
            out.append(" ip helper-address " + c["helper"])
        if c.get("nat"):
            out.append(" ip nat " + c["nat"])
        if c.get("acl_in"):
            out.append(" ip access-group %s in" % c["acl_in"])
        if c.get("acl_out"):
            out.append(" ip access-group %s out" % c["acl_out"])
        if n.startswith("Gig") and not sub:
            out += [" duplex auto", " speed auto"]
        if n.startswith("Serial"):
            out.append(" clock rate %d" % c.get("clock", 2000000))
        if c.get("shutdown"):
            out.append(" shutdown")
        return out

    def running_config(self):
        out = self._head("15.1")
        for b in self.pre:
            out += b.split("\n") + ["!"]
        out += ["!", "!", "ip cef", "no ipv6 cef", "!"]
        if self.ssh:
            out += ["username %s secret %s" % (self.ssh["user"], self.ssh["password"]), "!"]
        out += ["!", "license udi pid CISCO2911/K9 sn FTX1524%04X-" % self.lab.rng.getrandbits(16), "!", "!"]
        if self.ssh:
            out += ["ip domain-name " + self.ssh["domain"], "!"]
        out += ["spanning-tree mode pvst", "!"]
        names = list(PORTS[self.kind][2:]) + list(PORTS[self.kind][:2])  # Gig first, like IOS
        for n in names:
            c = self.ifaces.get(n)
            if c is None:
                c = {"shutdown": True}
                if n.startswith("Serial"):
                    c["clock"] = 2000000
            out += self._iface_block(n, c) + ["!"]
            for s in sorted(k for k in self.ifaces if k.startswith(n + ".")):
                out += self._iface_block(s, self.ifaces[s]) + ["!"]
        out += ["interface Vlan1", " no ip address", " shutdown", "!"]
        for b in self.post:
            out += b.split("\n") + ["!"]
        out += ["ip classless", "!", "ip flow-export version 9", "!"]
        vty = None
        if self.ssh:
            vty = [" login local", " transport input ssh"]
        if self.vty_acl:
            vty = [" access-class %s in" % self.vty_acl] + (vty or [" password " + self.vty, " login"])
        out += self._lines(vty_extra=vty) + ["!", "!", "!", "end"]
        return "\n".join(out)

    def script(self):
        s = ["enable", "configure terminal", "hostname " + self.name]
        s += self._script_security()
        for b in self.pre:
            s += b.split("\n")
            if "\n" in b:
                s.append(" exit")
        for n, c in self.ifaces.items():
            if c.get("shutdown"):
                continue
            blk = [l for l in self._iface_block(n, c)
                   if l not in (" duplex auto", " speed auto", " no ip address")]
            if n.startswith("Serial") and "clock" not in c:
                blk = [l for l in blk if not l.startswith(" clock rate")]
            if "." not in n:
                blk.append(" no shutdown")
            s += blk + [" exit"]
        for b in self.post:
            s += b.split("\n")
            if "\n" in b:
                s.append(" exit")
        if self.ssh:
            s += ["ip domain-name " + self.ssh["domain"],
                  "username %s secret %s" % (self.ssh["user"], self.ssh["password"]),
                  "crypto key generate rsa general-keys modulus 1024",
                  "ip ssh version 2",
                  "line vty 0 4"] + ([" access-class %s in" % self.vty_acl] if self.vty_acl else []) + [
                  " login local", " transport input ssh", " exit"]
        elif self.vty_acl:
            s += ["line vty 0 4", " access-class %s in" % self.vty_acl, " exit"]
        s += ["end", "write memory"]
        return "\n".join(s)

    def customize(self, eng):
        _set(eng, "SYS_NAME", self.name)
        _config_lines(eng, self.running_config())
        for n in PORTS[self.kind]:
            p = self.port_el(eng, n)
            c = self.ifaces.get(n)
            up = c is not None and not c.get("shutdown")
            _set(p, "POWER", "true" if up else "false")
            _set(p, "UP_METHOD", "3" if up else "5")
            if c and c.get("ip"):
                ip, mask, _ = _mask(c["ip"])
            else:
                ip = mask = ""
            _set(p, "IP", ip)
            _set(p, "SUBNET", mask)
            _set(p, "DESCRIPTION", (c or {}).get("desc", ""))
            if n.startswith("Serial"):
                _set(p, "CLOCKRATE", str((c or {}).get("clock", 2000000)))


class Switch(IOSDevice):
    """Cisco 2960-24TT.

    vlans: {10: 'STUDENT'}; ports: {name: {access: 10 | trunk: True, allowed, native,
    desc, shutdown, portsec: {max, violation, sticky}}}; svi: {1: 'ip/len'}; gw: default-gateway
    """
    kind = "switch2960"

    def __init__(self, lab, name, x, y, vlans=None, ports=None, svi=None, gw=None, **kw):
        super().__init__(lab, name, x, y, **kw)
        self.vlans, self.ports = vlans or {}, ports or {}
        self.svi, self.gw = svi or {}, gw
        for n in self.ports:
            if n not in PORTS[self.kind]:
                raise ValueError("%s: unknown port %s" % (name, n))

    def _port_block(self, c):
        out = []
        if c.get("desc"):
            out.append(" description " + c["desc"])
        if c.get("trunk"):
            if c.get("native"):
                out.append(" switchport trunk native vlan %d" % c["native"])
            if c.get("allowed"):
                out.append(" switchport trunk allowed vlan " + c["allowed"])
            out.append(" switchport mode trunk")
        elif c.get("access"):
            if c["access"] != 1:
                out.append(" switchport access vlan %d" % c["access"])
            out.append(" switchport mode access")
        ps = c.get("portsec")
        if ps:
            out.append(" switchport port-security")
            if ps.get("max"):
                out.append(" switchport port-security maximum %d" % ps["max"])
            if ps.get("sticky"):
                out.append(" switchport port-security mac-address sticky")
            if ps.get("violation"):
                out.append(" switchport port-security violation " + ps["violation"])
        if c.get("shutdown"):
            out.append(" shutdown")
        return out

    def running_config(self):
        out = self._head("12.2")
        out += ["!", "!", "!", "spanning-tree mode pvst", "spanning-tree extend system-id", "!"]
        for n in PORTS[self.kind]:
            out += ["interface " + n] + self._port_block(self.ports.get(n, {})) + ["!"]
        for v in sorted(set([1]) | set(self.svi)):
            out.append("interface Vlan%d" % v)
            if v in self.svi:
                ip, mask, _ = _mask(self.svi[v])
                out.append(" ip address %s %s" % (ip, mask))
            else:
                out += [" no ip address", " shutdown"]
            out.append("!")
        if self.gw:
            out += ["ip default-gateway " + self.gw, "!"]
        lines = self._lines(aux=False)
        lines += ["line vty 5 15", " login"]
        out += lines + ["!", "!", "!", "!", "end"]
        return "\n".join(out)

    def script(self):
        s = ["enable", "configure terminal", "hostname " + self.name]
        s += self._script_security()
        for v, nm in sorted(self.vlans.items()):
            s += ["vlan %d" % v, " name " + nm, " exit"]
        for n, c in self.ports.items():
            blk = self._port_block(c)
            if blk:
                s += ["interface " + n] + blk + [" exit"]
        for v, cidr in sorted(self.svi.items()):
            ip, mask, _ = _mask(cidr)
            s += ["interface Vlan%d" % v, " ip address %s %s" % (ip, mask), " no shutdown", " exit"]
        if self.gw:
            s += ["ip default-gateway " + self.gw]
        s += ["end", "write memory"]
        return "\n".join(s)

    def customize(self, eng):
        _set(eng, "SYS_NAME", self.name)
        _config_lines(eng, self.running_config())
        vl = eng.find("VLANS")
        for c in list(vl):
            vl.remove(c)
        rows = [(1, "default")] + sorted(self.vlans.items()) + [
            (1002, "fddi-default"), (1003, "token-ring-default"),
            (1004, "fddinet-default"), (1005, "trnet-default")]
        for num, nm in rows:
            ET.SubElement(vl, "VLAN", name=nm, rspan="0", number=str(num))
        for n, c in self.ports.items():
            if c.get("shutdown"):
                p = self.port_el(eng, n)
                _set(p, "POWER", "false")


# ---------------------------------------------------------------- lab / file

class _Skeleton:
    def __init__(self):
        self.tree = ET.parse(os.path.join(TPL, "skeleton.xml"))
        self.root = self.tree.getroot()
        pw = self.root.find("PHYSICALWORKSPACE")
        self.parent = {c: p for p in pw.iter() for c in p}
        nodes = list(pw.iter("NODE"))
        self.rack = next(n for n in nodes if n.findtext("TYPE") == "4")          # Rack
        self.office = next(n for n in nodes if n.findtext("NAME") == "Corporate Office")
        self.slots = {True: 1, False: 0}

    def path(self, node):
        out = []
        while node is not None and node.tag == "NODE":
            out.append(node.findtext("UUID_STR"))
            node = self.parent.get(self.parent.get(node))  # NODE -> CHILDREN -> NODE
        return list(reversed(out))

    def next_slot(self, in_rack):
        s = self.slots[in_rack]
        self.slots[in_rack] += 1
        return s


class Lab:
    def __init__(self, title, description="", seed=None):
        self.title, self.description = title, description
        self.rng = random.Random(seed if seed is not None else title)
        self.devices, self.links, self.notes = [], [], []

    def _add(self, cls, *a, **kw):
        d = cls(self, *a, **kw)
        if any(x.name == d.name for x in self.devices):
            raise ValueError("duplicate device name " + d.name)
        self.devices.append(d)
        return d

    def router(self, *a, **kw):
        return self._add(Router, *a, **kw)

    def switch(self, *a, **kw):
        return self._add(Switch, *a, **kw)

    def pc(self, *a, **kw):
        return self._add(PC, *a, **kw)

    def server(self, *a, **kw):
        return self._add(Server, *a, **kw)

    def hub(self, *a, **kw):
        return self._add(Hub, *a, **kw)

    def link(self, a, pa, b, pb, dce=None):
        """Cable two ports. Serial ports get a serial DCE cable (DCE end = `dce`,
        default a); end devices to router/switch-to-switch/hub-to-switch use
        cross-over, everything else straight-through."""
        a.port(pa), b.port(pb)
        if pa.startswith("Serial") != pb.startswith("Serial"):
            raise ValueError("serial port cabled to non-serial")
        if pa.startswith("Serial"):
            kind = "serial"
        else:
            same = {"router2911": "r", "pc": "r", "server": "r",
                    "switch2960": "s", "hub": "s"}
            kind = "cross" if same[a.kind] == same[b.kind] else "straight"
        a.used[pa] = (b, pb)
        b.used[pb] = (a, pa)
        self.links.append((a, pa, b, pb, kind, dce or a))

    def note(self, x, y, text):
        self.notes.append((x, y, text))

    # -- output
    def to_xml(self):
        sk = _Skeleton()
        root = sk.root
        devs = root.find("NETWORK/DEVICES")
        for d in self.devices:
            devs.append(d.to_xml(sk))
        links = root.find("NETWORK/LINKS")
        rng = self.rng
        for a, pa, b, pb, kind, dce in self.links:
            L = ET.SubElement(links, "LINK")
            ET.SubElement(L, "TYPE").text = "eSerial" if kind == "serial" else "eCopper"
            C = ET.SubElement(L, "CABLE")
            ET.SubElement(C, "LENGTH").text = "1"
            ET.SubElement(C, "FUNCTIONAL").text = "true"
            ET.SubElement(C, "FROM").text = a.ref
            ET.SubElement(C, "PORT").text = pa
            ET.SubElement(C, "TO").text = b.ref
            ET.SubElement(C, "PORT").text = pb
            ET.SubElement(C, "FROM_DEVICE_MEM_ADDR").text = str(a.dev_addr)
            ET.SubElement(C, "TO_DEVICE_MEM_ADDR").text = str(b.dev_addr)
            ET.SubElement(C, "FROM_PORT_MEM_ADDR").text = str(rng.randrange(10 ** 11, 10 ** 12))
            ET.SubElement(C, "TO_PORT_MEM_ADDR").text = str(rng.randrange(10 ** 11, 10 ** 12))
            ET.SubElement(C, "GEO_VIEW_COLOR").text = "#1e59a5" if kind == "serial" else "#6ba72e"
            ET.SubElement(C, "IS_MANAGED_IN_RACK_VIEW").text = "false"
            if kind == "serial":
                ET.SubElement(C, "DCEDEV").text = dce.ref
                ET.SubElement(C, "DCEPORT").text = pa if dce is a else pb
            else:
                ET.SubElement(C, "TYPE").text = "eCrossOver" if kind == "cross" else "eStraightThrough"
        notes = root.find("PHYSICALWORKSPACE/NOTES")
        for i, (x, y, text) in enumerate(self.notes):
            N = ET.SubElement(notes, "NOTE", uuid="{%s}" % uuidlib.UUID(int=rng.getrandbits(128), version=4))
            ET.SubElement(N, "X").text = "%g" % x
            ET.SubElement(N, "Y").text = "%g" % y
            ET.SubElement(N, "Z").text = str(40000 + i)
            ET.SubElement(N, "TEXT", translate="true").text = text
            ET.SubElement(N, "NOTECLUSTERID").text = "1-1"
            ET.SubElement(N, "MEM_ADDR").text = str(rng.randrange(10 ** 11, 10 ** 12))
        desc = root.find("NETWORK/DESCRIPTION")
        desc.text = self.title + ("\n\n" + self.description if self.description else "")
        ET.indent(root, space=" ")
        return ET.tostring(root, encoding="unicode").encode("utf-8")

    def save(self, folder, stem):
        os.makedirs(folder, exist_ok=True)
        xml = self.to_xml()
        data = ptfile.encode(xml)
        if ptfile.decode(data) != xml:
            raise AssertionError("round-trip failed")
        open(os.path.join(folder, stem + ".pkt"), "wb").write(data)
        cfg = os.path.join(folder, "configs", stem)
        os.makedirs(cfg, exist_ok=True)
        for d in self.devices:
            if isinstance(d, (Router, Switch)):
                open(os.path.join(cfg, d.name + ".txt"), "w", newline="\n").write(d.script() + "\n")
        return os.path.join(folder, stem + ".pkt")

    def ip_table(self):
        """Markdown table of every addressed interface."""
        rows = ["| Device | Interface | IP address | Subnet mask | Gateway / notes |",
                "|---|---|---|---|---|"]
        for d in self.devices:
            if isinstance(d, Router):
                for n, c in d.ifaces.items():
                    if c.get("ip"):
                        ip, mask, _ = _mask(c["ip"])
                        note = "VLAN %d sub-interface" % c["vlan"] if "vlan" in c else (c.get("desc") or "")
                        rows.append("| %s | %s | %s | %s | %s |" % (d.name, n, ip, mask, note))
            elif isinstance(d, Switch):
                for v, cidr in d.svi.items():
                    ip, mask, _ = _mask(cidr)
                    rows.append("| %s | Vlan%d | %s | %s | %s |" % (d.name, v, ip, mask, d.gw or ""))
            elif isinstance(d, Host):
                r = d.ip_table_row()
                rows.append("| %s | FastEthernet0 | %s | %s | %s |" % (r[0], r[1], r[2], r[3]
                            + ("" if r[4] in ("-", "(from DHCP)") else ", DNS " + r[4])))
        return "\n".join(rows)

    def cabling_table(self):
        names = {"serial": "Serial DCE", "cross": "Copper cross-over", "straight": "Copper straight-through"}
        rows = ["| From | Port | To | Port | Cable |", "|---|---|---|---|---|"]
        for a, pa, b, pb, kind, dce in self.links:
            k = names[kind] + (" (DCE end: %s)" % dce.name if kind == "serial" else "")
            rows.append("| %s | %s | %s | %s | %s |" % (a.name, pa, b.name, pb, k))
        return "\n".join(rows)
