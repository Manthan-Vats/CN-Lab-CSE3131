"""Read and write Cisco Packet Tracer .pkt files (pure Python, standard library only).

A .pkt file is the topology XML, wrapped like this (scheme documented by the
pka2xml project, github.com/mircodz/pka2xml):

    xml -> [4-byte big-endian length + zlib]   (compress)
        -> byte[i] ^= (n - i)                   (inner obfuscation)
        -> Twofish-EAX, key {137}*16, nonce {16}*16, 16-byte tag appended
        -> reverse bytes, byte[i] ^= (n - i*n)  (outer obfuscation)

Twofish is implemented here from the published specification (Schneier et al.,
1998) and checked against the book's test vectors in self_test().

Usage:
    python ptfile.py decode in.pkt out.xml
    python ptfile.py encode in.xml out.pkt
    python ptfile.py selftest
"""

import struct
import sys
import zlib

# ---------------------------------------------------------------- Twofish

_Q_T = (
    # q0: t0, t1, t2, t3
    ((0x8, 0x1, 0x7, 0xD, 0x6, 0xF, 0x3, 0x2, 0x0, 0xB, 0x5, 0x9, 0xE, 0xC, 0xA, 0x4),
     (0xE, 0xC, 0xB, 0x8, 0x1, 0x2, 0x3, 0x5, 0xF, 0x4, 0xA, 0x6, 0x7, 0x0, 0x9, 0xD),
     (0xB, 0xA, 0x5, 0xE, 0x6, 0xD, 0x9, 0x0, 0xC, 0x8, 0xF, 0x3, 0x2, 0x4, 0x7, 0x1),
     (0xD, 0x7, 0xF, 0x4, 0x1, 0x2, 0x6, 0xE, 0x9, 0xB, 0x3, 0x0, 0x8, 0x5, 0xC, 0xA)),
    # q1: t0, t1, t2, t3
    ((0x2, 0x8, 0xB, 0xD, 0xF, 0x7, 0x6, 0xE, 0x3, 0x1, 0x9, 0x4, 0x0, 0xA, 0xC, 0x5),
     (0x1, 0xE, 0x2, 0xB, 0x4, 0xC, 0x3, 0x7, 0x6, 0xD, 0xA, 0x5, 0xF, 0x9, 0x0, 0x8),
     (0x4, 0xC, 0x7, 0x5, 0x1, 0x6, 0x9, 0xA, 0x0, 0xE, 0xD, 0x8, 0x2, 0xB, 0x3, 0xF),
     (0xB, 0x9, 0x5, 0x1, 0xC, 0x3, 0xD, 0xE, 0x6, 0x4, 0x7, 0xF, 0x2, 0x0, 0x8, 0xA)),
)


def _ror4(x, n):
    return ((x >> n) | (x << (4 - n))) & 0xF


def _make_q(t):
    q = []
    for x in range(256):
        a0, b0 = x >> 4, x & 0xF
        a1 = a0 ^ b0
        b1 = a0 ^ _ror4(b0, 1) ^ ((8 * a0) & 0xF)
        a2, b2 = t[0][a1], t[1][b1]
        a3 = a2 ^ b2
        b3 = a2 ^ _ror4(b2, 1) ^ ((8 * a2) & 0xF)
        a4, b4 = t[2][a3], t[3][b3]
        q.append((b4 << 4) | a4)
    return q


Q0 = _make_q(_Q_T[0])
Q1 = _make_q(_Q_T[1])


def _gf_mul(a, b, poly):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= poly
        b >>= 1
    return r


_MDS = ((0x01, 0xEF, 0x5B, 0x5B),
        (0x5B, 0xEF, 0xEF, 0x01),
        (0xEF, 0x5B, 0x01, 0xEF),
        (0xEF, 0x01, 0xEF, 0x5B))

_RS = ((0x01, 0xA4, 0x55, 0x87, 0x5A, 0x58, 0xDB, 0x9E),
       (0xA4, 0x56, 0x82, 0xF3, 0x1E, 0xC6, 0x68, 0xE5),
       (0x02, 0xA1, 0xFC, 0xC1, 0x47, 0xAE, 0x3D, 0x19),
       (0xA4, 0x55, 0x87, 0x5A, 0x58, 0xDB, 0x9E, 0x03))

M32 = 0xFFFFFFFF


def _rol(x, n):
    return ((x << n) | (x >> (32 - n))) & M32


def _ror(x, n):
    return ((x >> n) | (x << (32 - n))) & M32


def _mds_col(j, y):
    """Contribution of input byte position j with value y to the MDS output word."""
    w = 0
    for i in range(4):
        w |= _gf_mul(_MDS[i][j], y, 0x169) << (8 * i)
    return w


# The q-box chain for each byte position, per key length k (spec section 4.3.2)
_CHAIN = {
    2: ((Q0, Q0, Q1), (Q1, Q0, Q0), (Q0, Q1, Q1), (Q1, Q1, Q0)),
    3: ((Q1, Q0, Q0, Q1), (Q1, Q1, Q0, Q0), (Q0, Q0, Q1, Q1), (Q0, Q1, Q1, Q0)),
    4: ((Q1, Q1, Q0, Q0, Q1), (Q0, Q1, Q1, Q0, Q0), (Q0, Q0, Q0, Q1, Q1), (Q1, Q0, Q1, Q1, Q0)),
}


def _h_byte(j, v, L):
    """The q-box chain for byte position j (before the MDS step)."""
    k = len(L)
    chain = _CHAIN[k][j]
    # chain[0] is applied first and combined with L[k-1]; the last box has no key.
    for step, box in enumerate(chain[:-1]):
        v = box[v] ^ ((L[k - 1 - step] >> (8 * j)) & 0xFF)
    return chain[-1][v]


def _h(x, L):
    """h function: x is a 32-bit word, L a list of k 32-bit words (L[0] .. L[k-1])."""
    w = 0
    for j in range(4):
        w ^= _mds_col(j, _h_byte(j, (x >> (8 * j)) & 0xFF, L))
    return w


class Twofish:
    def __init__(self, key):
        if len(key) not in (16, 24, 32):
            raise ValueError("Twofish key must be 16, 24 or 32 bytes")
        k = len(key) // 8
        words = struct.unpack("<%dI" % (2 * k), key)
        me, mo = list(words[0::2]), list(words[1::2])
        s = []
        for i in range(k):
            m = key[8 * i:8 * i + 8]
            v = 0
            for r in range(4):
                b = 0
                for c in range(8):
                    b ^= _gf_mul(_RS[r][c], m[c], 0x14D)
                v |= b << (8 * r)
            s.append(v)
        s.reverse()  # S = (S_{k-1}, ..., S_0)
        rho = 0x01010101
        self.K = []
        for i in range(20):
            a = _h((2 * i * rho) & M32, me)
            b = _rol(_h(((2 * i + 1) * rho) & M32, mo), 8)
            self.K.append((a + b) & M32)
            self.K.append(_rol((a + 2 * b) & M32, 9))
        # Precompute the key-dependent g() as four 256-entry tables
        # (the MDS step is linear, so g(x) = T0[x0] ^ T1[x1] ^ T2[x2] ^ T3[x3]).
        self.T = [[_mds_col(j, _h_byte(j, v, s)) for v in range(256)] for j in range(4)]

    def _g(self, x):
        T = self.T
        return (T[0][x & 0xFF] ^ T[1][(x >> 8) & 0xFF]
                ^ T[2][(x >> 16) & 0xFF] ^ T[3][x >> 24])

    def encrypt(self, block):
        K, g = self.K, self._g
        r0, r1, r2, r3 = struct.unpack("<4I", block)
        r0 ^= K[0]; r1 ^= K[1]; r2 ^= K[2]; r3 ^= K[3]
        for rnd in range(16):
            t0 = g(r0)
            t1 = g(_rol(r1, 8))
            f0 = (t0 + t1 + K[2 * rnd + 8]) & M32
            f1 = (t0 + 2 * t1 + K[2 * rnd + 9]) & M32
            r2 = _ror(r2 ^ f0, 1)
            r3 = _rol(r3, 1) ^ f1
            r0, r1, r2, r3 = r2, r3, r0, r1
        return struct.pack("<4I", r2 ^ K[4], r3 ^ K[5], r0 ^ K[6], r1 ^ K[7])


def self_test():
    """Twofish book, appendix B.2 (I=3, 128-bit) and the all-zero key vector."""
    vectors = [
        ("00000000000000000000000000000000", "00000000000000000000000000000000",
         "9F589F5CF6122C32B6BFEC2F2AE8C35A"),
        ("9F589F5CF6122C32B6BFEC2F2AE8C35A", "D491DB16E7B1C39E86CB086B789F5419",
         "019F9809DE1711858FAAC3A3BA20FBC3"),
        ("88B2B2706B105E36B446BB6D731A1E88EFA71F788965BD44", "39DA69D6BA4997D585B6DC073CA341B2",
         "182B02D81497EA45F9DAACDC29193A65"),
        ("D43BB7556EA32E46F2A282B7D45B4E0D57FF739D4DC92C1BD7FC01700CC8216F",
         "90AFE91BB288544F2C32DC239B2635E6", "6CB4561C40BF0A9705931CB6D408E7FA"),
    ]
    for key, pt, ct in vectors:
        got = Twofish(bytes.fromhex(key)).encrypt(bytes.fromhex(pt)).hex().upper()
        if got != ct:
            raise AssertionError("Twofish self-test failed: %s != %s" % (got, ct))
    return True


# ---------------------------------------------------------------- EAX (Crypto++ semantics)

def _xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def _dbl(b):
    n = int.from_bytes(b, "big") << 1
    if b[0] & 0x80:
        n ^= 0x87
    return (n & ((1 << 128) - 1)).to_bytes(16, "big")


def _cmac(enc, msg):
    L = enc(bytes(16))
    k1 = _dbl(L)
    if msg and len(msg) % 16 == 0:
        last_key, data = k1, msg
    else:
        last_key = _dbl(k1)
        data = msg + b"\x80" + bytes(15 - len(msg) % 16)
    x = bytes(16)
    for i in range(0, len(data) - 16, 16):
        x = enc(_xor(x, data[i:i + 16]))
    return enc(_xor(_xor(x, data[-16:]), last_key))


def _omac(enc, t, msg):
    return _cmac(enc, bytes(15) + bytes([t]) + msg)


def _ctr(enc, nonce_tag, data):
    out = bytearray()
    ctr = int.from_bytes(nonce_tag, "big")
    for i in range(0, len(data), 16):
        ks = enc(ctr.to_bytes(16, "big"))
        out += _xor(data[i:i + 16], ks)
        ctr = (ctr + 1) & ((1 << 128) - 1)
    return bytes(out)


def eax_seal(enc, nonce, msg):
    n = _omac(enc, 0, nonce)
    ct = _ctr(enc, n, msg)
    tag = _xor(_xor(n, _omac(enc, 1, b"")), _omac(enc, 2, ct))
    return ct + tag


def eax_open(enc, nonce, blob):
    ct, tag = blob[:-16], blob[-16:]
    n = _omac(enc, 0, nonce)
    if _xor(_xor(n, _omac(enc, 1, b"")), _omac(enc, 2, ct)) != tag:
        raise ValueError("EAX tag mismatch: not a valid Packet Tracer file")
    return _ctr(enc, n, ct)


# ---------------------------------------------------------------- Packet Tracer wrapper

_KEY = bytes([137]) * 16
_NONCE = bytes([16]) * 16


def _inner(data):
    n = len(data)
    return bytes(b ^ ((n - i) & 0xFF) for i, b in enumerate(data))


def decode(pkt):
    n = len(pkt)
    sealed = bytes(pkt[n - 1 - i] ^ ((n - i * n) & 0xFF) for i in range(n))
    packed = _inner(eax_open(Twofish(_KEY).encrypt, _NONCE, sealed))
    size = struct.unpack(">I", packed[:4])[0]
    xml = zlib.decompress(packed[4:])
    if len(xml) != size:
        raise ValueError("length header mismatch")
    return xml


def encode(xml):
    packed = struct.pack(">I", len(xml)) + zlib.compress(xml, 6)
    sealed = eax_seal(Twofish(_KEY).encrypt, _NONCE, _inner(packed))
    n = len(sealed)
    out = bytearray(n)
    for i in range(n):
        out[n - 1 - i] = sealed[i] ^ ((n - i * n) & 0xFF)
    return bytes(out)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "selftest":
        self_test()
        print("Twofish self-test OK")
    elif cmd == "decode":
        open(sys.argv[3], "wb").write(decode(open(sys.argv[2], "rb").read()))
    elif cmd == "encode":
        open(sys.argv[3], "wb").write(encode(open(sys.argv[2], "rb").read()))
    else:
        print(__doc__)
