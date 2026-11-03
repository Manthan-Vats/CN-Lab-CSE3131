"""Show or change the version stamp inside Packet Tracer .pkt files.

Packet Tracer refuses a file whose stamp is NEWER than the copy opening it
("created with a newer version"). Files stamped lower or equal open normally.
This tool rewrites only the top-level <VERSION> tag; nothing else in the file changes.

Usage (standard library only, Python 3):

    python restamp.py --show  FILE_OR_FOLDER
    python restamp.py FILE_OR_FOLDER --version 7.0.0.0000            # edit in place
    python restamp.py FILE_OR_FOLDER --version 8.0.0.0212 --out DIR  # write copies to DIR

A folder is searched recursively for *.pkt.

Which version to use? Open Packet Tracer on the lab PC, Help > About, and read the
number. Any stamp at or below it works. The default, 7.0.0.0000, is below every
Packet Tracer release a lab is likely to run.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptfile  # noqa: E402

DEFAULT = "7.0.0.0000"
TAG = re.compile(rb"<VERSION>([^<]*)</VERSION>")


def find(paths):
    for p in paths:
        if os.path.isdir(p):
            for d, _, fs in os.walk(p):
                for f in sorted(fs):
                    if f.lower().endswith(".pkt"):
                        yield os.path.join(d, f)
        else:
            yield p


def stamp_of(xml):
    """The top-level stamp is the first <VERSION> tag in the document."""
    m = TAG.search(xml)
    return m.group(1).decode() if m else None


def restamp(xml, version):
    """Replace only the first (top-level) <VERSION> tag."""
    m = TAG.search(xml)
    if not m:
        raise ValueError("no <VERSION> tag found")
    return xml[:m.start()] + b"<VERSION>" + version.encode() + b"</VERSION>" + xml[m.end():]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help=".pkt files or folders")
    ap.add_argument("--version", default=DEFAULT, help="stamp to write (default %s)" % DEFAULT)
    ap.add_argument("--out", help="write restamped copies here instead of editing in place")
    ap.add_argument("--show", action="store_true", help="only print each file's stamp")
    a = ap.parse_args()

    if not a.show and not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", a.version):
        sys.exit("version must look like 8.2.0.0162 (four numbers separated by dots)")

    n = 0
    for path in find(a.paths):
        raw = open(path, "rb").read()
        xml = ptfile.decode(raw)
        old = stamp_of(xml)
        if a.show:
            print("%-12s %s" % (old, path))
            continue
        new_raw = ptfile.encode(restamp(xml, a.version))
        # prove nothing but the stamp moved
        if ptfile.decode(new_raw) != restamp(xml, a.version):
            raise AssertionError("round-trip failed for " + path)
        dest = path
        if a.out:
            os.makedirs(a.out, exist_ok=True)
            dest = os.path.join(a.out, os.path.basename(path))
        open(dest, "wb").write(new_raw)
        print("%s -> %s  %s" % (old, a.version, dest))
        n += 1
    if not a.show:
        print("%d file(s) restamped" % n)


if __name__ == "__main__":
    main()
