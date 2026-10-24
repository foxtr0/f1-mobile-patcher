#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F1 Mobile Racing 5.4.11 - offline patch builder (v40)

Takes YOUR OWN original com.codemasters.F1Mobile 5.4.11 APK and produces a
patched, re-signed APK that runs offline with:

  * no network error on startup, offline profile
  * PLAY -> original hub (Events / Duel / Showdown / Career)
  * Duel tile -> offline single-race setup (track / race type / laps / difficulty)
  * in-race settings menu no longer freezes the race
  * Graphics quality row in Game Options -> Preferences
  * maximum quality: Q100 profile, native render resolution, 60 FPS
  * 2048px directional shadow cascades
  * career step/contract screen reachable (signing itself needs the dead server)

Only lib/arm64-v8a/libil2cpp.so is modified (70 instruction patches).
Nothing from the original APK is redistributed: the input file is required.

Usage
-----
    python f1mobile_patcher.py com.codemasters.F1Mobile_5.4.11.apk
    python f1mobile_patcher.py <input.apk> -o <output.apk>

Requires Python 3.8+ (standard library only - no Java, no Android SDK).

The output is signed with an APK Signature Scheme v2 key embedded in this
script, which is NOT EA's key, so the phone must not have the store version
installed: uninstall it first (back up the OBB, see README.md).
"""

import sys, os, struct, zlib, hashlib, base64

ORIGINAL_SHA256 = "90ae142fa1ed5e81946c8b5624552007f3d6770f404a51773eba4192639c9b82"
PATCHED_SHA256 = "e6667708bc0da737ec34a15d9742d17f0a00861c43e5717cba3a1e71056ecdd3"
LIB_ENTRY = "lib/arm64-v8a/libil2cpp.so"
DROP_ENTRIES = ("META-INF/CERT.RSA", "META-INF/CERT.SF", "META-INF/MANIFEST.MF")

# (file offset in libil2cpp.so, replacement bytes)
PATCHES = [
    (0x1C151C8, bytes.fromhex("20008052")),
    (0x1E69258, bytes.fromhex("20008052")),
    (0x1E6925C, bytes.fromhex("c0035fd6")),
    (0x1E6A30C, bytes.fromhex("93078052")),
    (0x1E6B7A8, bytes.fromhex("b6253f14")),
    (0x1E6BDE4, bytes.fromhex("800c8052")),
    (0x1E6BDE8, bytes.fromhex("c0035fd6")),
    (0x1EADF74, bytes.fromhex("16008152")),
    (0x27AFBEC, bytes.fromhex("c0035fd6")),
    (0x27E5E38, bytes.fromhex("08000014")),
    (0x27ED714, bytes.fromhex("07010014")),
    (0x27EDB10, bytes.fromhex("1f2003d5")),
    (0x27EDBDC, bytes.fromhex("28008052")),
    (0x27EDCA8, bytes.fromhex("28008052")),
    (0x27EDCF4, bytes.fromhex("28008052")),
    (0x27F5A84, bytes.fromhex("28008052")),
    (0x285AAB0, bytes.fromhex("28008052")),
    (0x285AC34, bytes.fromhex("28008052")),
    (0x285AFD0, bytes.fromhex("28008052")),
    (0x287E49C, bytes.fromhex("28008052")),
    (0x29187A8, bytes.fromhex("930100b4")),
    (0x29187B0, bytes.fromhex("480100b4")),
    (0x29187B8, bytes.fromhex("080100b4")),
    (0x29187D0, bytes.fromhex("41000054")),
    (0x2918838, bytes.fromhex("140400b4")),
    (0x2918840, bytes.fromhex("c80300b4")),
    (0x2918850, bytes.fromhex("540300b4")),
    (0x2950E00, bytes.fromhex("f4031f2a")),
    (0x29523F0, bytes.fromhex("f3881314")),
    (0x29612C8, bytes.fromhex("28008052")),
    (0x296138C, bytes.fromhex("01000014")),
    (0x296BE60, bytes.fromhex("c0035fd6")),
    (0x2988900, bytes.fromhex("20008052")),
    (0x2988904, bytes.fromhex("c0035fd6")),
    (0x29AB8DC, bytes.fromhex("20008052")),
    (0x29AB8E0, bytes.fromhex("c0035fd6")),
    (0x29ACAB0, bytes.fromhex("600c8052")),
    (0x29ACAB4, bytes.fromhex("c0035fd6")),
    (0x29E9A74, bytes.fromhex("1f2003d5")),
    (0x29E9C9C, bytes.fromhex("c0035fd6")),
    (0x29EA1DC, bytes.fromhex("782a1114")),
    (0x29ECCCC, bytes.fromhex("c0035fd6")),
    (0x29EE060, bytes.fromhex("c0035fd6")),
    (0x29EE7EC, bytes.fromhex("c0035fd6")),
    (0x29F32A4, bytes.fromhex("40008052")),
    (0x2BCF148, bytes.fromhex("28008052")),
    (0x2C05060, bytes.fromhex("c0035fd6")),
    (0x2C3B0A0, bytes.fromhex("28008052")),
    (0x2C471D4, bytes.fromhex("c0035fd6")),
    (0x2CA1B8C, bytes.fromhex("0c000014")),
    (0x2CA37DC, bytes.fromhex("c0035fd6")),
    (0x2CA3864, bytes.fromhex("01008052")),
    (0x2CBB980, bytes.fromhex("00008052")),
    (0x2CBB984, bytes.fromhex("c0035fd6")),
    (0x2CD1F90, bytes.fromhex("c0035fd6")),
    (0x2CD83E0, bytes.fromhex("00008052")),
    (0x2CD83E4, bytes.fromhex("c0035fd6")),
    (0x2CD8BA4, bytes.fromhex("27700514")),
    (0x2D9CCD8, bytes.fromhex("1f2003d5")),
    (0x2E347BC, bytes.fromhex("ff8301d1fd7b02a9f35303a9f55b04a9f76305a9fd030091f30300aa75e240b976e640b977ea40b978ee40b9ff0600714a000054770080521f0300714a00005438008052df0200714a000054d6008052149e00d094da42f9e00314aa002a7b97800240f9784e0b94200300b4f40300aa15020035e00314aae451f897e00314aaeb51f897e00314aa1a53f897000200b4091840b9c9010034090840f9890100b4291140f9490100b4351140b915010034e00314aae103152a22068052e303162ae403172ae503182af553f897f76345a9f55b44a9f35343a9fd7b42a9ff830191c0035fd6")),
    (0x2E34BBC, bytes.fromhex("fd7bbea9fd030091f35301a9f39a009073f246f9680240f9085d40f9080140f9080100b4002940f9c00000b4810080522200805223008052e4031faa8a61ff97f35341a9fd7bc2a8c0035fd6")),
    (0x2E34C40, bytes.fromhex("fd7bbca9fd030091f35301a9f55b02a9f30300aa149e00f0943e44f9800240f9684d0b94400100b4f40300aae00314aae8baf9979fc200b99ff600b96800805288b200b92800805288a60239689d00d0082547f9000140f92ae4bc97a00000b408f0a7520001271ee1031faa6726a69708f0a7520001271ee0031faa9ea29a97e00313aa0a8ffa97f55b42a9f35341a9fd7bc4a8c0035fd6")),
    (0x2E34E80, bytes.fromhex("e00302aae10303aac0035fd6")),
    (0x2ED3DF0, bytes.fromhex("1f2003d5")),
    (0x2F1386C, bytes.fromhex("28008052")),
    (0x2F22698, bytes.fromhex("28008052")),
    (0x2F23154, bytes.fromhex("28008052")),
    (0x2F23570, bytes.fromhex("28008052")),
    (0x2F24020, bytes.fromhex("28008052")),
    (0x2FFA90C, bytes.fromhex("28008052")),
]

KEY_PEM_B64 = (
    "QmFnIEF0dHJpYnV0ZXMKICAgIGZyaWVuZGx5TmFtZTogZjFvZmZsaW5lCiAgICBsb2NhbEtleUlE"
    "OiA1NCA2OSA2RCA2NSAyMCAzMSAzNyAzOSAzMiAzNiAzOCAzNSAzMyAzNSAzMSAzOCAzMCAzMiAK"
    "S2V5IEF0dHJpYnV0ZXM6IDxObyBBdHRyaWJ1dGVzPgotLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0t"
    "LS0KTUlJRXZRSUJBREFOQmdrcWhraUc5dzBCQVFFRkFBU0NCS2N3Z2dTakFnRUFBb0lCQVFEUEpx"
    "TjFBR0l5TWxFdwpVQVhBTUVSOEZQdGZvMER6bWdsZEhlS0MxOVpBTWl1YVd5WVpKT3JoVUNPSnFJ"
    "RHhqdmNWd1JWYkFnRzYzSmZOClUrUkN6Zlh3TVI1QTQ1UEQwYXNUS2FkQ293NE9Nb01wUWQ2SHVM"
    "eW1Pc0JOWTB6Tmp6TUU5U09xckE4NVZTTnoKQTlDMnhzNWR0MjZKWmNqMzNTb1c3U2NQZ3R1QjBB"
    "azV6K3JKMjNhV0FTeGNocmpncEI5d2prbkcyYzArRWxwVgp2M3hGWEozMUdJckU5bDVlOG13K0FH"
    "Ync2L2ZxQjg2VmJMNkhpNDFLb3BLUXl3OHN0bmZaeWZIUXpucUloamZ5ClZKVndkODFKUm03aVk3"
    "UFllUkVwbjJiSG5sMVNsaDhlSmJKOXh1eXpza1k3NXlOZTM5dWtNcUVCNjE2cmhCM1cKWlJpaW51"
    "N1pBZ01CQUFFQ2dnRUFBNnppMHh1Ym9taVY2aTZHbnladDNSUmxWVjVJN0o3ZlhNVUhGTTcveEVL"
    "MAo4NUI3amNrWkhxUFVsTEpYNHVNVEIrQ09rbFN2SGcvMTVLYWRaTG1ZVXlYZmdkL2tQNXJaRUJT"
    "SUhSSUFwdytjClh3WjMwNEl3enF4eUxoOFo2TDdma2FPNkI3Z3VBNks2dlJBQkMzQ3pWYjhBYTJh"
    "TEIwWlpuQXdVZFFEL0I4NEIKQTNjWERxbmJCcTdHN1Y1UTVsOC9BeEZDYzlQNUR0MnJmL1BpeEMr"
    "VVRBaFRBTDlYV3VpKzNYRENkdi92OVFKQwo0YmlvYWVMcjg2UXJLS3BYbDExNkwrNytjWnRpcmpC"
    "eUJWRXppdGxQVEJBcWEvMkI4ZlJPMGFtRWRsLzgwV0k2CkxmZERVbU5Qek9WQnpodk1MV2Z5czNU"
    "U0N3bFpKd3FEejNZVjNEcTlSUUtCZ1FEK3pHLzNxejg2Z3JsQmN3V20KMFkrVzFULzY4UHdkcDZv"
    "cC8wWjJXdlhVamZjV0ZDanRUTDQveUUvODFLRWM3UHJQSlZ1VFprOFVFdVlmbW9yZgpYY1FoNkp3"
    "VGhqTzVKMFR5d0ZMcmh1Q25VUmR1N3lQa3BiNU1VeEY0bWVuaFVmc0Qyd2ZnRlVvMFYxSHRnSHVi"
    "CmlsUWRSSnpHMkNBK0VwUmg0M2o3T2VJcm93S0JnUURRSUsvQTdZaURTaGlGbExacHdKS0hYUW01"
    "Rk1tbTEwcmcKS05Cd3hzZ0tpTHBLS0xjYisvNkE5ZzJXcVNnZzBQaGdKRTlybDBxeWlCNHIrOTFa"
    "eHU2cXdzNnMwWHE0T2duUgpCcnQ4dmwrUDFaMHh4VG56M1JSZ1FVSldtNi9xbHNWc3h4Rk9vZFdt"
    "RnpWUFFnMGRwSVhaWFVUWVF4K3psSWgyCk5pc1BPWmFqVXdLQmdRREJERGZSR0VnaGxxV3h0dW9U"
    "U0RkWWVsMnRUU1JYZTQ3cm51UE9ESUN3K0phNmZhKzgKaXlhaHdLMEp6RGY5YUhkbXR0RTVUb3lm"
    "a3VvVUM4MG9DeXpzM0FaVXJKdEhyejhJQlR0T0E3VDJUL1JITXB5cApRZ0o2WlgyWk9GUUJTVkc3"
    "ekJtZFo4UC9BQ0dzcG1vQW9MKzJKU1A3YkFpUnZ4WDVUSlYvRW80UHJRS0JnQ0loCitqRHR3OEdr"
    "V1RrdkZtdHBoWjVsaDc2dXhoTnlvM2ozdUplR1FqQllGQlV0Y0RwS3JZYUEwK0d0aEVNOWdqNWkK"
    "TmhRekQ3RVAyY0xrMzN4bHY2YUpwRk43VjJEM1E3emdHY2R2Z1VTWmg5b3R1ajlnTm9OQ3NKcDds"
    "ZkluSCtHagpGQmVOT3ZpdVBiUHQ1VEREVnFBN1I1c2dCd2J3aVNDNTZYM3B0K2E1QW9HQVBLQ0Fq"
    "a1Y0QXJvYzltaU5Va05JCk1vR1FkWWw3S2g3UGdMLzloWWdXV21SckM1QWxhallOWHkrSGRkSXMx"
    "N0R4Q1E4Z1BxbG5CZ3RxM29GdGpnaFMKRFBwOFdGVGZiVDVvUzQvNGVHVHhSQVUwUjJiQy9kZFJh"
    "T3ZuYi95TDNFNXhqbWJwTThMYjZySS9BWUZka3A0dgpjNkxrcnl0am9Bakc4bnA3enlWNEZWdz0K"
    "LS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLQpCYWcgQXR0cmlidXRlcwogICAgZnJpZW5kbHlOYW1l"
    "OiBmMW9mZmxpbmUKICAgIGxvY2FsS2V5SUQ6IDU0IDY5IDZEIDY1IDIwIDMxIDM3IDM5IDMyIDM2"
    "IDM4IDM1IDMzIDM1IDMxIDM4IDMwIDMyIApzdWJqZWN0PUM9VVMsIE89TG9jYWwsIENOPUYxIE9m"
    "ZmxpbmUgUGF0Y2gKaXNzdWVyPUM9VVMsIE89TG9jYWwsIENOPUYxIE9mZmxpbmUgUGF0Y2gKLS0t"
    "LS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURGVENDQWYyZ0F3SUJBZ0lJSHVKclI2RmdjSmN3"
    "RFFZSktvWklodmNOQVFFTUJRQXdPREVMTUFrR0ExVUUKQmhNQ1ZWTXhEakFNQmdOVkJBb1RCVXh2"
    "WTJGc01Sa3dGd1lEVlFRREV4QkdNU0JQWm1ac2FXNWxJRkJoZEdObwpNQ0FYRFRJMk1UQXlNakUy"
    "TURreE1Wb1lEekl3TlRRd016QTVNVFl3T1RFeFdqQTRNUXN3Q1FZRFZRUUdFd0pWClV6RU9NQXdH"
    "QTFVRUNoTUZURzlqWVd3eEdUQVhCZ05WQkFNVEVFWXhJRTltWm14cGJtVWdVR0YwWTJnd2dnRWkK"
    "TUEwR0NTcUdTSWIzRFFFQkFRVUFBNElCRHdBd2dnRUtBb0lCQVFEUEpxTjFBR0l5TWxFd1VBWEFN"
    "RVI4RlB0ZgpvMER6bWdsZEhlS0MxOVpBTWl1YVd5WVpKT3JoVUNPSnFJRHhqdmNWd1JWYkFnRzYz"
    "SmZOVStSQ3pmWHdNUjVBCjQ1UEQwYXNUS2FkQ293NE9Nb01wUWQ2SHVMeW1Pc0JOWTB6Tmp6TUU5"
    "U09xckE4NVZTTnpBOUMyeHM1ZHQyNkoKWmNqMzNTb1c3U2NQZ3R1QjBBazV6K3JKMjNhV0FTeGNo"
    "cmpncEI5d2prbkcyYzArRWxwVnYzeEZYSjMxR0lyRQo5bDVlOG13K0FHYnc2L2ZxQjg2VmJMNkhp"
    "NDFLb3BLUXl3OHN0bmZaeWZIUXpucUloamZ5VkpWd2Q4MUpSbTdpClk3UFllUkVwbjJiSG5sMVNs"
    "aDhlSmJKOXh1eXpza1k3NXlOZTM5dWtNcUVCNjE2cmhCM1daUmlpbnU3WkFnTUIKQUFHaklUQWZN"
    "QjBHQTFVZERnUVdCQlJZNzZTZzR2UTdndFhmdHRyUHVUMzlwTUp3M1RBTkJna3Foa2lHOXcwQgpB"
    "UXdGQUFPQ0FRRUFscXlJMW9EMTRSTWlXVWNzeDkxU2pMOFpzVU9oSGRBSTE4U2w0M2NOczFoUklz"
    "MjdMa0svCm83MUxGRXA4ZnRTamRxTmkwRkl0SjlSaGxiQlQ3MXNMY05yV2pxZUM2Zkx2SzdaUk95"
    "Tmw1N0o3Y2ZrdWxDVGkKeHA2OE1qck1aak9vSWh1ODllMWhtOGpoVTU1NHN3NGRmOUoyN2VPNVlu"
    "MWdGaGpBYXJGb3VWNktsV2pMTW5hdApyY3pKbkh1ZTdFdllOcXp4eXdLa01uQVpzV1VNMDFBSXBu"
    "YTM5dmdtcllhZGYvOTI5cmlpVXFoWk53NGFlbmFECldVa2poem9ZN2FEZHBQOWxFeThwOFdtTmQx"
    "WTZ6cW44Mkw1RXlLVVZGREpxMkhrQUxtVXBJbTd2YUZSV3hoSG4KdHpmOGVQQnhQN2QyZkY2eE5H"
    "UWNKMzdQUUJ5YkNONlNEdz09Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K"
)

CERT_DER_B64 = (
    "MIIDFTCCAf2gAwIBAgIIHuJrR6FgcJcwDQYJKoZIhvcNAQEMBQAwODELMAkGA1UEBhMCVVMxDjAM"
    "BgNVBAoTBUxvY2FsMRkwFwYDVQQDExBGMSBPZmZsaW5lIFBhdGNoMCAXDTI2MTAyMjE2MDkxMVoY"
    "DzIwNTQwMzA5MTYwOTExWjA4MQswCQYDVQQGEwJVUzEOMAwGA1UEChMFTG9jYWwxGTAXBgNVBAMT"
    "EEYxIE9mZmxpbmUgUGF0Y2gwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDPJqN1AGIy"
    "MlEwUAXAMER8FPtfo0DzmgldHeKC19ZAMiuaWyYZJOrhUCOJqIDxjvcVwRVbAgG63JfNU+RCzfXw"
    "MR5A45PD0asTKadCow4OMoMpQd6HuLymOsBNY0zNjzME9SOqrA85VSNzA9C2xs5dt26JZcj33SoW"
    "7ScPgtuB0Ak5z+rJ23aWASxchrjgpB9wjknG2c0+ElpVv3xFXJ31GIrE9l5e8mw+AGbw6/fqB86V"
    "bL6Hi41KopKQyw8stnfZyfHQznqIhjfyVJVwd81JRm7iY7PYeREpn2bHnl1Slh8eJbJ9xuyzskY7"
    "5yNe39ukMqEB616rhB3WZRiinu7ZAgMBAAGjITAfMB0GA1UdDgQWBBRY76Sg4vQ7gtXfttrPuT39"
    "pMJw3TANBgkqhkiG9w0BAQwFAAOCAQEAlqyI1oD14RMiWUcsx91SjL8ZsUOhHdAI18Sl43cNs1hR"
    "Is27LkK/o71LFEp8ftSjdqNi0FItJ9RhlbBT71sLcNrWjqeC6fLvK7ZROyNl57J7cfkulCTixp68"
    "MjrMZjOoIhu89e1hm8jhU554sw4df9J27eO5Yn1gFhjAarFouV6KlWjLMnatrczJnHue7EvYNqzx"
    "ywKkMnAZsWUM01AIpna39vgmrYadf/929riiUqhZNw4aenaDWUkjhzoY7aDdpP9lEy8p8WmNd1Y6"
    "zqn82L5EyKUVFDJq2HkALmUpIm7vaFRWxhHntzf8ePBxP7d2fF6xNGQcJ37PQBybCN6SDw=="
)

# ---------------------------------------------------------------------------
# ASN.1 / RSA (pure Python, stdlib only)
# ---------------------------------------------------------------------------

def _der_len(n):
    if n < 0x80:
        return bytes([n])
    b = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    return bytes([0x80 | len(b)]) + b


def _tlv(tag, content):
    return bytes([tag]) + _der_len(len(content)) + content


def _der_int(i):
    if i == 0:
        return _tlv(0x02, b'\x00')
    b = i.to_bytes((i.bit_length() + 7) // 8, 'big')
    if b[0] & 0x80:
        b = b'\x00' + b
    return _tlv(0x02, b)


def _read_tlv(data, pos):
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 0x80:
        n = length & 0x7F
        length = int.from_bytes(data[pos:pos + n], 'big')
        pos += n
    return tag, data[pos:pos + length], pos + length


def load_key(pem_text):
    """Parse a PKCS#8 PEM RSA private key -> (n, e, d)."""
    begin = pem_text.index('-----BEGIN')
    end = pem_text.index('-----END')
    block = pem_text[begin:end]
    b64 = ''.join(block.splitlines()[1:]).strip()
    der = base64.b64decode(b64)
    _, pkcs8, _ = _read_tlv(der, 0)
    pos = 0
    _, version, pos = _read_tlv(pkcs8, pos)
    _, alg, pos = _read_tlv(pkcs8, pos)
    _, octets, pos = _read_tlv(pkcs8, pos)
    _, rsa, _ = _read_tlv(octets, 0)
    pos = 0
    ints = []
    while pos < len(rsa):
        _, val, pos = _read_tlv(rsa, pos)
        ints.append(int.from_bytes(val, 'big'))
    return ints[1], ints[2], ints[3]


def rsa_public_key_der(n, e):
    rsa_pub = _tlv(0x30, _der_int(n) + _der_int(e))
    alg = _tlv(0x30, bytes.fromhex('06092a864886f70d010101') + b'\x05\x00')
    return _tlv(0x30, alg + _tlv(0x03, b'\x00' + rsa_pub))


def rsa_sign_sha256(message, n, d):
    digest = hashlib.sha256(message).digest()
    digest_info = bytes.fromhex('3031300d060960864801650304020105000420') + digest
    k = (n.bit_length() + 7) // 8
    em = b'\x00\x01' + b'\xff' * (k - len(digest_info) - 3) + b'\x00' + digest_info
    return pow(int.from_bytes(em, 'big'), d, n).to_bytes(k, 'big')


# ---------------------------------------------------------------------------
# APK Signature Scheme v2
# ---------------------------------------------------------------------------

SIG_ALG_RSA_PKCS1_SHA256 = 0x0103
DIGEST_ALG_CHUNKED_SHA256 = 0x0101
V2_BLOCK_ID = 0x7109871A
APK_SIG_BLOCK_MAGIC = b'APK Sig Block 42'
CHUNK = 1024 * 1024


def _lp(data):
    return struct.pack('<I', len(data)) + data


def _content_digest(*sections):
    """apksig chunked content digest: one continuous chunk stream over the three
    ZIP sections, prefixed by 0x5a + total chunk count."""
    chunks = []
    for section in sections:
        for i in range(0, len(section), CHUNK):
            chunk = section[i:i + CHUNK]
            chunks.append(hashlib.sha256(b'\xa5' + struct.pack('<I', len(chunk)) + chunk).digest())
    return hashlib.sha256(b'\x5a' + struct.pack('<I', len(chunks)) + b''.join(chunks)).digest()


def _find_eocd(data):
    sig = b'PK\x05\x06'
    limit = max(0, len(data) - 0xFFFF - 22)
    pos = data.rfind(sig, limit)
    while pos != -1:
        comment_len = struct.unpack_from('<H', data, pos + 20)[0]
        if pos + 22 + comment_len == len(data):
            return pos
        pos = data.rfind(sig, limit, pos)
    raise ValueError('EOCD not found - is this a valid APK/ZIP?')


def sign_v2(apk, n, e, d, cert_der):
    """Insert an APK Signature Scheme v2 block, return the signed APK."""
    eocd_pos = _find_eocd(apk)
    cd_size, cd_offset = struct.unpack_from('<II', apk, eocd_pos + 12)
    cd_end = cd_offset + cd_size

    # Digests are computed on the APK *before* the signing block exists, so the
    # EOCD here still carries the unshifted central-directory offset.
    content_digest = _content_digest(apk[:cd_offset], apk[cd_offset:cd_end], apk[cd_end:])

    public_key = rsa_public_key_der(n, e)
    digest_entry = struct.pack('<I', SIG_ALG_RSA_PKCS1_SHA256) + _lp(content_digest)
    signed_data = _lp(_lp(digest_entry)) + _lp(_lp(cert_der)) + _lp(b'')
    signature = rsa_sign_sha256(signed_data, n, d)
    sig_entry = struct.pack('<I', SIG_ALG_RSA_PKCS1_SHA256) + _lp(signature)
    signer = _lp(signed_data) + _lp(_lp(sig_entry)) + _lp(public_key)
    value = _lp(_lp(signer))

    pair = struct.pack('<Q', 4 + len(value)) + struct.pack('<I', V2_BLOCK_ID) + value
    block_len = 8 + len(pair) + 8 + 16
    block = (struct.pack('<Q', block_len - 8) + pair
             + struct.pack('<Q', block_len - 8) + APK_SIG_BLOCK_MAGIC)
    assert len(block) == block_len, (len(block), block_len)

    eocd = bytearray(apk[cd_end:])
    struct.pack_into('<I', eocd, 16, cd_offset + block_len)
    return apk[:cd_offset] + block + apk[cd_offset:cd_end] + bytes(eocd)


# ---------------------------------------------------------------------------
# ZIP writer (4-byte aligns stored entries, like zipalign)
# ---------------------------------------------------------------------------

def _dos_time(dt):
    y, mo, d, h, mi, s = dt
    return ((h << 11) | (mi << 5) | (s // 2)), (((y - 1980) << 9) | (mo << 5) | d)


def write_zip(entries, out_path):
    out = bytearray()
    central = bytearray()
    for name, method, data, dt, ext_attr in entries:
        name_b = name.encode('utf-8')
        flags = 0x800 if any(ord(ch) > 127 for ch in name) else 0
        crc = zlib.crc32(data) & 0xFFFFFFFF
        if method == 8:
            co = zlib.compressobj(6, zlib.DEFLATED, -15)
            payload = co.compress(data) + co.flush()
        elif method == 0:
            payload = data
        else:
            raise ValueError('unsupported compression method %d for %s' % (method, name))
        t, d = _dos_time(dt)
        extra = b''
        if method == 0:
            pad = (-(len(out) + 30 + len(name_b))) % 4
            if pad:
                if pad < 4:
                    pad += 4
                extra = struct.pack('<HH', 0x0000, pad - 4) + b'\x00' * (pad - 4)
        offset = len(out)
        out += struct.pack('<IHHHHHIIIHH', 0x04034B50, 20, flags, method, t, d,
                           crc, len(payload), len(data), len(name_b), len(extra))
        out += name_b + extra + payload
        central += struct.pack('<IHHHHHHIIIHHHHHII', 0x02014B50, 20, 20, flags, method, t, d,
                               crc, len(payload), len(data), len(name_b), len(extra), 0, 0, 0,
                               ext_attr, offset)
        central += name_b + extra
    cd_offset = len(out)
    out += central
    out += struct.pack('<IHHHHIIH', 0x06054B50, 0, 0, len(entries), len(entries),
                       len(central), cd_offset, 0)
    with open(out_path, 'wb') as f:
        f.write(out)
    return bytes(out)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def patch_library(lib):
    if hashlib.sha256(lib).hexdigest() != ORIGINAL_SHA256:
        raise SystemExit(
            'ERROR: this APK does not contain the expected F1 Mobile Racing 5.4.11 '
            'libil2cpp.so\n       expected sha256: %s\n       Make sure the input is the '
            'original 5.4.11 APK (versionCode 24001341).' % ORIGINAL_SHA256)
    buf = bytearray(lib)
    for offset, repl in PATCHES:
        if offset + len(repl) > len(buf):
            raise SystemExit('ERROR: patch offset 0x%X outside the library' % offset)
        buf[offset:offset + len(repl)] = repl
    out = bytes(buf)
    actual = hashlib.sha256(out).hexdigest()
    if actual != PATCHED_SHA256:
        raise SystemExit('ERROR: patch table produced %s, expected %s' % (actual, PATCHED_SHA256))
    return out


def main(argv):
    import zipfile
    if len(argv) < 2 or argv[1] in ('-h', '--help'):
        print(__doc__)
        return 2
    src = argv[1]
    out_path = argv[argv.index('-o') + 1] if '-o' in argv else None
    if not os.path.isfile(src):
        raise SystemExit('ERROR: %s not found' % src)
    if out_path is None:
        out_path = os.path.splitext(src)[0] + '-offline-patched.apk'

    print('input :', src)
    print('output:', out_path)

    with zipfile.ZipFile(src) as zin:
        if LIB_ENTRY not in zin.namelist():
            raise SystemExit('ERROR: %s not found in the APK' % LIB_ENTRY)
        print('reading entries...')
        entries = []
        for info in zin.infolist():
            if info.filename in DROP_ENTRIES:
                continue
            data = zin.read(info.filename)
            if info.filename == LIB_ENTRY:
                data = patch_library(data)
                print('libil2cpp.so patched ->', hashlib.sha256(data).hexdigest()[:16], '...')
            entries.append((info.filename, info.compress_type, data, info.date_time,
                            info.external_attr))

    print('rebuilding APK...')
    apk = write_zip(entries, out_path)

    print('signing (APK Signature Scheme v2)...')
    n, e, d = load_key(base64.b64decode(KEY_PEM_B64).decode('utf-8'))
    cert_der = base64.b64decode(CERT_DER_B64)
    signed = sign_v2(apk, n, e, d, cert_der)
    with open(out_path, 'wb') as f:
        f.write(signed)

    print('done: %s (%.1f MB)' % (out_path, os.path.getsize(out_path) / 1048576.0))
    print()
    print('The store version must be removed first (different signing key):')
    print('  adb uninstall com.codemasters.F1Mobile')
    print('  adb install -r "%s"' % out_path)
    print('Keep the OBB under /sdcard/Android/obb/com.codemasters.F1Mobile/ (README.md).')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
