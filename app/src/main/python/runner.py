"""Android entry point.

`f1mobile_patcher.py` is kept verbatim: all patch offsets, the RSA key and the
signing helpers come from it.  The only thing done differently here is that the
ZIP is rewritten entry by entry and the v2 signature block is appended in place
instead of building the whole APK in memory, so a multi-gigabyte file does not
exhaust a phone's heap.
"""

import base64
import hashlib
import os
import struct
import zipfile
import zlib

import f1mobile_patcher as P

CHUNK = 1024 * 1024
MAX32 = 0xFFFFFFFF


def run(src, dst, progress=None):
    def say(message):
        if progress is not None:
            try:
                progress.emit(str(message))
                return
            except Exception:
                pass
        print(message)

    say('input : %s' % os.path.basename(src))
    with zipfile.ZipFile(src) as zin:
        if P.LIB_ENTRY not in zin.namelist():
            raise ValueError('%s not found in the APK' % P.LIB_ENTRY)
        say('reading %s ...' % P.LIB_ENTRY)
        try:
            patched_lib = P.patch_library(zin.read(P.LIB_ENTRY))
        except SystemExit as exc:
            raise ValueError(str(exc))
        say('libil2cpp.so patched -> %s ...' % hashlib.sha256(patched_lib).hexdigest()[:16])
        say('rebuilding APK ...')
        _rebuild(zin, dst, patched_lib, say)

    say('signing (APK Signature Scheme v2) ...')
    n, e, d = P.load_key(base64.b64decode(P.KEY_PEM_B64).decode('utf-8'))
    _sign_v2(dst, n, e, d, base64.b64decode(P.CERT_DER_B64))
    say('done: %.1f MB' % (os.path.getsize(dst) / 1048576.0))
    return dst


# ---------------------------------------------------------------- zip writer


def _align_extra(header_end, name):
    """Padding so that stored data starts aligned (like zipalign -p 4)."""
    alignment = 4096 if name.endswith('.so') else 4
    pad = (-(header_end + 4)) % alignment
    return struct.pack('<HH', 0x0000, pad) + b'\x00' * pad


def _copy_file(path, out):
    with open(path, 'rb') as f:
        while True:
            blob = f.read(CHUNK)
            if not blob:
                return
            out.write(blob)


def _copy_raw(zin, info, out):
    """Copy an entry's already-compressed bytes without decompressing them."""
    f = zin.fp
    f.seek(info.header_offset)
    header = f.read(30)
    if len(header) != 30 or header[:4] != b'PK\x03\x04':
        raise ValueError('bad local header for %s' % info.filename)
    name_len, extra_len = struct.unpack_from('<HH', header, 26)
    f.seek(info.header_offset + 30 + name_len + extra_len)
    left = info.compress_size
    while left > 0:
        blob = f.read(min(CHUNK, left))
        if not blob:
            raise ValueError('truncated entry %s' % info.filename)
        out.write(blob)
        left -= len(blob)


def _deflate_to_file(data, path):
    comp = zlib.compressobj(6, zlib.DEFLATED, -15)
    size = 0
    with open(path, 'wb') as f:
        for start in range(0, len(data), CHUNK):
            blob = comp.compress(data[start:start + CHUNK])
            if blob:
                f.write(blob)
                size += len(blob)
        blob = comp.flush()
        f.write(blob)
        size += len(blob)
    return size, path


def _rebuild(zin, dst, patched_lib, say):
    entries = [i for i in zin.infolist() if i.filename not in P.DROP_ENTRIES]
    total = len(entries)
    central = bytearray()
    spare = dst + '.part'
    with open(dst, 'wb') as out:
        for index, info in enumerate(entries, 1):
            name = info.filename
            name_b = name.encode('utf-8')
            method = info.compress_type
            if method not in (0, 8):
                raise ValueError('unsupported compression method %d for %s' % (method, name))
            flags = 0x800 if any(ord(c) > 127 for c in name) else 0
            hour, day = P._dos_time(info.date_time)
            offset = out.tell()
            extra = b''
            if method == 0 and not name.endswith('/'):
                extra = _align_extra(offset + 30 + len(name_b), name)

            payload = None
            if name == P.LIB_ENTRY:
                crc = zlib.crc32(patched_lib) & MAX32
                usize = len(patched_lib)
                if method == 8:
                    csize, payload = _deflate_to_file(patched_lib, spare)
                else:
                    csize = usize
            else:
                crc, csize, usize = info.CRC, info.compress_size, info.file_size

            if csize > MAX32 or usize > MAX32:
                raise ValueError('%s is too large for a non-ZIP64 APK' % name)

            out.write(struct.pack('<IHHHHHIIIHH', 0x04034B50, 20, flags, method,
                                  hour, day, crc, csize, usize, len(name_b), len(extra)))
            out.write(name_b)
            out.write(extra)
            if payload is not None:
                _copy_file(payload, out)
                os.remove(payload)
            elif name == P.LIB_ENTRY:
                for start in range(0, usize, CHUNK):
                    out.write(patched_lib[start:start + CHUNK])
            else:
                _copy_raw(zin, info, out)

            central += struct.pack('<IHHHHHHIIIHHHHHII', 0x02014B50, 20, 20, flags, method,
                                   hour, day, crc, csize, usize, len(name_b), len(extra),
                                   0, 0, 0, info.external_attr, offset)
            central += name_b + extra
            if index % 25 == 0 or index == total:
                say('  packed %d/%d entries' % (index, total))

        cd_offset = out.tell()
        if cd_offset + len(central) + 22 > MAX32:
            raise ValueError('output APK would exceed the 4 GB ZIP limit')
        out.write(central)
        out.write(struct.pack('<IHHHHIIH', 0x06054B50, 0, 0, total, total,
                              len(central), cd_offset, 0))


# ------------------------------------------------------------ v2 signing


def _content_digest(f, size, cd_offset, cd_end):
    chunks = []
    for start, end in ((0, cd_offset), (cd_offset, cd_end), (cd_end, size)):
        f.seek(start)
        left = end - start
        while left > 0:
            data = f.read(min(CHUNK, left))
            if not data:
                raise ValueError('truncated APK')
            left -= len(data)
            chunks.append(hashlib.sha256(b'\xa5' + struct.pack('<I', len(data)) + data).digest())
    return hashlib.sha256(b'\x5a' + struct.pack('<I', len(chunks)) + b''.join(chunks)).digest()


def _sign_v2(path, n, e, d, cert_der):
    with open(path, 'r+b') as f:
        size = f.seek(0, 2)
        tail_len = min(size, 0xFFFF + 22)
        f.seek(size - tail_len)
        tail = f.read()
        pos = tail.rfind(b'PK\x05\x06')
        while pos != -1:
            comment_len = struct.unpack_from('<H', tail, pos + 20)[0]
            if size - tail_len + pos + 22 + comment_len == size:
                break
            pos = tail.rfind(b'PK\x05\x06', 0, pos)
        if pos == -1:
            raise ValueError('EOCD not found - is this a valid APK/ZIP?')

        eocd_pos = size - tail_len + pos
        cd_size, cd_offset = struct.unpack_from('<II', tail, pos + 12)
        cd_end = cd_offset + cd_size

        digest = _content_digest(f, size, cd_offset, cd_end)

        public_key = P.rsa_public_key_der(n, e)
        digest_entry = struct.pack('<I', P.SIG_ALG_RSA_PKCS1_SHA256) + P._lp(digest)
        signed_data = P._lp(P._lp(digest_entry)) + P._lp(P._lp(cert_der)) + P._lp(b'')
        signature = P.rsa_sign_sha256(signed_data, n, d)
        sig_entry = struct.pack('<I', P.SIG_ALG_RSA_PKCS1_SHA256) + P._lp(signature)
        signer = P._lp(signed_data) + P._lp(P._lp(sig_entry)) + P._lp(public_key)
        value = P._lp(P._lp(signer))

        pair = struct.pack('<Q', 4 + len(value)) + struct.pack('<I', P.V2_BLOCK_ID) + value
        block_len = 8 + len(pair) + 8 + 16
        block = (struct.pack('<Q', block_len - 8) + pair
                 + struct.pack('<Q', block_len - 8) + P.APK_SIG_BLOCK_MAGIC)
        assert len(block) == block_len

        f.seek(cd_offset)
        rest = bytearray(f.read())
        struct.pack_into('<I', rest, eocd_pos - cd_offset + 16, cd_offset + len(block))
        f.seek(cd_offset)
        f.write(block)
        f.write(rest)
        f.truncate()
