"""Tiny network simulator that reads a finished .pkt and predicts every ping.

    python netsim.py file.pkt                 # print routing tables + all-pairs ping matrix
    python netsim.py file.pkt PC0 192.168.2.2 # one ping, with the hop-by-hop path

It works only from what is inside the file (each device's saved running-config,
the PC/server IP settings, the switch VLAN database and the cables), so it
checks the same data Packet Tracer loads. It models the subset of IOS the labs
use: interfaces and sub-interfaces, switch access/trunk ports and VLANs, hubs,
static routes, RIPv1/v2 (classful summarisation), OSPF (cost = 10^8/bandwidth),
router DHCP pools (+ helper), NAT (static, dynamic pool, PAT) and numbered
standard/extended ACLs. It is a checker, not a replacement for Packet Tracer:
timers, ARP, STP and convergence time are not modelled.
"""

import ipaddress as ipa
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptfile  # noqa: E402
from validate import MODEL_KIND, ports_of  # noqa: E402
from pktgen import PORTS  # noqa: E402

BW = {"Gig": 1000000, "Fas": 100000, "Ser": 1544}  # kbit/s, IOS defaults


def classful(ip):
    first = int(str(ip).split(".")[0])
    plen = 8 if first < 128 else 16 if first < 192 else 24
    return ipa.IPv4Network("%s/%d" % (ip, plen), strict=False)


def wild_match(ip, net, wild):
    i, n, w = int(ipa.IPv4Address(ip)), int(ipa.IPv4Address(net)), int(ipa.IPv4Address(wild))
    return (i & ~w & 0xFFFFFFFF) == (n & ~w & 0xFFFFFFFF)


def blocks(lines):
    out, cur = [], None
    for l in lines:
        if not l or l == "!":
            cur = None
            continue
        if l.startswith(" "):
            if cur is not None:
                cur[1].append(l.strip())
        else:
            cur = (l, [])
            out.append(cur)
    return out


class Iface:
    def __init__(self, dev, name):
        self.dev, self.name = dev, name
        self.ip = self.net = None
        self.shut = False
        self.vlan = None          # sub-interface dot1Q tag
        self.nat = None
        self.acl_in = self.acl_out = None
        self.helper = None
        self.seg = None

    @property
    def cost(self):
        return max(1, 100000 // BW.get(self.name[:3], 100000))


class Router:
    def __init__(self, name, cfg):
        self.name, self.ifs = name, {}
        self.statics, self.rip, self.ospf = [], None, None
        self.nat_static, self.nat_rules, self.pools = [], [], {}
        self.acls, self.dhcp, self.excluded = {}, [], []
        for head, sub in blocks(cfg):
            m = re.match(r"interface (\S+)$", head)
            if m:
                if m.group(1).startswith("Vlan"):
                    continue
                it = self.ifs.setdefault(m.group(1), Iface(self, m.group(1)))
                for s in sub:
                    if s.startswith("ip address "):
                        a, msk = s.split()[2:4]
                        it.ip = ipa.IPv4Address(a)
                        it.net = ipa.IPv4Network("%s/%s" % (a, msk), strict=False)
                    elif s == "shutdown":
                        it.shut = True
                    elif s.startswith("encapsulation dot1Q"):
                        it.vlan = int(s.split()[2])
                    elif s.startswith("ip nat "):
                        it.nat = s.split()[2]
                    elif s.startswith("ip access-group"):
                        _, _, acl, d = s.split()
                        setattr(it, "acl_" + d, acl)
                    elif s.startswith("ip helper-address"):
                        it.helper = ipa.IPv4Address(s.split()[2])
            elif head.startswith("ip route "):
                p = head.split()
                ad = int(p[5]) if len(p) > 5 and p[5].isdigit() else 1
                self.statics.append((ipa.IPv4Network("%s/%s" % (p[2], p[3])), p[4], ad))
            elif head.startswith("router rip"):
                self.rip = {"v": 1, "nets": [], "auto": True, "passive": set()}
                for s in sub:
                    if s.startswith("version"):
                        self.rip["v"] = int(s.split()[1])
                    elif s.startswith("network"):
                        self.rip["nets"].append(classful(s.split()[1]))
                    elif s == "no auto-summary":
                        self.rip["auto"] = False
                    elif s.startswith("passive-interface"):
                        self.rip["passive"].add(s.split()[1])
                if not self.rip["nets"]:
                    self.rip = None
            elif head.startswith("router ospf"):
                self.ospf = {"nets": [], "passive": set()}
                for s in sub:
                    if s.startswith("network"):
                        _, n, w, _, area = s.split()
                        self.ospf["nets"].append((n, w, area))
                    elif s.startswith("passive-interface"):
                        self.ospf["passive"].add(s.split()[1])
            elif head.startswith("ip nat inside source static"):
                p = head.split()
                self.nat_static.append((ipa.IPv4Address(p[5]), ipa.IPv4Address(p[6])))
            elif head.startswith("ip nat pool"):
                p = head.split()
                lo, hi = int(ipa.IPv4Address(p[4])), int(ipa.IPv4Address(p[5]))
                self.pools[p[3]] = [ipa.IPv4Address(x) for x in range(lo, hi + 1)]
            elif head.startswith("ip nat inside source list"):
                p = head.split()
                self.nat_rules.append({"acl": p[5], "pool": p[7] if p[6] == "pool" else None,
                                       "iface": p[7] if p[6] == "interface" else None,
                                       "overload": "overload" in p})
            elif head.startswith("access-list"):
                p = head.split()
                self.acls.setdefault(p[1], []).append(p[2:])
            elif head.startswith("ip dhcp excluded-address"):
                p = head.split()[3:]
                lo = int(ipa.IPv4Address(p[0]))
                hi = int(ipa.IPv4Address(p[1])) if len(p) > 1 else lo
                self.excluded.append((lo, hi))
            elif head.startswith("ip dhcp pool"):
                pool = {"name": head.split()[3], "net": None, "gw": None, "dns": None}
                for s in sub:
                    p = s.split()
                    if p[0] == "network":
                        pool["net"] = ipa.IPv4Network("%s/%s" % (p[1], p[2]))
                    elif p[0] == "default-router":
                        pool["gw"] = ipa.IPv4Address(p[1])
                    elif p[0] == "dns-server":
                        pool["dns"] = ipa.IPv4Address(p[1])
                pool["used"] = set()
                self.dhcp.append(pool)
        self.nat_table = {}   # (global ip) -> local ip, for replies

    carrier = None   # set of physical port names with a live cable (filled by Net)

    def up_ifs(self):
        base = lambda i: i.name.split(".")[0]  # noqa: E731
        return [i for i in self.ifs.values() if i.ip and not i.shut and i.seg is not None
                and not (i.vlan is None and "." in i.name)
                and not self.ifs.get(base(i), i).shut
                and (self.carrier is None or base(i) in self.carrier)]

    def acl_permits(self, acl, src, dst):
        if acl is None or acl not in self.acls:
            return True
        for rule in self.acls[acl]:
            action, rest = rule[0], rule[1:]
            if int(acl) < 100:
                if self._match(rest, src)[0]:
                    return action == "permit"
            else:
                rest = rest[1:]  # protocol: ip/icmp, both match a ping
                ok, rest = self._match(rest, src)
                ok2, _ = self._match(rest, dst)
                if ok and ok2:
                    return action == "permit"
        return False  # implicit deny

    @staticmethod
    def _match(tok, ip):
        if tok[0] == "any":
            return True, tok[1:]
        if tok[0] == "host":
            return ip == ipa.IPv4Address(tok[1]), tok[2:]
        if len(tok) > 1 and re.match(r"\d+\.\d+\.\d+\.\d+$", tok[1]):
            return wild_match(ip, tok[0], tok[1]), tok[2:]
        return ip == ipa.IPv4Address(tok[0]), tok[1:]


class Host:
    def __init__(self, name, port):
        self.name = name
        self.dhcp = port.findtext("PORT_DHCP_ENABLE") == "true"
        self.ip = self.net = self.gw = None
        if not self.dhcp and port.findtext("IP"):
            self.ip = ipa.IPv4Address(port.findtext("IP"))
            self.net = ipa.IPv4Network("%s/%s" % (port.findtext("IP"), port.findtext("SUBNET")), strict=False)
            if port.findtext("PORT_GATEWAY"):
                self.gw = ipa.IPv4Address(port.findtext("PORT_GATEWAY"))
        self.seg = None


class Net:
    def __init__(self, path):
        root = ET.fromstring(ptfile.decode(open(path, "rb").read()))
        self.routers, self.hosts, self.switches = {}, {}, {}
        byref = {}
        for d in root.find("NETWORK/DEVICES"):
            e = d.find("ENGINE")
            kind = MODEL_KIND.get(e.find("TYPE").get("model"))
            name = e.findtext("NAME")
            if kind is None:
                continue
            ports = dict(zip(PORTS[kind], ports_of(e)))
            byref[e.findtext("SAVE_REF_ID")] = (name, kind)
            if kind == "router2911":
                self.routers[name] = Router(name, [l.text or "" for l in e.find("RUNNINGCONFIG")])
            elif kind in ("pc", "server"):
                self.hosts[name] = Host(name, ports["FastEthernet0"])
            elif kind == "switch2960":
                self.switches[name] = self._switch(e)
            elif kind == "hub":
                self.switches[name] = {"hub": True}
        self.links = []
        for L in root.find("NETWORK/LINKS"):
            c = L.find("CABLE")
            pa, pb = [p.text for p in c.findall("PORT")]
            self.links.append((byref[c.findtext("FROM")], pa, byref[c.findtext("TO")], pb))
        self._carrier()
        self._segments()
        self._dhcp()
        self._routing()

    @staticmethod
    def _switch(e):
        vlans = {int(v.get("number")) for v in e.find("VLANS")}
        ports = {}
        for head, sub in blocks([l.text or "" for l in e.find("RUNNINGCONFIG")]):
            m = re.match(r"interface (\S+)$", head)
            if not m or m.group(1).startswith("Vlan"):
                continue
            c = {"mode": "access", "vlan": 1, "allowed": None, "native": 1, "shut": False}
            for s in sub:
                if s.startswith("switchport access vlan"):
                    c["vlan"] = int(s.split()[3])
                elif s == "switchport mode trunk":
                    c["mode"] = "trunk"
                elif s.startswith("switchport trunk allowed vlan"):
                    c["allowed"] = {int(x) for x in s.split()[4].split(",")}
                elif s.startswith("switchport trunk native vlan"):
                    c["native"] = int(s.split()[4])
                elif s == "shutdown":
                    c["shut"] = True
            ports[m.group(1)] = c
        return {"hub": False, "vlans": vlans, "ports": ports}

    def _admin_down(self, name, kind, port):
        if kind == "router2911":
            it = self.routers[name].ifs.get(port)
            return it is not None and it.shut
        if kind == "switch2960":
            return self.switches[name]["ports"].get(port, {}).get("shut", False)
        return False

    def _carrier(self):
        """A port has carrier only if it is cabled and neither end is shut down."""
        for r in self.routers.values():
            r.carrier = set()
        for (da, ka), pa, (db, kb), pb in self.links:
            if self._admin_down(da, ka, pa) or self._admin_down(db, kb, pb):
                continue
            for d, k, p in ((da, ka, pa), (db, kb, pb)):
                if k == "router2911":
                    self.routers[d].carrier.add(p)

    # -- layer 2: union-find over (device, vlan) / router-interface attachment points
    def _segments(self):
        parent = {}

        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            parent[find(a)] = find(b)

        def attach(dev, kind, port):
            """Attachment points a port offers: {vlan or None: node}."""
            if kind == "switch2960":
                c = self.switches[dev]["ports"].get(port, {"mode": "access", "vlan": 1, "shut": False,
                                                           "allowed": None, "native": 1})
                if c["shut"]:
                    return {}
                vl = self.switches[dev]["vlans"]
                if c["mode"] == "access":
                    return {None: ("sw", dev, c["vlan"])} if c["vlan"] in vl else {}
                allowed = (c["allowed"] or vl) & vl
                out = {v: ("sw", dev, v) for v in allowed}
                out[None] = ("sw", dev, c["native"])
                return out
            if kind == "hub":
                return {None: ("hub", dev)}
            if kind == "router2911":
                r = self.routers[dev]
                if port in r.ifs and r.ifs[port].shut:
                    return {}
                out = {None: ("rif", dev, port)}
                for n, it in r.ifs.items():
                    if n.startswith(port + ".") and it.vlan:
                        out[it.vlan] = ("rif", dev, n)
                return out
            return {None: ("host", dev)}

        for (da, ka), pa, (db, kb), pb in self.links:
            A, B = attach(da, ka, pa), attach(db, kb, pb)
            tagged_a = {k for k in A if k is not None}
            tagged_b = {k for k in B if k is not None}
            if None in A and None in B:
                union(A[None], B[None])
            for v in tagged_a & tagged_b:
                union(A[v], B[v])
        for r in self.routers.values():
            for n, it in r.ifs.items():
                it.seg = find(("rif", r.name, n))
        for h in self.hosts.values():
            h.seg = find(("host", h.name))

    def _l3_on_seg(self, seg):
        out = [(i.ip, i) for r in self.routers.values() for i in r.up_ifs() if i.seg == seg]
        out += [(h.ip, h) for h in self.hosts.values() if h.ip and h.seg == seg]
        return out

    def _dhcp(self):
        for h in sorted(self.hosts.values(), key=lambda x: x.name):
            if not h.dhcp:
                continue
            for r in self.routers.values():
                for it in r.up_ifs():
                    if it.seg != h.seg:
                        continue
                    target_r, net = r, it.net
                    if it.helper:  # relay: pool lives on the router owning the helper address
                        owner = [x for x in self.routers.values()
                                 for y in x.ifs.values() if y.ip == it.helper]
                        target_r = owner[0] if owner else None
                    if not target_r:
                        continue
                    for pool in target_r.dhcp:
                        if pool["net"] == net:
                            taken = {i.ip for x in self.routers.values() for i in x.ifs.values() if i.ip}
                            taken |= {x.ip for x in self.hosts.values() if x.ip}
                            for a in pool["net"].hosts():
                                ai = int(a)
                                if any(lo <= ai <= hi for lo, hi in target_r.excluded) or a in taken:
                                    continue
                                h.ip, h.net, h.gw = a, pool["net"], pool["gw"]
                                h.dns = pool["dns"]
                                break
                        if h.ip:
                            break
                    if h.ip:
                        break
                if h.ip:
                    break

    # -- layer 3 control plane
    def _routing(self):
        self.rt = {}
        for r in self.routers.values():
            t = {}
            for it in r.up_ifs():
                t[it.net] = ("C", 0, None, it, 0)
            self.rt[r.name] = t
        for r in self.routers.values():   # statics (next hop must be on a connected net)
            for net, nh, ad in r.statics:
                if re.match(r"\d", nh):
                    nh = ipa.IPv4Address(nh)
                    out = next((i for i in r.up_ifs() if nh in i.net), None)
                    if out:
                        self._install(r.name, net, ("S", 0, nh, out, ad))
                else:
                    it = r.ifs.get(nh)
                    if it and it in r.up_ifs():
                        self._install(r.name, net, ("S", 0, None, it, ad))
        self._ospf()
        self._rip()

    def _neighbors(self, r, it):
        for _, other in self._l3_on_seg(it.seg):
            if isinstance(other, Iface) and other.dev is not r and other.net == it.net:
                yield other

    def _install(self, rname, net, entry):
        cur = self.rt[rname].get(net)
        if cur is None or (entry[4], entry[1]) < (cur[4], cur[1]):
            self.rt[rname][net] = entry

    def _ospf(self):
        def area(r, it):
            for n, w, a in (r.ospf or {}).get("nets", []):
                if wild_match(it.ip, n, w):
                    return a
            return None

        def enabled(r, it):
            return area(r, it) is not None

        ors = [r for r in self.routers.values() if r.ospf]
        if not ors:
            return
        dist = {}
        for src in ors:
            # Dijkstra from src over OSPF adjacencies
            d = {src.name: (0, None, None)}
            todo = [(0, src.name, None, None)]
            while todo:
                todo.sort(key=lambda x: x[0])
                c, name, first_nh, first_if = todo.pop(0)
                if d.get(name, (1e9,))[0] < c:
                    continue
                r = self.routers[name]
                for it in r.up_ifs():
                    if not enabled(r, it) or it.name in r.ospf["passive"]:
                        continue
                    for nb in self._neighbors(r, it):
                        if not enabled(nb.dev, nb) or nb.name in nb.dev.ospf["passive"]:
                            continue
                        if area(nb.dev, nb) != area(r, it):
                            continue   # area mismatch: no adjacency
                        nc = c + it.cost
                        nh = (nb.ip, it) if name == src.name else (first_nh, first_if)
                        if nc < d.get(nb.dev.name, (1e9,))[0]:
                            d[nb.dev.name] = (nc, nh[0], nh[1])
                            todo.append((nc, nb.dev.name, nh[0], nh[1]))
            dist[src.name] = d
        for src in ors:
            for dst_name, (c, nh, oif) in dist[src.name].items():
                if dst_name == src.name:
                    continue
                for it in self.routers[dst_name].up_ifs():
                    if enabled(self.routers[dst_name], it):
                        self._install(src.name, it.net, ("O", c + it.cost, nh, oif, 110))

    def _rip(self):
        rr = [r for r in self.routers.values() if r.rip]

        def enabled(r, it):
            return r.rip and classful(it.ip) in r.rip["nets"]

        db = {r.name: {} for r in rr}   # net -> (metric, nh, oif)
        for r in rr:
            for it in r.up_ifs():
                if enabled(r, it):
                    db[r.name][it.net] = (0, None, it)
        for _ in range(16):
            changed = False
            for r in rr:
                for it in r.up_ifs():
                    if not enabled(r, it) or it.name in r.rip["passive"]:
                        continue
                    for nb in self._neighbors(r, it):
                        n = nb.dev
                        if not n.rip or not enabled(n, nb):
                            continue
                        # what r advertises out of `it`
                        for net, (m, _, src_if) in list(db[r.name].items()):
                            if src_if is it or m >= 15:
                                continue
                            adv = net
                            summ = r.rip["v"] == 1 or r.rip["auto"]
                            if summ and classful(net.network_address) != classful(it.ip):
                                adv = classful(net.network_address)
                            elif r.rip["v"] == 1 and net.prefixlen != it.net.prefixlen:
                                continue   # v1 cannot carry a different mask inside a major net
                            if n.rip["v"] == 1 and r.rip["v"] == 2:
                                continue   # v1 router ignores v2 (multicast) updates
                            if r.rip["v"] == 1 and n.rip["v"] == 2:
                                continue   # v2-only receiver ignores v1 broadcasts
                            if adv in self.rt[n.name] and self.rt[n.name][adv][0] == "C":
                                continue
                            cur = db[n.name].get(adv)
                            if cur is None or m + 1 < cur[0]:
                                db[n.name][adv] = (m + 1, it.ip, nb)
                                changed = True
            if not changed:
                break
        for r in rr:
            for net, (m, nh, oif) in db[r.name].items():
                if nh is not None:
                    self._install(r.name, net, ("R", m, nh, oif, 120))

    def route(self, r, dst):
        best = None
        for net, e in self.rt[r.name].items():
            if dst in net and (best is None or net.prefixlen > best[0].prefixlen):
                best = (net, e)
        return best

    # -- data plane
    def _owner(self, seg, ip):
        for a, obj in self._l3_on_seg(seg):
            if a == ip:
                return obj
        return None

    def _nat_out(self, r, inif, outif, src):
        """Translate src when going inside -> outside."""
        if inif.nat != "inside" or outif.nat != "outside":
            return src
        for loc, glob in r.nat_static:
            if loc == src:
                return glob
        for rule in r.nat_rules:
            if r.acl_permits(rule["acl"], src, src):
                if rule["iface"]:
                    g = r.ifs[rule["iface"]].ip
                else:
                    pool = r.pools[rule["pool"]]
                    used = set(r.nat_table)
                    free = [p for p in pool if p not in used or r.nat_table[p] == src]
                    if not free:
                        if not rule["overload"]:
                            return None
                        free = pool[:1]
                    g = free[0]
                r.nat_table[g] = src
                return g
        return src

    def _nat_in(self, r, inif, dst):
        if inif.nat != "outside":
            return dst
        for loc, glob in r.nat_static:
            if glob == dst:
                return loc
        return r.nat_table.get(dst, dst)

    def send(self, src_name, src_ip, dst, path):
        """Deliver one packet from host `src_name`. Returns (delivered-to obj, final src ip) or (None, reason)."""
        h = self.hosts[src_name]
        if dst in h.net:
            nxt = dst
        elif h.gw is None:
            return None, "no default gateway on " + h.name
        else:
            nxt = h.gw
        obj = self._owner(h.seg, nxt)
        if obj is None:
            return None, "%s: %s not reachable on its LAN" % (h.name, nxt)
        src = src_ip
        for _ in range(32):
            if isinstance(obj, Host):
                return (obj, src) if obj.ip == dst else (None, "wrong host")
            it, r = obj, obj.dev
            path.append("%s(%s)" % (r.name, it.name))
            if not r.acl_permits(it.acl_in, src, dst):
                return None, "%s: denied by ACL %s in on %s" % (r.name, it.acl_in, it.name)
            dst = self._nat_in(r, it, dst)
            if any(i.ip == dst for i in r.up_ifs()):
                return (r, src)
            rt = self.route(r, dst)
            if rt is None:
                return None, "%s: no route to %s" % (r.name, dst)
            _, (code, _, nh, oif, _ad) = rt
            nsrc = self._nat_out(r, it, oif, src)
            if nsrc is None:
                return None, "%s: NAT pool exhausted" % r.name
            src = nsrc
            if not r.acl_permits(oif.acl_out, src, dst):
                return None, "%s: denied by ACL %s out on %s" % (r.name, oif.acl_out, oif.name)
            hop = dst if code == "C" else nh
            obj = self._owner(oif.seg, hop)
            if obj is None:
                return None, "%s: next hop %s not on %s" % (r.name, hop, oif.name)
        return None, "TTL expired"

    def ping(self, src_name, dst):
        """Echo + reply. Returns (ok, text)."""
        dst = ipa.IPv4Address(dst)
        h = self.hosts[src_name]
        if h.ip is None:
            return False, "%s has no IP address" % src_name
        path = [src_name]
        got, src_seen = self.send(src_name, h.ip, dst, path)
        if got is None:
            return False, src_seen + "  [" + " > ".join(path) + "]"
        if isinstance(got, Router):
            return True, " > ".join(path) + " (router answered)"
        back = [got.name]
        rep, why = self.send(got.name, got.ip, src_seen, back)
        if rep is None or getattr(rep, "name", None) != src_name:
            return False, "reply lost: %s  [%s]" % (why, " > ".join(back))
        return True, " > ".join(path + [got.name])


def main():
    net = Net(sys.argv[1])
    if len(sys.argv) == 4:
        ok, txt = net.ping(sys.argv[2], sys.argv[3])
        print(("SUCCESS " if ok else "FAIL    ") + txt)
        return
    for r in net.routers.values():
        print("== %s routing table" % r.name)
        for n, (code, m, nh, oif, ad) in sorted(net.rt[r.name].items(), key=lambda x: (x[0].network_address, x[0].prefixlen)):
            print("  %s %-18s %s%s" % (code, n, ("via %s, " % nh) if nh else "is directly connected, ", oif.name))
    names = sorted(net.hosts)
    for a in names:
        for b in names:
            if a != b and net.hosts[b].ip:
                ok, txt = net.ping(a, net.hosts[b].ip)
                print("%-8s %-10s -> %-10s %s" % ("OK" if ok else "FAIL", a, b, "" if ok else txt))


if __name__ == "__main__":
    main()
