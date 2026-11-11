"""Remove Blender's scene filename PNG text field without changing image chunks."""
import struct
import zlib


def without_scene_filename(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected PNG')
    result = bytearray(data[:8])
    offset = 8
    ended = False
    while offset < len(data):
        length = struct.unpack('>I', data[offset:offset + 4])[0]
        end = offset + length + 12
        if end > len(data):
            raise ValueError('Truncated PNG chunk')
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        crc = struct.unpack('>I', data[end - 4:end])[0]
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ValueError('Invalid PNG CRC')
        remove = kind in {b'tEXt', b'iTXt', b'zTXt'} and payload.split(b'\x00', 1)[0] == b'File'
        if not remove:
            result.extend(data[offset:end])
        offset = end
        if kind == b'IEND':
            ended = True
            break
    if not ended or offset != len(data):
        raise ValueError('Invalid PNG ending')
    return bytes(result)
