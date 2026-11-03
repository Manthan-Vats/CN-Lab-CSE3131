# Credits and notes

- **.pkt file format:** the encryption/compression scheme was documented by
  [mircodz/pka2xml](https://github.com/mircodz/pka2xml). `tools/ptfile.py` is an independent
  pure-Python implementation of it (Twofish written from the specification, checked against
  the published test vectors). No third-party code is included or executed.
- **Device templates:** the default device XML in `tools/templates/` was taken from
  Packet Tracer 8.2.1 saves in
  [Thuy-Hung/Cisco-Packet-Tracer-Labs-for-CCNA](https://github.com/Thuy-Hung/Cisco-Packet-Tracer-Labs-for-CCNA)
  and reset (names, addresses, configs) for each lab.
- Cisco and Packet Tracer are trademarks of Cisco Systems, Inc. This is an unofficial student
  repository for the CSE3131 Computer Networks lab, made for learning.
- The device blocks come from 8.2.1 saves, but every file is stamped `7.0.0.0000` so older
  Packet Tracer copies accept it (they refuse files stamped newer than themselves). The saved
  configs use only basic IOS commands that exist on every Packet Tracer 7.x to 9.x image.
  This was checked by decoding the files; it has not been tested inside every Packet Tracer
  release. If a lab PC still refuses a file, see `tools/restamp.py` and HOW_TO_RUN.md.
