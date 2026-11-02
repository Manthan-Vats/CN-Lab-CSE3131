"""Build every lab .pkt, then prove it: structure check + simulated pings.

    python build.py            # build all, write README tables, exit 1 on any failure

For every lab: write <folder>/<stem>.pkt and <folder>/configs/<device>.txt,
run validate.check() on the written file, then run every expected ping in
netsim against the written file. Results go to <folder>/<stem>.results.md and
are pasted into the folder README (between the AUTO markers) by docs.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import labs  # noqa: E402
import netsim  # noqa: E402
import validate  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_one(fn):
    L, folder, stem, exp = fn()
    out = os.path.join(ROOT, folder)
    path = L.save(out, stem)
    _, errs = validate.check(path)
    net = netsim.Net(path)
    rows, bad = [], list(errs)
    for src, dst, want in exp:
        ok, txt = net.ping(src, dst)
        mark = "reply" if ok else "no reply"
        rows.append("| %s | %s | %s | %s |" % (src, dst, mark,
                                                "as expected" if ok == want else "**UNEXPECTED**"))
        if ok != want:
            bad.append("ping %s -> %s: got %s, expected %s (%s)" % (src, dst, ok, want, txt))
    leases = ["| %s | %s | %s |" % (h.name, h.ip, h.gw) for h in net.hosts.values() if h.dhcp]
    rt = []
    for r in net.routers.values():
        rt.append("%s# show ip route   (connected / static / OSPF / RIP part)" % r.name)
        for n, (code, m, nh, oif, ad) in sorted(net.rt[r.name].items(),
                                                key=lambda x: (x[0].network_address, x[0].prefixlen)):
            if code == "C":
                rt.append("C    %s is directly connected, %s" % (n, oif.name))
            else:
                rt.append("%s    %s [%d/%d] via %s, %s" % (code, n, ad, m, nh, oif.name) if nh else
                          "%s    %s is directly connected, %s" % (code, n, oif.name))
        rt.append("")
    md = ["### Simulated results for `%s.pkt`" % stem, "",
          "Checked by `tools/netsim.py` reading the finished file (configs + cables), not by Packet Tracer.", "",
          "| From | Ping to | Result | Check |", "|---|---|---|---|"] + rows
    if leases:
        md += ["", "DHCP leases the simulator expects (Packet Tracer may hand them out in a different order):", "",
               "| PC | IP address | Gateway |", "|---|---|---|"] + leases
    if rt:
        md += ["", "Expected routing tables:", "", "```"] + rt + ["```"]
    md += ["", "#### Addressing", "", L.ip_table(), "", "#### Cabling", "", L.cabling_table(), ""]
    open(os.path.join(out, stem + ".results.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md))
    return path, bad, len(exp)


def main():
    failed = 0
    total = 0
    for fn in labs.ALL:
        try:
            path, bad, n = build_one(fn)
        except Exception as e:  # report and keep going
            print("ERROR %s: %r" % (fn.__name__, e))
            failed += 1
            continue
        total += n
        print(("OK    " if not bad else "FAIL  ") + os.path.relpath(path, ROOT) + "  (%d pings checked)" % n)
        for b in bad:
            print("      - " + b)
        failed += bool(bad)
    print("\n%d lab files, %d expected pings, %d failing" % (len(labs.ALL), total, failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
