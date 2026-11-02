"""Structural checks on a finished .pkt (no Packet Tracer needed).

    python validate.py file.pkt [file2.pkt ...]

Decodes the file with ptfile.py (this also verifies the EAX integrity tag)
and checks the things Packet Tracer relies on when it opens a file:
  * XML parses; version header present
  * every device: unique name, unique save-ref-id, unique MACs, has config
  * every link: both ends point at real devices and real port names,
    no port is cabled twice, cable type fits the ports, serial DCE end is valid
  * every device's physical path resolves to real workspace nodes
  * router/switch running-config only names interfaces the hardware has
  * router port IP fields match the running-config
"""

import ipaddress
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptfile  # noqa: E402
from pktgen import PORTS

MODEL_KIND = {"2911": "router2911", "2960-24TT": "switch2960", "PC-PT": "pc",
              "Server-PT": "server", "Hub-PT": "hub"}


def ports_of(eng):
    ps = [p for p in eng.iter("PORT") if p.find("TYPE") is not None and p.find("MACADDRESS") is not None]
    return [p for p in ps if p.findtext("TYPE") != "eBluetooth"] + \
           [p for p in ps if p.findtext("TYPE") == "eBluetooth"]


def check(path):
    errs = []
    xml = ptfile.decode(open(path, "rb").read())
    root = ET.fromstring(xml)
    if not root.findtext("VERSION"):
        errs.append("no VERSION")
    pw = root.find("PHYSICALWORKSPACE")
    uuids = {n.findtext("UUID_STR") for n in pw.iter("NODE")}
    devs = {}
    names, macs = set(), {}
    for d in root.find("NETWORK/DEVICES"):
        e = d.find("ENGINE")
        model = e.find("TYPE").get("model")
        name, ref = e.findtext("NAME"), e.findtext("SAVE_REF_ID")
        if model == "Power Distribution Device":
            continue
        kind = MODEL_KIND.get(model)
        if kind is None:
            errs.append("%s: unexpected model %s" % (name, model))
            continue
        if name in names:
            errs.append("duplicate name " + name)
        names.add(name)
        if ref in devs:
            errs.append("duplicate save-ref-id " + ref)
        ports = ports_of(e)
        if len(ports) != len(PORTS[kind]):
            errs.append("%s: %d ports, expected %d" % (name, len(ports), len(PORTS[kind])))
        devs[ref] = (name, kind, e, dict(zip(PORTS[kind], ports)))
        for p in ports:
            m = p.findtext("MACADDRESS")
            if m in macs:
                errs.append("duplicate MAC %s (%s, %s)" % (m, name, macs[m]))
            macs[m] = name
        for u in d.findtext("WORKSPACE/PHYSICAL").split(","):
            if u not in uuids:
                errs.append("%s: physical path node %s missing" % (name, u))
        if d.findtext("WORKSPACE/PHYSICAL_CPUR/CONTAINER_ID") not in uuids:
            errs.append("%s: CPUR container missing" % name)
        if kind in ("router2911", "switch2960"):
            cfg = [l.text or "" for l in e.find("RUNNINGCONFIG")]
            if not cfg or cfg[-1] != "end":
                errs.append("%s: running-config does not end with 'end'" % name)
            if [l.text for l in e.find("STARTUPCONFIG")] != [l.text for l in e.find("RUNNINGCONFIG")]:
                errs.append("%s: startup-config differs from running-config (not saved)" % name)
            cur = None
            for l in cfg:
                m = re.match(r"interface (\S+)$", l)
                if m:
                    cur = m.group(1)
                    base = cur.split(".")[0]
                    if base not in PORTS[kind] and not re.match(r"Vlan\d+$", cur):
                        errs.append("%s: config names missing interface %s" % (name, cur))
                    continue
                m = re.match(r" ip address (\S+) (\S+)$", l)
                if m and kind == "router2911" and cur in PORTS[kind]:
                    p = devs[ref][3].get(cur)
                    if p is None:
                        errs.append("%s: no port element for %s" % (name, cur))
                    elif (p.findtext("IP"), p.findtext("SUBNET")) != m.groups():
                        errs.append("%s %s: port fields %s/%s != config %s/%s" % (
                            name, cur, p.findtext("IP"), p.findtext("SUBNET"), *m.groups()))
                if not l.startswith(" "):
                    cur = None if not l.startswith("interface") else cur
    used = set()
    for L in root.find("NETWORK/LINKS"):
        c = L.find("CABLE")
        frm, to = c.findtext("FROM"), c.findtext("TO")
        pa, pb = [p.text for p in c.findall("PORT")]
        ends = []
        for ref, port in ((frm, pa), (to, pb)):
            if ref not in devs:
                errs.append("link to unknown device %s" % ref)
                continue
            name, kind, e, ports = devs[ref]
            if port not in ports:
                errs.append("link to unknown port %s %s" % (name, port))
            if (ref, port) in used:
                errs.append("port cabled twice: %s %s" % (name, port))
            used.add((ref, port))
            ends.append((name, kind, port))
        if len(ends) != 2:
            continue
        ser = [p.startswith("Serial") for _, _, p in ends]
        if L.findtext("TYPE") == "eSerial":
            if not all(ser):
                errs.append("serial cable on non-serial port %s" % ends)
            if c.findtext("DCEDEV") not in (frm, to) or c.findtext("DCEPORT") not in (pa, pb):
                errs.append("bad DCE end on %s" % ends)
        else:
            if any(ser):
                errs.append("copper cable on serial port %s" % ends)
            cls = {"router2911": "r", "pc": "r", "server": "r", "switch2960": "s", "hub": "s"}
            want = "eCrossOver" if cls[ends[0][1]] == cls[ends[1][1]] else "eStraightThrough"
            if c.findtext("TYPE") != want:
                errs.append("wrong cable %s on %s (want %s)" % (c.findtext("TYPE"), ends, want))
    for ref, (name, kind, e, ports) in devs.items():
        if kind in ("pc", "server"):
            p = ports["FastEthernet0"]
            if p.findtext("PORT_DHCP_ENABLE") != "true":
                try:
                    ipaddress.IPv4Interface("%s/%s" % (p.findtext("IP"), p.findtext("SUBNET")))
                except ValueError:
                    errs.append("%s: bad static IP %s/%s" % (name, p.findtext("IP"), p.findtext("SUBNET")))
    return root, errs


if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        _, errs = check(f)
        print(("OK   " if not errs else "FAIL ") + f)
        for e in errs:
            print("     - " + e)
        bad += bool(errs)
    sys.exit(1 if bad else 0)
