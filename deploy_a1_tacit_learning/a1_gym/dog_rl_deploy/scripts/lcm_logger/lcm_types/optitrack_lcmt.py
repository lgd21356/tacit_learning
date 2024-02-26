"""LCM type definitions
This file automatically generated by lcm.
DO NOT MODIFY BY HAND!!!!
"""

from io import BytesIO
import struct

class optitrack_lcmt(object):
    __slots__ = ["target_pos", "target_yaw", "time", "pos", "rot"]

    __typenames__ = ["float", "float", "float", "float", "float"]

    __dimensions__ = [[2], None, None, [3], [3]]

    def __init__(self):
        self.target_pos = [ 0.0 for dim0 in range(2) ]
        self.target_yaw = 0.0
        self.time = 0.0
        self.pos = [ 0.0 for dim0 in range(3) ]
        self.rot = [ 0.0 for dim0 in range(3) ]

    def encode(self):
        buf = BytesIO()
        buf.write(optitrack_lcmt._get_packed_fingerprint())
        self._encode_one(buf)
        return buf.getvalue()

    def _encode_one(self, buf):
        buf.write(struct.pack('>2f', *self.target_pos[:2]))
        buf.write(struct.pack(">ff", self.target_yaw, self.time))
        buf.write(struct.pack('>3f', *self.pos[:3]))
        buf.write(struct.pack('>3f', *self.rot[:3]))

    def decode(data):
        if hasattr(data, 'read'):
            buf = data
        else:
            buf = BytesIO(data)
        if buf.read(8) != optitrack_lcmt._get_packed_fingerprint():
            raise ValueError("Decode error")
        return optitrack_lcmt._decode_one(buf)
    decode = staticmethod(decode)

    def _decode_one(buf):
        self = optitrack_lcmt()
        self.target_pos = struct.unpack('>2f', buf.read(8))
        self.target_yaw, self.time = struct.unpack(">ff", buf.read(8))
        self.pos = struct.unpack('>3f', buf.read(12))
        self.rot = struct.unpack('>3f', buf.read(12))
        return self
    _decode_one = staticmethod(_decode_one)

    def _get_hash_recursive(parents):
        if optitrack_lcmt in parents: return 0
        tmphash = (0x9befffe2ec0a2f7a) & 0xffffffffffffffff
        tmphash  = (((tmphash<<1)&0xffffffffffffffff) + (tmphash>>63)) & 0xffffffffffffffff
        return tmphash
    _get_hash_recursive = staticmethod(_get_hash_recursive)
    _packed_fingerprint = None

    def _get_packed_fingerprint():
        if optitrack_lcmt._packed_fingerprint is None:
            optitrack_lcmt._packed_fingerprint = struct.pack(">Q", optitrack_lcmt._get_hash_recursive([]))
        return optitrack_lcmt._packed_fingerprint
    _get_packed_fingerprint = staticmethod(_get_packed_fingerprint)

    def get_hash(self):
        """Get the LCM hash of the struct"""
        return struct.unpack(">Q", optitrack_lcmt._get_packed_fingerprint())[0]

