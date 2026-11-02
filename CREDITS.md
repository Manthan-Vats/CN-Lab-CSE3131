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
- Files open in Packet Tracer 8.2.1 and newer. If a lab PC says the file is from a newer
  version, update Packet Tracer.
