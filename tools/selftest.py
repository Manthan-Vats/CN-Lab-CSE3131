"""Mutation tests: break a working lab on purpose and make sure netsim notices.

    python selftest.py

A checker that says "OK" to everything is useless, so each case below takes a
lab that passes, introduces one classic student mistake, rebuilds the .pkt and
asserts that the simulator now reports the ping as failing (or, for the last
cases, still succeeding when the mistake should be harmless).
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import labs  # noqa: E402
import netsim  # noqa: E402
import ptfile  # noqa: E402


def dev(L, name):
    return next(d for d in L.devices if d.name == name)


def run(fn, mutate, src, dst, want, label):
    L, _, _, _ = fn()
    mutate(L)
    tmp = tempfile.mkdtemp()
    path = L.save(tmp, "t")
    ok, txt = netsim.Net(path).ping(src, dst)
    good = ok == want
    print("%s %-60s -> %s" % ("PASS" if good else "FAIL", label, txt if not ok else "reply"))
    return good


def drop_post(name, idx=None):
    def m(L):
        d = dev(L, name)
        d.post = [] if idx is None else [b for i, b in enumerate(d.post) if i != idx]
    return m


def set_iface(name, ifc, **kw):
    def m(L):
        dev(L, name).ifaces[ifc].update(kw)
    return m


def cases():
    G0, G1, S0 = "GigabitEthernet0/0", "GigabitEthernet0/1", "Serial0/0/0"
    yield labs.p06, drop_post("Router1"), "PC0", "192.168.2.2", False, "static: Router1 has no route back"
    yield labs.p06, set_iface("Router0", S0, shutdown=True), "PC0", "192.168.2.2", False, "static: serial shut down"
    yield labs.p06, set_iface("Router1", S0, ip="12.0.0.2/8"), "PC0", "192.168.2.2", False, "static: serial IPs in different subnets"
    yield labs.p06, lambda L: setattr(dev(L, "PC0"), "gw", ""), "PC0", "192.168.2.2", False, "static: PC without default gateway"
    yield labs.p06, lambda L: setattr(dev(L, "PC0"), "gw", "192.168.1.9"), "PC0", "192.168.2.2", False, "static: PC with wrong gateway"
    yield labs.p06, lambda L: None, "PC0", "192.168.1.3", True, "static: same-LAN ping needs no router"

    def rip_v1_on_r2(L):
        d = dev(L, "Router2")
        d.post = [b.replace(" version 2\n", "") for b in d.post]
    yield labs.p07b, rip_v1_on_r2, "PC1", "8.0.0.2", False, "RIP: Router2 forced to v1 ignores v2 updates"
    yield labs.p07b, drop_post("Router0"), "PC0", "60.0.0.2", False, "RIP: Router0 not running RIP"

    def rip_v1_slash16(L):
        dev(L, "Router0").ifaces["GigabitEthernet0/0"]["ip"] = "192.168.1.1/16"
        dev(L, "PC0").ip = "192.168.1.2/16"
    yield labs.p07a, rip_v1_slash16, "PC1", "192.168.1.2", False, "RIPv1 cannot carry the /16 supernet (why v1 file uses /24)"

    def ospf_wrong_wildcard(L):
        d = dev(L, "R2")
        d.post = [d.post[0].replace("network 30.0.0.0 0.255.255.255", "network 31.0.0.0 0.255.255.255")]
    yield labs.p08a, ospf_wrong_wildcard, "PC1", "30.0.0.2", False, "OSPF: LAN network statement wrong"

    def ospf_area(L):
        d = dev(L, "R2")
        d.post = [d.post[0].replace("network 20.0.0.0 0.255.255.255 area 0", "network 20.0.0.0 0.255.255.255 area 1")]
    yield labs.p08a, ospf_area, "PC1", "30.0.0.2", False, "OSPF: area mismatch on the link"
    yield labs.p08b, set_iface("R0", S0, shutdown=True), "PC0", "192.168.2.12", True, "OSPF: R0-R1 link down, reroute via R2"

    def access_not_trunk(L):
        for s in ("Switch0", "Switch1"):
            dev(L, s).ports["GigabitEthernet0/1"] = {"access": 10}
    yield labs.p09a, access_not_trunk, "PC0", "192.168.10.7", True, "VLAN: uplink as access VLAN 10 -> STUDENT still works"
    yield labs.p09a, access_not_trunk, "PC4", "192.168.10.10", False, "VLAN: uplink as access VLAN 10 -> FACULTY broken"

    def wrong_vlan(L):
        dev(L, "Switch0").ports["FastEthernet0/1"] = {"access": 20}
    yield labs.p09a, wrong_vlan, "PC0", "192.168.10.2", False, "VLAN: PC0 port in wrong VLAN"

    def no_subif_vlan(L):
        dev(L, "Router0").ifaces["GigabitEthernet0/0.20"]["vlan"] = 30
    yield labs.p09b, no_subif_vlan, "PC0", "192.168.20.11", False, "router-on-a-stick: wrong dot1Q tag"

    def vlan_missing(L):
        del dev(L, "Switch1").vlans[20]
    yield labs.p09b, vlan_missing, "PC6", "192.168.10.11", False, "VLAN 20 not created on Switch1"
    yield labs.p10c, set_iface("R1", S0, nat=None), "PC0", "198.51.100.10", False, "NAT: forgot 'ip nat outside'"
    yield labs.p10c, set_iface("R1", G0, nat=None), "PC0", "198.51.100.10", False, "NAT: forgot 'ip nat inside'"

    def acl_wrong(L):
        d = dev(L, "R1")
        d.post = [b.replace("access-list 1 permit 192.168.1.0", "access-list 1 permit 192.168.2.0") for b in d.post]
    yield labs.p10b, acl_wrong, "PC0", "198.51.100.10", False, "NAT: ACL matches the wrong subnet"
    yield labs.p12, set_iface("R1", G1, acl_in=None), "Guest-PC", "192.168.30.100", True, "ACL removed -> guest reaches server"

    def no_pool(L):
        dev(L, "Router0").pre = []
    yield labs.p04, no_pool, "PC0", "192.168.1.1", False, "DHCP: no pool -> PC has no address"

    def primary_down(L):
        dev(L, "R1").ifaces["Serial0/0/0"]["shutdown"] = True
    yield labs.p13b, primary_down, "Sales-PC1", "198.51.100.10", True, "case study: primary ISP link down -> backup via R2"

    def both_down(L):
        dev(L, "R1").ifaces["Serial0/0/0"]["shutdown"] = True
        dev(L, "R2").ifaces["Serial0/0/0"]["shutdown"] = True
    yield labs.p13b, both_down, "Sales-PC1", "198.51.100.10", False, "case study: both ISP links down"


def main():
    results = [run(*c) for c in cases()]
    print("\n%d/%d mutation tests behaved as expected" % (sum(results), len(results)))
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
