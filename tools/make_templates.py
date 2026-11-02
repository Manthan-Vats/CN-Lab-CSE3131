"""One-time step: pull clean device templates out of real Packet Tracer 8.2.1 saves.

    python make_templates.py <decoded-xml-dir>

Reads decoded XML (see ptfile.py decode) of three public lab files saved with
Packet Tracer 8.2.1.0118 (github.com/Thuy-Hung/Cisco-Packet-Tracer-Labs-for-CCNA):
  Day 28 OSPF Part 3  -> skeleton, 2911 (with HWIC-2T), 2960-24TT, PC-PT
  Day 44 Static NAT   -> Server-PT
  Day 22 Rapid STP    -> Hub-PT
and writes templates/<kind>.xml (DEVICE element + its physical-workspace NODE)
and templates/skeleton.xml (an empty 8.2.1 network that keeps only the
Power Distribution Device every PT file has).
"""

import copy
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "templates")

SOURCES = {
    "ospf": "Cisco_Packet_Tracer_Labs_for_CCNA_Day_28_Lab_OSPF_Part_3_pkt.xml",
    "nat": "_Cisco_Packet_Tracer_Labs_for_CCNA_Day_44_Lab_Static_NAT_pkt.xml",
    "stp": "g_Cisco_Packet_Tracer_Labs_for_CCNA_Day_22_Lab_Rapid_STP_pkt.xml",
}
WANT = {  # kind: (source, model)
    "router2911": ("ospf", "2911"),
    "switch2960": ("ospf", "2960-24TT"),
    "pc": ("ospf", "PC-PT"),
    "server": ("nat", "Server-PT"),
    "hub": ("stp", "Hub-PT"),
}


def pw_nodes(root):
    return {n.findtext("UUID_STR"): n for n in root.find("PHYSICALWORKSPACE").iter("NODE")}


def main(src_dir):
    os.makedirs(OUT, exist_ok=True)
    trees = {k: ET.parse(os.path.join(src_dir, v)) for k, v in SOURCES.items()}
    for kind, (src, model) in WANT.items():
        root = trees[src].getroot()
        dev = next(d for d in root.find("NETWORK/DEVICES")
                   if d.find("ENGINE/TYPE").get("model") == model)
        dev = copy.deepcopy(dev)
        uuid = dev.findtext("WORKSPACE/PHYSICAL").split(",")[-1]
        node = copy.deepcopy(pw_nodes(root)[uuid])
        wrap = ET.Element("TEMPLATE", kind=kind, model=model,
                          version=root.findtext("VERSION"))
        wrap.append(dev)
        wrap.append(node)
        ET.ElementTree(wrap).write(os.path.join(OUT, kind + ".xml"), encoding="utf-8")
        print(kind, model, root.findtext("VERSION"))

    # skeleton: drop every device except the Power Distribution Device
    root = trees["ospf"].getroot()
    devs = root.find("NETWORK/DEVICES")
    keep_uuid = set()
    for d in list(devs):
        if d.find("ENGINE/TYPE").get("model") == "Power Distribution Device":
            keep_uuid.add(d.findtext("WORKSPACE/PHYSICAL").split(",")[-1])
        else:
            devs.remove(d)
    for l in list(root.find("NETWORK/LINKS")):
        root.find("NETWORK/LINKS").remove(l)
    pw = root.find("PHYSICALWORKSPACE")
    parents = {c: p for p in pw.iter() for c in p}
    for n in list(pw.iter("NODE")):
        if n.findtext("TYPE") == "6" and n.findtext("UUID_STR") not in keep_uuid:
            parents[n].remove(n)
    for tag in ("RECTANGLES", "COMMAND_LOGS"):
        el = root.find(tag)
        for c in list(el):
            el.remove(c)
    notes = pw.find("NOTES")
    if notes is not None:
        for c in list(notes):
            notes.remove(c)
    trees["ospf"].write(os.path.join(OUT, "skeleton.xml"), encoding="utf-8")
    print("skeleton", root.findtext("VERSION"))


if __name__ == "__main__":
    main(sys.argv[1])
