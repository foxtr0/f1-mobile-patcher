import sys, os, struct, zlib, hashlib, base64

ORIGINAL_SHA256 = "90ae142fa1ed5e81946c8b5624552007f3d6770f404a51773eba4192639c9b82"
PATCHED_SHA256 = "c69ec18ead746986263d4caa92789e6f5784b715437d133334df72e4764da948"
LIB_ENTRY = "lib/arm64-v8a/libil2cpp.so"
DROP_ENTRIES = ("META-INF/CERT.RSA", "META-INF/CERT.SF", "META-INF/MANIFEST.MF")

# (file offset in libil2cpp.so, replacement bytes)
PATCHES = [
    (0xA0, bytes.fromhex("3866")),
    (0x1A40E7C, bytes.fromhex("512b5014")),
    (0x1A41468, bytes.fromhex("d6295014")),
    (0x1C151C8, bytes.fromhex("20008052")),
    (0x1E69258, bytes.fromhex("20008052c0035fd6")),
    (0x1E6A30C, bytes.fromhex("93078052")),
    (0x1E6B7A8, bytes.fromhex("b6253f14")),
    (0x1E6BDE4, bytes.fromhex("800c8052c0035fd6")),
    (0x1EADF74, bytes.fromhex("16008152")),
    (0x27AFBEC, bytes.fromhex("c0035fd6")),
    (0x27E5E38, bytes.fromhex("0800")),
    (0x27E5E3B, bytes.fromhex("14")),
    (0x27ED714, bytes.fromhex("0701")),
    (0x27ED717, bytes.fromhex("14")),
    (0x27EDB10, bytes.fromhex("1f2003d5")),
    (0x27EDBDC, bytes.fromhex("28008052")),
    (0x27EDCA8, bytes.fromhex("28008052")),
    (0x27EDCF4, bytes.fromhex("28008052")),
    (0x27F5A84, bytes.fromhex("28008052")),
    (0x285AAB0, bytes.fromhex("28008052")),
    (0x285AC34, bytes.fromhex("28008052")),
    (0x285AFD0, bytes.fromhex("28008052")),
    (0x287E49C, bytes.fromhex("28008052")),
    (0x2913BEA, bytes.fromhex("1f2a")),
    (0x29187A8, bytes.fromhex("9301")),
    (0x29187B0, bytes.fromhex("48")),
    (0x29187B8, bytes.fromhex("08")),
    (0x29187D0, bytes.fromhex("41")),
    (0x2918838, bytes.fromhex("1404")),
    (0x2918840, bytes.fromhex("c803")),
    (0x2918850, bytes.fromhex("5403")),
    (0x292AAF8, bytes.fromhex("2300")),
    (0x292AAFB, bytes.fromhex("14")),
    (0x292E48D, bytes.fromhex("031f2a")),
    (0x292F1B4, bytes.fromhex("cb161414")),
    (0x2950E02, bytes.fromhex("1f")),
    (0x29523F1, bytes.fromhex("881314")),
    (0x29612C8, bytes.fromhex("28008052")),
    (0x296138C, bytes.fromhex("0100")),
    (0x296138F, bytes.fromhex("14")),
    (0x2961B54, bytes.fromhex("6006")),
    (0x2961B94, bytes.fromhex("6004")),
    (0x2961BAC, bytes.fromhex("a003")),
    (0x2961BEC, bytes.fromhex("a001")),
    (0x2961BFC, bytes.fromhex("20")),
    (0x2961C20, bytes.fromhex("20008052")),
    (0x2962014, bytes.fromhex("601c")),
    (0x2962054, bytes.fromhex("601a")),
    (0x2962170, bytes.fromhex("9611")),
    (0x2962188, bytes.fromhex("d510")),
    (0x29621EC, bytes.fromhex("b50d")),
    (0x296225C, bytes.fromhex("35")),
    (0x29622CC, bytes.fromhex("b506")),
    (0x29622EC, bytes.fromhex("a005")),
    (0x2962360, bytes.fromhex("15")),
    (0x2962380, bytes.fromhex("00")),
    (0x29623A0, bytes.fromhex("20008052")),
    (0x296BE60, bytes.fromhex("c0035fd6")),
    (0x2988900, bytes.fromhex("20008052c0")),
    (0x2988906, bytes.fromhex("5fd6")),
    (0x298B50C, bytes.fromhex("5da51214")),
    (0x299A500, bytes.fromhex("d43e1314")),
    (0x299FBD0, bytes.fromhex("0c561214")),
    (0x299FD48, bytes.fromhex("170500d101000014")),
    (0x29A20B8, bytes.fromhex("a000")),
    (0x29A3AE0, bytes.fromhex("08000014")),
    (0x29A4448, bytes.fromhex("2300")),
    (0x29A444B, bytes.fromhex("14")),
    (0x29A44D4, bytes.fromhex("0b431214")),
    (0x29A4508, bytes.fromhex("1f2003d5")),
    (0x29A452C, bytes.fromhex("21008052")),
    (0x29A4CC4, bytes.fromhex("0f421214")),
    (0x29A4E00, bytes.fromhex("21008052")),
    (0x29A5A88, bytes.fromhex("fe3d1214")),
    (0x29AB8DC, bytes.fromhex("20008052c0035fd6")),
    (0x29ACAB0, bytes.fromhex("600c8052c0035fd6")),
    (0x29B0EE4, bytes.fromhex("2500")),
    (0x29B0EE7, bytes.fromhex("14")),
    (0x29B0F78, bytes.fromhex("e20f1214")),
    (0x29B0FD4, bytes.fromhex("21008052")),
    (0x29B10DC, bytes.fromhex("bf0f1294")),
    (0x29B11B0, bytes.fromhex("e203132a")),
    (0x29B11B8, bytes.fromhex("21008052")),
    (0x29B1370, bytes.fromhex("1f2003d5")),
    (0x29B138C, bytes.fromhex("21008052")),
    (0x29B1498, bytes.fromhex("2100")),
    (0x29B149B, bytes.fromhex("14")),
    (0x29B151C, bytes.fromhex("190f1214")),
    (0x29B1574, bytes.fromhex("21008052")),
    (0x29B17F0, bytes.fromhex("1100")),
    (0x29B17F3, bytes.fromhex("14")),
    (0x29B187C, bytes.fromhex("21008052")),
    (0x29E9A74, bytes.fromhex("1f2003d5")),
    (0x29E9C9C, bytes.fromhex("c0035fd6")),
    (0x29EA1DC, bytes.fromhex("782a1114")),
    (0x29ECCCC, bytes.fromhex("c0035fd6")),
    (0x29EE060, bytes.fromhex("c0035fd6")),
    (0x29EE7EC, bytes.fromhex("c0")),
    (0x29EE7EE, bytes.fromhex("5fd6")),
    (0x29F32A4, bytes.fromhex("40008052")),
    (0x2A72048, bytes.fromhex("9403")),
    (0x2B89A34, bytes.fromhex("43810b14")),
    (0x2B8CA88, bytes.fromhex("82710b14")),
    (0x2B8CB10, bytes.fromhex("3c750b14")),
    (0x2BCF148, bytes.fromhex("28008052")),
    (0x2C05060, bytes.fromhex("c0035fd6")),
    (0x2C3B0A0, bytes.fromhex("28008052")),
    (0x2C43650, bytes.fromhex("ec970814")),
    (0x2C471D4, bytes.fromhex("c0035fd6")),
    (0x2C5C004, bytes.fromhex("8bbe0714")),
    (0x2C5C08C, bytes.fromhex("e003082a")),
    (0x2C5C1D4, bytes.fromhex("57bf0714")),
    (0x2C5C29C, bytes.fromhex("96620714")),
    (0x2C5DAAC, bytes.fromhex("3000805214b80714")),
    (0x2C5E31C, bytes.fromhex("50008052f8b50714")),
    (0x2C5E584, bytes.fromhex("0800")),
    (0x2C5E587, bytes.fromhex("14")),
    (0x2C63D40, bytes.fromhex("1f2003d59f440714")),
    (0x2C6414C, bytes.fromhex("1f2003d5")),
    (0x2C664B0, bytes.fromhex("14990714")),
    (0x2C952C8, bytes.fromhex("0e500714")),
    (0x2C954D4, bytes.fromhex("ab4f0714")),
    (0x2CA1B8C, bytes.fromhex("0c00")),
    (0x2CA1B8F, bytes.fromhex("14")),
    (0x2CA37DC, bytes.fromhex("c0035fd6")),
    (0x2CA3864, bytes.fromhex("01008052")),
    (0x2CBB980, bytes.fromhex("00008052c0035fd6")),
    (0x2CD1F90, bytes.fromhex("c0035fd6")),
    (0x2CD83E0, bytes.fromhex("00008052c0035fd6")),
    (0x2CD8BA4, bytes.fromhex("27700514")),
    (0x2D9CCD8, bytes.fromhex("1f2003d5")),
    (0x2DE33C0, bytes.fromhex("ffc301d1fd7b02a9f35303a9f55b04a9f76305a9f96b06a9fb0b")),
    (0x2DE33DB, bytes.fromhex("f9fd03")),
    (0x2DE33DF, bytes.fromhex("9108a1")),
    (0x2DE33E3, bytes.fromhex("90")),
    (0x2DE33E5, bytes.fromhex("2d46f90c6f7c9788c9")),
    (0x2DE33EF, bytes.fromhex("d008013091c91e")),
    (0x2DE33F7, bytes.fromhex("12e91e1833091f10330901")),
    (0x2DE3403, bytes.fromhex("b91505")),
    (0x2DE3407, bytes.fromhex("b9a962fb97800e")),
    (0x2DE340F, bytes.fromhex("b4f903")),
    (0x2DE3413, bytes.fromhex("aa3a0f40f93a0e")),
    (0x2DE341B, bytes.fromhex("b4481b40b9e803")),
    (0x2DE3423, bytes.fromhex("351b")),
    (0x2DE3426, bytes.fromhex("80527f2b")),
    (0x2DE342B, bytes.fromhex("712202")),
    (0x2DE342F, bytes.fromhex("5408")),
    (0x2DE3433, bytes.fromhex("b008010191")),
    (0x2DE3439, bytes.fromhex("597bb821")),
    (0x2DE343E, bytes.fromhex("80529e1bef972001")),
    (0x2DE3447, bytes.fromhex("b41f")),
    (0x2DE344A, bytes.fromhex("01391f040139e103")),
    (0x2DE3453, bytes.fromhex("aae0031aaa08a1")),
    (0x2DE345B, bytes.fromhex("90082d46f9020140f9a122db977b07")),
    (0x2DE346B, bytes.fromhex("11efffff17481b40b9480b")),
    (0x2DE3477, bytes.fromhex("34284f40b91f05")),
    (0x2DE347F, bytes.fromhex("71ea")),
    (0x2DE3483, bytes.fromhex("54490b40f9291140f989")),
    (0x2DE348F, bytes.fromhex("b4211540b9e00319aaad630594752a40f9f509")),
    (0x2DE34A3, bytes.fromhex("b4b63240f9b609")),
    (0x2DE34AB, bytes.fromhex("b4e00315aae10316aa22")),
    (0x2DE34B6, bytes.fromhex("805223")),
    (0x2DE34BA, bytes.fromhex("805224")),
    (0x2DE34BE, bytes.fromhex("8052a3a3")),
    (0x2DE34C3, bytes.fromhex("94e00316aa1483f997d73a40f97708")),
    (0x2DE34D3, bytes.fromhex("b488c9")),
    (0x2DE34D7, bytes.fromhex("d008013091080540b9e807")),
    (0x2DE34E3, bytes.fromhex("34e86a")),
    (0x2DE34E7, bytes.fromhex("b9c89f")),
    (0x2DE34EB, bytes.fromhex("b0080147f9")),
    (0x2DE34F1, bytes.fromhex("0140f943930c942007")),
    (0x2DE34FB, bytes.fromhex("b4289f")),
    (0x2DE34FF, bytes.fromhex("b0087146f9010140f99165")),
    (0x2DE350B, bytes.fromhex("948006")),
    (0x2DE350F, bytes.fromhex("b4e16a40b9e2031faa68e00394")),
    (0x2DE351D, bytes.fromhex("06")),
    (0x2DE351F, bytes.fromhex("b4f803")),
    (0x2DE3523, bytes.fromhex("aaf53240f9b505")),
    (0x2DE352B, bytes.fromhex("b489c9")),
    (0x2DE352F, bytes.fromhex("d0290130913509")),
    (0x2DE3537, bytes.fromhex("f9a80240f9e00315aae1031faae20318aa098d5ea920013fd6e01a40f960")),
    (0x2DE3557, bytes.fromhex("b4e1031f2a3c979e97e02640f960")),
    (0x2DE3567, bytes.fromhex("b4e1031f2a38979e97e00e40f9a0")),
    (0x2DE3577, bytes.fromhex("b41d799e9760")),
    (0x2DE357F, bytes.fromhex("b4e1031f2a32979e97e01240f9a0")),
    (0x2DE358F, bytes.fromhex("b417799e9760")),
    (0x2DE3597, bytes.fromhex("b4e1031f2a2c979e97a04e40f9a0")),
    (0x2DE35A7, bytes.fromhex("b411799e9760")),
    (0x2DE35AF, bytes.fromhex("b4e1031f2a26979e97a05240f9a0")),
    (0x2DE35BF, bytes.fromhex("b40b799e9760")),
    (0x2DE35C7, bytes.fromhex("b4e1031f2a20979e97bfaa")),
    (0x2DE35D3, bytes.fromhex("b9bfae")),
    (0x2DE35D7, bytes.fromhex("b90c")),
    (0x2DE35DB, bytes.fromhex("1488c9")),
    (0x2DE35DF, bytes.fromhex("d008013091010540b90101")),
    (0x2DE35EB, bytes.fromhex("340a0140b9e00314aa22068052431d")),
    (0x2DE35FB, bytes.fromhex("12443d0853455d10539598f997fb0b40f9f96b46a9f76345a9f55b44a9f35343a9fd7b42a9ffc30191c0035fd6")),
    (0x2DE3780, bytes.fromhex("ff83")),
    (0x2DE3783, bytes.fromhex("d1e007")),
    (0x2DE3787, bytes.fromhex("a9fd7b01a985c9")),
    (0x2DE378F, bytes.fromhex("d0a5")),
    (0x2DE3792, bytes.fromhex("3091a50840f965")),
    (0x2DE379B, bytes.fromhex("b4bf")),
    (0x2DE379F, bytes.fromhex("eb80")),
    (0x2DE37A3, bytes.fromhex("54fd7b41a9ff83")),
    (0x2DE37AB, bytes.fromhex("91c0035fd6e00340f9fd7b41a9ff83")),
    (0x2DE37BB, bytes.fromhex("914102")),
    (0x2DE37BF, bytes.fromhex("14")),
    (0x2DE4040, bytes.fromhex("1e2503")),
    (0x2DE4044, bytes.fromhex("1f2503")),
    (0x2DE4048, bytes.fromhex("202503")),
    (0x2DE404C, bytes.fromhex("212503")),
    (0x2DE4050, bytes.fromhex("222503")),
    (0x2DE4054, bytes.fromhex("232503")),
    (0x2DE4058, bytes.fromhex("242503")),
    (0x2DE405C, bytes.fromhex("252503")),
    (0x2DE4060, bytes.fromhex("262503")),
    (0x2DE4064, bytes.fromhex("272503")),
    (0x2DE40C0, bytes.fromhex("fd7bbda9f35301a9f513")),
    (0x2DE40CB, bytes.fromhex("f9f303")),
    (0x2DE40CF, bytes.fromhex("aa692a40f90901")),
    (0x2DE40D7, bytes.fromhex("b429c140f9c9")),
    (0x2DE40DF, bytes.fromhex("b4601e40f980")),
    (0x2DE40E7, bytes.fromhex("b4211540b9e2031faa9760059488a0")),
    (0x2DE40F7, bytes.fromhex("d014d942f9e00314aac66b7c97800240f93e900c942006")),
    (0x2DE410F, bytes.fromhex("b4f303")),
    (0x2DE4113, bytes.fromhex("aa88c9")),
    (0x2DE4117, bytes.fromhex("b008013091140540b91402")),
    (0x2DE4123, bytes.fromhex("35e00313aaa793f997e00313aaae93f997e00313aadd94f997a004")),
    (0x2DE413F, bytes.fromhex("b4091840b96904")),
    (0x2DE4147, bytes.fromhex("34090840f92904")),
    (0x2DE414F, bytes.fromhex("b4291140f9e903")),
    (0x2DE4157, bytes.fromhex("b4341140b9b403")),
    (0x2DE415F, bytes.fromhex("3488c9")),
    (0x2DE4163, bytes.fromhex("b0080130911f09")),
    (0x2DE416B, bytes.fromhex("f90a0140b9431d")),
    (0x2DE4173, bytes.fromhex("127f04")),
    (0x2DE4177, bytes.fromhex("7162")),
    (0x2DE417B, bytes.fromhex("54c3")),
    (0x2DE417E, bytes.fromhex("805204")),
    (0x2DE4183, bytes.fromhex("147f14")),
    (0x2DE4187, bytes.fromhex("7149")),
    (0x2DE418B, bytes.fromhex("54c3")),
    (0x2DE418E, bytes.fromhex("8052443d08539f04")),
    (0x2DE4197, bytes.fromhex("7162")),
    (0x2DE419B, bytes.fromhex("5464")),
    (0x2DE419E, bytes.fromhex("805204")),
    (0x2DE41A3, bytes.fromhex("149f50")),
    (0x2DE41A7, bytes.fromhex("7149")),
    (0x2DE41AB, bytes.fromhex("5464")),
    (0x2DE41AE, bytes.fromhex("8052455d1053bf08")),
    (0x2DE41B7, bytes.fromhex("7149")),
    (0x2DE41BB, bytes.fromhex("5425")),
    (0x2DE41BE, bytes.fromhex("8052e00313aae103142a22068052a395f997f51340f9f35341a9fd7bc3a8c0035fd6")),
    (0x2E347BC, bytes.fromhex("ff8301d1fd7b02a9f35303a9f55b04a9f76305a9fd03")),
    (0x2E347D3, bytes.fromhex("91f303")),
    (0x2E347D7, bytes.fromhex("aa75e240b976e640b977ea40b978ee40b9ff06")),
    (0x2E347EB, bytes.fromhex("714a")),
    (0x2E347EF, bytes.fromhex("5477")),
    (0x2E347F2, bytes.fromhex("80521f03")),
    (0x2E347F7, bytes.fromhex("714a")),
    (0x2E347FB, bytes.fromhex("5438")),
    (0x2E347FE, bytes.fromhex("8052df02")),
    (0x2E34803, bytes.fromhex("714a")),
    (0x2E34807, bytes.fromhex("54d6")),
    (0x2E3480A, bytes.fromhex("8052149e")),
    (0x2E3480F, bytes.fromhex("d094da42f9e00314aa")),
    (0x2E34819, bytes.fromhex("2a7b97800240f9784e0b942003")),
    (0x2E34827, bytes.fromhex("b4f403")),
    (0x2E3482B, bytes.fromhex("aa1502")),
    (0x2E3482F, bytes.fromhex("35e00314aae451f897e00314aaeb51f897e00314aa1a53f897")),
    (0x2E34849, bytes.fromhex("02")),
    (0x2E3484B, bytes.fromhex("b4091840b9c901")),
    (0x2E34853, bytes.fromhex("34090840f98901")),
    (0x2E3485B, bytes.fromhex("b4291140f94901")),
    (0x2E34863, bytes.fromhex("b4351140b91501")),
    (0x2E3486B, bytes.fromhex("34e00314aae103152a22068052e303162ae403172ae503182acfbafe97f76345a9f55b44a9f35343a9fd7b42a9ff830191c0035fd666316f5f73746570")),
    (0x2E348AC, bytes.fromhex("66316f5f7465616d")),
    (0x2E348B8, bytes.fromhex("66316f5f6770")),
    (0x2E348C4, bytes.fromhex("66316f5f647276")),
    (0x2E348D0, bytes.fromhex("66316f5f6368616d70")),
    (0x2E348E0, bytes.fromhex("fd7bbda9fd03")),
    (0x2E348E7, bytes.fromhex("91f35301a9f303")),
    (0x2E348EF, bytes.fromhex("aa685240b91f01")),
    (0x2E348F7, bytes.fromhex("71cd03")),
    (0x2E348FB, bytes.fromhex("5414")),
    (0x2E348FF, bytes.fromhex("90948222918002")),
    (0x2E34907, bytes.fromhex("918bca7897614a40b9e2031faa463cb7978032")),
    (0x2E3491B, bytes.fromhex("9186ca7897615240b9e2031faa413cb7978062")),
    (0x2E3492F, bytes.fromhex("9181ca7897614e40b9e2031faa3c3cb7978092")),
    (0x2E34943, bytes.fromhex("917cca7897615640b9e2031faa373cb79780c2")),
    (0x2E34957, bytes.fromhex("9177ca789761024239e2031faa323cb797e2031faa6b3db797f35341a9fd7bc3a8c0035fd6")),
    (0x2E34990, bytes.fromhex("fd7bbca9fd03")),
    (0x2E34997, bytes.fromhex("91f35301a9f55b02a9f303")),
    (0x2E349A3, bytes.fromhex("aa684a40b91f05")),
    (0x2E349AB, bytes.fromhex("3180")),
    (0x2E349AF, bytes.fromhex("54685240b91f05")),
    (0x2E349B7, bytes.fromhex("31a104")),
    (0x2E349BB, bytes.fromhex("5414")),
    (0x2E349BF, bytes.fromhex("90948222918032")),
    (0x2E349C7, bytes.fromhex("915bca7897e1031f2ae2031faa5a3cb797a003")),
    (0x2E349DB, bytes.fromhex("346052")),
    (0x2E349DF, bytes.fromhex("b98002")),
    (0x2E349E3, bytes.fromhex("9154ca7897e1031f2ae2031faa533cb797604a")),
    (0x2E349F7, bytes.fromhex("b98062")),
    (0x2E349FB, bytes.fromhex("914eca7897e1031f2ae2031faa4d3cb797604e")),
    (0x2E34A0F, bytes.fromhex("b98092")),
    (0x2E34A13, bytes.fromhex("9148ca7897e1031f2ae2031faa473cb7976056")),
    (0x2E34A27, bytes.fromhex("b980c2")),
    (0x2E34A2B, bytes.fromhex("9142ca7897e1031f2ae2031faa413cb7976002023928")),
    (0x2E34A42, bytes.fromhex("805268060239684a0239f55b42a9f35341a9fd7bc4a8c0035fd6")),
    (0x2E34A80, bytes.fromhex("fd7bbea9fd03")),
    (0x2E34A87, bytes.fromhex("91f35301a9f303")),
    (0x2E34A8F, bytes.fromhex("aa684a423968")),
    (0x2E34A97, bytes.fromhex("34e00313aa91ffff97f35341a9fd7bc2a8f50f1df8995aed17")),
    (0x2E34BBC, bytes.fromhex("fd7bbea9fd03")),
    (0x2E34BC3, bytes.fromhex("91f35301a9f39a")),
    (0x2E34BCB, bytes.fromhex("9073f246f9680240f9085d40f9080140f90801")),
    (0x2E34BDF, bytes.fromhex("b4")),
    (0x2E34BE1, bytes.fromhex("2940f9c0")),
    (0x2E34BE7, bytes.fromhex("b481")),
    (0x2E34BEA, bytes.fromhex("805222")),
    (0x2E34BEE, bytes.fromhex("805223")),
    (0x2E34BF2, bytes.fromhex("8052e4031faa8a61ff97f35341a9fd7bc2a8c0035fd6")),
    (0x2E34C40, bytes.fromhex("fd7bbca9fd03")),
    (0x2E34C47, bytes.fromhex("91f35301a9f55b02a9f303")),
    (0x2E34C53, bytes.fromhex("aa149e")),
    (0x2E34C57, bytes.fromhex("f0943e44f9800240f9684d0b944001")),
    (0x2E34C67, bytes.fromhex("b4f403")),
    (0x2E34C6B, bytes.fromhex("aae00314aae8baf9979fc2")),
    (0x2E34C77, bytes.fromhex("b99ff6")),
    (0x2E34C7B, bytes.fromhex("b968")),
    (0x2E34C7E, bytes.fromhex("805288b2")),
    (0x2E34C83, bytes.fromhex("b928")),
    (0x2E34C86, bytes.fromhex("805288a60239689d")),
    (0x2E34C8F, bytes.fromhex("d0082547f9")),
    (0x2E34C95, bytes.fromhex("0140f92ae4bc97a0")),
    (0x2E34C9F, bytes.fromhex("b408f0a752")),
    (0x2E34CA5, bytes.fromhex("01271ee1031faa6726a69708f0a752")),
    (0x2E34CB5, bytes.fromhex("01271ee0031faa9ea29a97e00313aa0a8ffa97f55b42a9f35341a9fd7bc4a8c0035fd6")),
    (0x2E34CE0, bytes.fromhex("691a41b908c7")),
    (0x2E34CE7, bytes.fromhex("b009e507b9e003152a32e9eb17fd7bbfa9fd03")),
    (0x2E34CFB, bytes.fromhex("91")),
    (0x2E34CFD, bytes.fromhex("3040f9c0")),
    (0x2E34D03, bytes.fromhex("b4")),
    (0x2E34D05, bytes.fromhex("1040f980")),
    (0x2E34D0B, bytes.fromhex("b4e1031f2ae2031faa4e519d97fd7bc1a8c0035fd6")),
    (0x2E34E80, bytes.fromhex("e00302aae10303aac0035fd6")),
    (0x2E34F00, bytes.fromhex("fd7bbea9fd03")),
    (0x2E34F07, bytes.fromhex("91f30b")),
    (0x2E34F0B, bytes.fromhex("f9c89e")),
    (0x2E34F0F, bytes.fromhex("d0088d46f9")),
    (0x2E34F15, bytes.fromhex("0140f908cc443988")),
    (0x2E34F1E, bytes.fromhex("103608e040b948")),
    (0x2E34F27, bytes.fromhex("3569287b97889c")),
    (0x2E34F2F, bytes.fromhex("b0082940f9")),
    (0x2E34F35, bytes.fromhex("0140f9b24c0b94e002")),
    (0x2E34F3F, bytes.fromhex("b4bd8af897a002")),
    (0x2E34F47, bytes.fromhex("b4f303")),
    (0x2E34F4B, bytes.fromhex("aa08c7")),
    (0x2E34F4F, bytes.fromhex("b008e547b91f01017162")),
    (0x2E34F5B, bytes.fromhex("54684a")),
    (0x2E34F5F, bytes.fromhex("b905")),
    (0x2E34F63, bytes.fromhex("14684a40b91f01017143")),
    (0x2E34F6F, bytes.fromhex("547f4a")),
    (0x2E34F73, bytes.fromhex("b97f4e")),
    (0x2E34F77, bytes.fromhex("b97652")),
    (0x2E34F7B, bytes.fromhex("b97556")),
    (0x2E34F7F, bytes.fromhex("b928")),
    (0x2E34F82, bytes.fromhex("80527f02023968060239684a0239e00313aa53feff97689d")),
    (0x2E34F9B, bytes.fromhex("f0083d45f9e00319aa010140f9b8cc0b94f30b40f9fd7bc2a8feefed17")),
    (0x2E34FC0, bytes.fromhex("e00313aa21")),
    (0x2E34FC6, bytes.fromhex("8052fd7b42a9f44f41a9f50743f823bcf817fd7bbca9fd03")),
    (0x2E34FDF, bytes.fromhex("91f35301a9f55b02a9a09d")),
    (0x2E34FEB, bytes.fromhex("f0")),
    (0x2E34FED, bytes.fromhex("e444f90a287b97b39d")),
    (0x2E34FF7, bytes.fromhex("f073e644f9730240f9889c")),
    (0x2E35003, bytes.fromhex("90082940f9")),
    (0x2E35009, bytes.fromhex("0140f97d4c0b94c005")),
    (0x2E35013, bytes.fromhex("b4e1031faa878af8976005")),
    (0x2E3501F, bytes.fromhex("b4f403")),
    (0x2E35023, bytes.fromhex("aa885240b91f01")),
    (0x2E3502B, bytes.fromhex("71ed04")),
    (0x2E3502F, bytes.fromhex("5408")),
    (0x2E35032, bytes.fromhex("8012884e")),
    (0x2E35037, bytes.fromhex("b9885e")),
    (0x2E3503B, bytes.fromhex("b968")),
    (0x2E3503E, bytes.fromhex("8052885a")),
    (0x2E35043, bytes.fromhex("b928")),
    (0x2E35046, bytes.fromhex("80528806023988460239884a0239893a40f92903")),
    (0x2E3505B, bytes.fromhex("b4281940b9e802")),
    (0x2E35063, bytes.fromhex("35953640f975")),
    (0x2E3506B, bytes.fromhex("b4a81a40b9a8")),
    (0x2E35073, bytes.fromhex("3580028052acd0ed97")),
    (0x2E3507D, bytes.fromhex("02")),
    (0x2E3507F, bytes.fromhex("b4f503")),
    (0x2E35083, bytes.fromhex("aaf6031f2adf52")),
    (0x2E3508B, bytes.fromhex("718a01")),
    (0x2E3508F, bytes.fromhex("54a91a40b9df02096b2a01")),
    (0x2E3509B, bytes.fromhex("54a90a40f92981")),
    (0x2E350A3, bytes.fromhex("91215976b8803a40f9e20313aaf9beda97d606")),
    (0x2E350B7, bytes.fromhex("11f4ffff17e00314aa21")),
    (0x2E350C2, bytes.fromhex("80521259ed97e0031f2af55b42a9f35341a9fd7bc4a8c0035fd6")),
    (0x2E35100, bytes.fromhex("fd7bbfa9889c")),
    (0x2E35107, bytes.fromhex("90082940f9")),
    (0x2E3510D, bytes.fromhex("0140f93c4c0b94a0")),
    (0x2E35117, bytes.fromhex("b4e1031faa468af89740")),
    (0x2E35123, bytes.fromhex("b4135c")),
    (0x2E35127, bytes.fromhex("b9fd7bc1a8a89a")),
    (0x2E3512F, bytes.fromhex("d0eabced17")),
    (0x2E35180, bytes.fromhex("fd7bbfa9889c")),
    (0x2E35187, bytes.fromhex("90082940f9")),
    (0x2E3518D, bytes.fromhex("0140f91c4c0b94a0")),
    (0x2E35197, bytes.fromhex("b4e1031faa268af89740")),
    (0x2E351A3, bytes.fromhex("b41f58")),
    (0x2E351A7, bytes.fromhex("b9fd7bc1a8a89a")),
    (0x2E351AF, bytes.fromhex("d0dcf0ed17")),
    (0x2E35280, bytes.fromhex("fd7bbda9f35301a9f513")),
    (0x2E3528B, bytes.fromhex("f9e017")),
    (0x2E3528F, bytes.fromhex("f9889c")),
    (0x2E35293, bytes.fromhex("90082940f9")),
    (0x2E35299, bytes.fromhex("0140f9d94b0b94e001")),
    (0x2E352A3, bytes.fromhex("b4e1031faae389f8978001")),
    (0x2E352AF, bytes.fromhex("b4f303")),
    (0x2E352B3, bytes.fromhex("aa683640f968")),
    (0x2E352BB, bytes.fromhex("b4081940b9e8")),
    (0x2E352C3, bytes.fromhex("358002805218d0ed9780")),
    (0x2E352CF, bytes.fromhex("b4e103")),
    (0x2E352D3, bytes.fromhex("aae00313aa924bed97e01740f9f51340f9f35341a9fd7bc3a8fb0f1af8e7c1ed17")),
    (0x2E35400, bytes.fromhex("ffc3")),
    (0x2E35403, bytes.fromhex("d1fd7b01a9f35302a9f40313aa880240f90801")),
    (0x2E35417, bytes.fromhex("b4085d40f9c8")),
    (0x2E3541F, bytes.fromhex("b4092540f989")),
    (0x2E35427, bytes.fromhex("b4291940b93f09")),
    (0x2E3542F, bytes.fromhex("71e201")),
    (0x2E35433, bytes.fromhex("54889c")),
    (0x2E35437, bytes.fromhex("90082940f9")),
    (0x2E3543D, bytes.fromhex("0140f9704b0b944001")),
    (0x2E35447, bytes.fromhex("b4f0c3f897")),
    (0x2E3544D, bytes.fromhex("01")),
    (0x2E3544F, bytes.fromhex("b4c23aed97c0")),
    (0x2E35457, bytes.fromhex("b4880240f988")),
    (0x2E3545F, bytes.fromhex("b4085d40f948")),
    (0x2E35467, bytes.fromhex("b4")),
    (0x2E35469, bytes.fromhex("25")),
    (0x2E3546B, bytes.fromhex("f9f35342a9fd7b41a9ffc3")),
    (0x2E35477, bytes.fromhex("91600240f9699b")),
    (0x2E3547F, bytes.fromhex("b0d5a9ed17")),
    (0x2E35500, bytes.fromhex("ff0302d1e803")),
    (0x2E35507, bytes.fromhex("fdf35301a9f55b02a9f76303a9f96b04a9fb7305a9fd7b06a9889c")),
    (0x2E35523, bytes.fromhex("90082940f9")),
    (0x2E35529, bytes.fromhex("0140f9354b0b94400e")),
    (0x2E35533, bytes.fromhex("b4e1031faa3f89f897e00d")),
    (0x2E3553F, bytes.fromhex("b4f303")),
    (0x2E35543, bytes.fromhex("aa683640f9880d")),
    (0x2E3554B, bytes.fromhex("b4a09e")),
    (0x2E3554F, bytes.fromhex("f0")),
    (0x2E35551, bytes.fromhex("4043f9b1267b97409f")),
    (0x2E3555B, bytes.fromhex("90")),
    (0x2E3555D, bytes.fromhex("6846f9ae267b97a09d")),
    (0x2E35567, bytes.fromhex("d0")),
    (0x2E35569, bytes.fromhex("e444f9ab267b97a89e")),
    (0x2E35573, bytes.fromhex("f0084143f9")),
    (0x2E35579, bytes.fromhex("0140f9db267b97c006")),
    (0x2E35583, bytes.fromhex("b4f403")),
    (0x2E35587, bytes.fromhex("aa489f")),
    (0x2E3558B, bytes.fromhex("90086946f9010140f968bada97f5031f2a683640f96805")),
    (0x2E355A3, bytes.fromhex("b4091940b9bf02096b0a05")),
    (0x2E355AF, bytes.fromhex("540a0940f9ca04")),
    (0x2E355B7, bytes.fromhex("b44a81")),
    (0x2E355BB, bytes.fromhex("91565975b8a8")),
    (0x2E355C3, bytes.fromhex("f008810291")),
    (0x2E355C9, bytes.fromhex("49358b5ac77897e1031faa5a39b797f703")),
    (0x2E355DB, bytes.fromhex("2adf02")),
    (0x2E355DF, bytes.fromhex("71c1")),
    (0x2E355E3, bytes.fromhex("54605e40b91f04")),
    (0x2E355EB, bytes.fromhex("716b")),
    (0x2E355EF, bytes.fromhex("54")),
    (0x2E355F1, bytes.fromhex("04")),
    (0x2E355F3, bytes.fromhex("5102")),
    (0x2E355F7, bytes.fromhex("14e003152ae1031faa71d1ed97f702")),
    (0x2E35607, bytes.fromhex("0ba8")),
    (0x2E3560B, bytes.fromhex("f008810291")),
    (0x2E35611, bytes.fromhex("49358b48c77897e103172ae2031faa0339b797e203172ae10316aa218002aaa89d")),
    (0x2E35633, bytes.fromhex("d008e544f9020140f9e00314aa95bdda97b506")),
    (0x2E35647, bytes.fromhex("11d5ffff1760c20191e10314aa58267b97684e40b91f05")),
    (0x2E3565F, bytes.fromhex("31a003")),
    (0x2E35663, bytes.fromhex("54899c")),
    (0x2E35667, bytes.fromhex("90292940f9200140f9e44a0b944002")),
    (0x2E35677, bytes.fromhex("b4e1031faad6c0f897e001")),
    (0x2E35683, bytes.fromhex("b4e1031faa692bed978001")),
    (0x2E3568F, bytes.fromhex("b4614a40b9e2031faa1c37ed97")),
    (0x2E3569D, bytes.fromhex("01")),
    (0x2E3569F, bytes.fromhex("b4")),
    (0x2E356A1, bytes.fromhex("2840f9c0")),
    (0x2E356A7, bytes.fromhex("b4081840b9694e40b92905")),
    (0x2E356B3, bytes.fromhex("113f01086baa")),
    (0x2E356BB, bytes.fromhex("54684e40b90805")),
    (0x2E356C3, bytes.fromhex("11684e")),
    (0x2E356C7, bytes.fromhex("b903")),
    (0x2E356CB, bytes.fromhex("1408")),
    (0x2E356CE, bytes.fromhex("8012684e")),
    (0x2E356D3, bytes.fromhex("b908")),
    (0x2E356D6, bytes.fromhex("8012685e")),
    (0x2E356DB, bytes.fromhex("b968")),
    (0x2E356DE, bytes.fromhex("8052685a")),
    (0x2E356E3, bytes.fromhex("b97f36")),
    (0x2E356E7, bytes.fromhex("f928")),
    (0x2E356EA, bytes.fromhex("8052684a0239e00313aa7bfcff97fd7b46a9fb7345a9f96b44a9f76343a9f55b42a9f35341a9e80340fdff03029190bded17")),
    (0x2E4BA30, bytes.fromhex("f44fbea9fd7b01a9fd43")),
    (0x2E4BA3B, bytes.fromhex("91ff43")),
    (0x2E4BA3F, bytes.fromhex("d1e003")),
    (0x2E4BA43, bytes.fromhex("f9f303")),
    (0x2E4BA47, bytes.fromhex("aae1031faafa2ff8978003")),
    (0x2E4BA53, bytes.fromhex("b4f303")),
    (0x2E4BA57, bytes.fromhex("aa684e40b91f01")),
    (0x2E4BA5F, bytes.fromhex("710b03")),
    (0x2E4BA63, bytes.fromhex("5468064239c802")),
    (0x2E4BA6B, bytes.fromhex("34684a40b91f01")),
    (0x2E4BA73, bytes.fromhex("716b02")),
    (0x2E4BA77, bytes.fromhex("54e00340f9d667f897")),
    (0x2E4BA81, bytes.fromhex("02")),
    (0x2E4BA83, bytes.fromhex("b4e1031faa69d2ec97a001")),
    (0x2E4BA8F, bytes.fromhex("b4614a40b9e2031faa1cdeec972001")),
    (0x2E4BA9F, bytes.fromhex("b4")),
    (0x2E4BAA1, bytes.fromhex("2840f9e0")),
    (0x2E4BAA7, bytes.fromhex("b4081840b9694e40b93f01086b6b")),
    (0x2E4BAB7, bytes.fromhex("5408")),
    (0x2E4BABA, bytes.fromhex("8012684e")),
    (0x2E4BABF, bytes.fromhex("b9e00340f9ff43")),
    (0x2E4BAC7, bytes.fromhex("915241f817")),
    (0x2E4BB00, bytes.fromhex("fd7bbba9f35301a9f55b02a9f033")),
    (0x2E4BB0F, bytes.fromhex("b9e01f")),
    (0x2E4BB13, bytes.fromhex("f9d59b")),
    (0x2E4BB17, bytes.fromhex("d0b52a40f9e00315aa3ecd7a97a00240f9b6f10a94a0")),
    (0x2E4BB2F, bytes.fromhex("b4e1031faac02ff89740")),
    (0x2E4BB3B, bytes.fromhex("b495a3ff9748c6")),
    (0x2E4BB43, bytes.fromhex("d013e147b93302")),
    (0x2E4BB4B, bytes.fromhex("341fe107b9559d")),
    (0x2E4BB53, bytes.fromhex("f0b5da42f9e00315aa2fcd7a97a00240f9a7f10a942001")),
    (0x2E4BB6B, bytes.fromhex("b4c550f997e0")),
    (0x2E4BB73, bytes.fromhex("b4")),
    (0x2E4BB75, bytes.fromhex("b440f9a0")),
    (0x2E4BB7B, bytes.fromhex("b4082040b91f01136b41")),
    (0x2E4BB87, bytes.fromhex("541f20")),
    (0x2E4BB8B, bytes.fromhex("b9f03340b9e01f40f9f55b42a9f35341a9fd7bc5a81f0a")),
    (0x2E4BBA3, bytes.fromhex("7180")),
    (0x2E4BBA7, bytes.fromhex("54f44fbea9fd7b01a9c147f817f50f1df8f44f01a9da49f817fd7bbda9fd03")),
    (0x2E4BBC7, bytes.fromhex("91f35301a9f513")),
    (0x2E4BBCF, bytes.fromhex("f9f303")),
    (0x2E4BBD3, bytes.fromhex("aa28")),
    (0x2E4BBD6, bytes.fromhex("80526862")),
    (0x2E4BBDB, bytes.fromhex("396866")),
    (0x2E4BBDF, bytes.fromhex("39689d")),
    (0x2E4BBE3, bytes.fromhex("90083d44f9e00308aa0bcd7a97689d")),
    (0x2E4BBF3, bytes.fromhex("90083d44f9")),
    (0x2E4BBF9, bytes.fromhex("0140f981f10a94a003")),
    (0x2E4BC03, bytes.fromhex("b4e1031faa9e50f9974003")),
    (0x2E4BC0F, bytes.fromhex("b4f403")),
    (0x2E4BC13, bytes.fromhex("aae00314aa611240f9e2031faa6e86f397e00314aa611640f9e2031faa49ed0294e00314aa613240b995ed0294e00314aa613640b9cded0294e00314aa611e40f9e2031faa3c87f397e00314aa614240b901ee0294e00314aa614640b939ee029415")),
    (0x2E4BC77, bytes.fromhex("90b5823a91e00315aaad6d7897611240f961")),
    (0x2E4BC8B, bytes.fromhex("b4e2031faa1ce0b697a012")),
    (0x2E4BC97, bytes.fromhex("91a76d7897611640f961")),
    (0x2E4BCA3, bytes.fromhex("b4e2031faa16e0b697a022")),
    (0x2E4BCAF, bytes.fromhex("91a16d7897613240b9e2031faa5cdfb697a032")),
    (0x2E4BCC3, bytes.fromhex("919c6d7897613640b9e2031faa57dfb697a042")),
    (0x2E4BCD7, bytes.fromhex("91976d7897614240b9e2031faa52dfb697a052")),
    (0x2E4BCEB, bytes.fromhex("91926d7897614640b9e2031faa4ddfb697a062")),
    (0x2E4BCFF, bytes.fromhex("918d6d7897611e40f961")),
    (0x2E4BD0B, bytes.fromhex("b4e2031faafcdfb697a072")),
    (0x2E4BD17, bytes.fromhex("91876d789721")),
    (0x2E4BD1E, bytes.fromhex("8052e2031faa42dfb697e0031faa7be0b697f35341a9f51340f9fd7bc3a8c0035fd6fd7bbea9f35301a9f303")),
    (0x2E4BD4B, bytes.fromhex("aa51")),
    (0x2E4BD4F, bytes.fromhex("94f403")),
    (0x2E4BD53, bytes.fromhex("2ae00313aa06")),
    (0x2E4BD5B, bytes.fromhex("94e003142af35341a9fd7bc2a8c0035fd6")),
    (0x2E4BD70, bytes.fromhex("fd7bbda9fd03")),
    (0x2E4BD77, bytes.fromhex("91f35301a9f513")),
    (0x2E4BD7F, bytes.fromhex("f9f303")),
    (0x2E4BD83, bytes.fromhex("aab307")),
    (0x2E4BD87, bytes.fromhex("b415")),
    (0x2E4BD8B, bytes.fromhex("90b5823a91a072")),
    (0x2E4BD93, bytes.fromhex("91686d7897e1031faa7cdfb6971f04")),
    (0x2E4BDA3, bytes.fromhex("71a106")),
    (0x2E4BDA7, bytes.fromhex("54e00315aa626d7897e1031faa0ee0b697e103")),
    (0x2E4BDBB, bytes.fromhex("aae00313aae2031faa0586f397a012")),
    (0x2E4BDCB, bytes.fromhex("915a6d7897e1031faa06e0b697e103")),
    (0x2E4BDDB, bytes.fromhex("aae00313aae2031faadcec0294a022")),
    (0x2E4BDEB, bytes.fromhex("91526d7897e1031faa66dfb697e103")),
    (0x2E4BDFB, bytes.fromhex("2ae00313aa24ed0294a032")),
    (0x2E4BE07, bytes.fromhex("914b6d7897e1031faa5fdfb697e103")),
    (0x2E4BE17, bytes.fromhex("2ae00313aa58ed0294a042")),
    (0x2E4BE23, bytes.fromhex("91446d7897e1031faa58dfb697e103")),
    (0x2E4BE33, bytes.fromhex("2ae00313aa8ced0294a052")),
    (0x2E4BE3F, bytes.fromhex("913d6d7897e1031faa51dfb697e103")),
    (0x2E4BE4F, bytes.fromhex("2ae00313aac0ed0294a062")),
    (0x2E4BE5B, bytes.fromhex("91366d7897e1031faae2dfb697e103")),
    (0x2E4BE6B, bytes.fromhex("aae00313aae2031faab586f397f35341a9f51340f9fd7bc3a8c0035fd6")),
    (0x2E4BE90, bytes.fromhex("ff4303d135f70214")),
    (0x2E4BEA0, bytes.fromhex("66706e")),
    (0x2E4BEA4, bytes.fromhex("667073")),
    (0x2E4BEA8, bytes.fromhex("667078")),
    (0x2E4BEAC, bytes.fromhex("667068")),
    (0x2E4BEB0, bytes.fromhex("667062")),
    (0x2E4BEB4, bytes.fromhex("667064")),
    (0x2E4BEB8, bytes.fromhex("667063")),
    (0x2E4BEBC, bytes.fromhex("663170")),
    (0x2E4BEC0, bytes.fromhex("4354584f4b")),
    (0x2E4BEC6, bytes.fromhex("4855444f4b")),
    (0x2E4BF00, bytes.fromhex("e903")),
    (0x2E4BF03, bytes.fromhex("aa")),
    (0x2E4BF05, bytes.fromhex("2040b9e0")),
    (0x2E4BF0B, bytes.fromhex("3548c6")),
    (0x2E4BF0F, bytes.fromhex("d008e147b968")),
    (0x2E4BF17, bytes.fromhex("34e003082ac0035fd6201140b9c0035fd6")),
    (0x2E4BF30, bytes.fromhex("fd7bbba9fd03")),
    (0x2E4BF37, bytes.fromhex("91f35301a9f55b02a9f76303a9f303")),
    (0x2E4BF47, bytes.fromhex("aaf503022af80301aa61")),
    (0x2E4BF53, bytes.fromhex("b4281840b92808")),
    (0x2E4BF5B, bytes.fromhex("3580028052f274ed97a007")),
    (0x2E4BF67, bytes.fromhex("b4f603")),
    (0x2E4BF6B, bytes.fromhex("aa089e")),
    (0x2E4BF6F, bytes.fromhex("b0084143f9e00308aa28cc7a97889e")),
    (0x2E4BF7F, bytes.fromhex("d0086946f9e00308aa24cc7a97089d")),
    (0x2E4BF8F, bytes.fromhex("9008e544f9e00308aa20cc7a97089e")),
    (0x2E4BF9F, bytes.fromhex("b0084143f9")),
    (0x2E4BFA5, bytes.fromhex("0140f950cc7a976005")),
    (0x2E4BFAF, bytes.fromhex("b4f403")),
    (0x2E4BFB3, bytes.fromhex("aa889e")),
    (0x2E4BFB7, bytes.fromhex("d0086946f9010140f9dd5fda97f7031f2ac81a40b9ff02086baa02")),
    (0x2E4BFD3, bytes.fromhex("54c90a40f96902")),
    (0x2E4BFDB, bytes.fromhex("b42981")),
    (0x2E4BFDF, bytes.fromhex("91385977b808")),
    (0x2E4BFE7, bytes.fromhex("b008810291")),
    (0x2E4BFED, bytes.fromhex("49378bd16c7897e1031faad1deb697e203")),
    (0x2E4BFFF, bytes.fromhex("2ae10318aa218002aae89c")),
    (0x2E4C00B, bytes.fromhex("f008e544f9020140f9e00314aa1f63da97f706")),
    (0x2E4C01F, bytes.fromhex("11eaffff17c89b")),
    (0x2E4C027, bytes.fromhex("b0082940f9")),
    (0x2E4C02D, bytes.fromhex("0140f974f00a94e0")),
    (0x2E4C037, bytes.fromhex("b4e1031faa7e2ef89780")),
    (0x2E4C043, bytes.fromhex("b4")),
    (0x2E4C045, bytes.fromhex("c00191e10314aadacb7a97e10314aa02")),
    (0x2E4C057, bytes.fromhex("14e10318aae00313aae203152af35341a9f55b42a9f76343a9fd7bc5a8f657bda9f44f01a9fd7b02a9fd83")),
    (0x2E4C083, bytes.fromhex("915840f817")),
    (0x2E4C0A0, bytes.fromhex("6b30")),
    (0x2E4C0A4, bytes.fromhex("6b31")),
    (0x2E4C0A8, bytes.fromhex("6b32")),
    (0x2E4C0AC, bytes.fromhex("6b33")),
    (0x2E4C0B0, bytes.fromhex("6b34")),
    (0x2E4C0B4, bytes.fromhex("6b35")),
    (0x2E4C0B8, bytes.fromhex("6b36")),
    (0x2E4C0BC, bytes.fromhex("6b37")),
    (0x2E4C0C0, bytes.fromhex("6b38")),
    (0x2E4C0C4, bytes.fromhex("6b39")),
    (0x2E4C0C8, bytes.fromhex("6b61")),
    (0x2E4C0CC, bytes.fromhex("6b62")),
    (0x2E4C0D0, bytes.fromhex("6b63")),
    (0x2E4C0D4, bytes.fromhex("6b64")),
    (0x2E4C0D8, bytes.fromhex("6b65")),
    (0x2E4C0DC, bytes.fromhex("6b66")),
    (0x2E4C0E0, bytes.fromhex("6b67")),
    (0x2E4C0E4, bytes.fromhex("6b68")),
    (0x2E4C0E8, bytes.fromhex("6b69")),
    (0x2E4C0EC, bytes.fromhex("6b6a")),
    (0x2E4C0F0, bytes.fromhex("6b6b")),
    (0x2E4C0F4, bytes.fromhex("6b6c")),
    (0x2E4C0F8, bytes.fromhex("6b6d")),
    (0x2E4C0FC, bytes.fromhex("6b6e")),
    (0x2E4C100, bytes.fromhex("fd7bbca9fd03")),
    (0x2E4C107, bytes.fromhex("91f35301a9f55b02a9f71b")),
    (0x2E4C113, bytes.fromhex("f9141040f97402")),
    (0x2E4C11B, bytes.fromhex("b4951a40b9960a40f91602")),
    (0x2E4C127, bytes.fromhex("b4f7031f2aff02156baa01")),
    (0x2E4C133, bytes.fromhex("54c84e378b")),
    (0x2E4C139, bytes.fromhex("1140f9")),
    (0x2E4C13D, bytes.fromhex("01")),
    (0x2E4C13F, bytes.fromhex("b41bd69c97ff4e9a971f0c")),
    (0x2E4C14B, bytes.fromhex("7181")),
    (0x2E4C14F, bytes.fromhex("54c84e378b")),
    (0x2E4C155, bytes.fromhex("1140f92a01")),
    (0x2E4C15B, bytes.fromhex("94f706")),
    (0x2E4C15F, bytes.fromhex("11f3ffff17f71b40f9f55b42a9f35341a9fd7bc4a8c0035fd6")),
    (0x2E4C180, bytes.fromhex("fd7bbda9fd03")),
    (0x2E4C187, bytes.fromhex("91f35301a9f513")),
    (0x2E4C18F, bytes.fromhex("f9e017")),
    (0x2E4C193, bytes.fromhex("f9dbffff97e01740f9f51340f9f35341a9fd7bc3a8f50f1df847740614")),
    (0x2E4C200, bytes.fromhex("48c6")),
    (0x2E4C203, bytes.fromhex("b009e147b949")),
    (0x2E4C20B, bytes.fromhex("340920")),
    (0x2E4C20F, bytes.fromhex("b9f50f1df8f44f01a9fd7b02a9fd83")),
    (0x2E4C21F, bytes.fromhex("9150d10214")),
    (0x2E4C300, bytes.fromhex("fd7bbea9fd03")),
    (0x2E4C307, bytes.fromhex("91f35301a9f303")),
    (0x2E4C30F, bytes.fromhex("aaa7d59c978b4e9a971f0c")),
    (0x2E4C31B, bytes.fromhex("7161")),
    (0x2E4C31F, bytes.fromhex("54e00313aab7")),
    (0x2E4C327, bytes.fromhex("94e00313aaf35341a9fd7bc2a8f50f1df8ab13")),
    (0x2E4C33B, bytes.fromhex("14")),
    (0x2E4C400, bytes.fromhex("fd7bbca9fd03")),
    (0x2E4C407, bytes.fromhex("91f35301a9f513")),
    (0x2E4C40F, bytes.fromhex("f9e017")),
    (0x2E4C413, bytes.fromhex("f966d59c974a4e9a97f303")),
    (0x2E4C41F, bytes.fromhex("2ae01740f962d59c9707ef999780")),
    (0x2E4C42F, bytes.fromhex("b4444e9a97f403")),
    (0x2E4C437, bytes.fromhex("2a02")),
    (0x2E4C43B, bytes.fromhex("1414")),
    (0x2E4C43E, bytes.fromhex("801280")),
    (0x2E4C442, bytes.fromhex("805201")),
    (0x2E4C447, bytes.fromhex("9021")),
    (0x2E4C44A, bytes.fromhex("209102")),
    (0x2E4C44F, bytes.fromhex("90421c2091e303132ae403142a113573977f0e")),
    (0x2E4C463, bytes.fromhex("71e103")),
    (0x2E4C467, bytes.fromhex("5448c6")),
    (0x2E4C46B, bytes.fromhex("b014e147b90a")),
    (0x2E4C473, bytes.fromhex("904a012591e9031f2a4b5969b87f01146bc0")),
    (0x2E4C487, bytes.fromhex("542905")),
    (0x2E4C48B, bytes.fromhex("113f29")),
    (0x2E4C48F, bytes.fromhex("716bffff54e9031f2a05")),
    (0x2E4C49B, bytes.fromhex("142905")),
    (0x2E4C49F, bytes.fromhex("113f29")),
    (0x2E4C4A3, bytes.fromhex("714b")),
    (0x2E4C4A7, bytes.fromhex("54e9031f2a545969b814e107b9f503092a80")),
    (0x2E4C4BA, bytes.fromhex("805201")),
    (0x2E4C4BF, bytes.fromhex("9021")),
    (0x2E4C4C2, bytes.fromhex("209102")),
    (0x2E4C4C7, bytes.fromhex("9042582091e303152ae403142af3347397e01740f949")),
    (0x2E4C4DF, bytes.fromhex("94f51340f9f35341a9fd7bc4a8c0035fd6")),
    (0x2E4C600, bytes.fromhex("fd7bbca9fd03")),
    (0x2E4C607, bytes.fromhex("91f35301a9f55b02a9f303")),
    (0x2E4C613, bytes.fromhex("aa48c6")),
    (0x2E4C617, bytes.fromhex("b014e147b909")),
    (0x2E4C61F, bytes.fromhex("9029012591f5031f2a2a5975b85f01146ba0")),
    (0x2E4C633, bytes.fromhex("54b506")),
    (0x2E4C637, bytes.fromhex("11bf2a")),
    (0x2E4C63B, bytes.fromhex("716bffff5455018052")),
    (0x2E4C647, bytes.fromhex("90")),
    (0x2E4C649, bytes.fromhex("a02591")),
    (0x2E4C64D, bytes.fromhex("50358b396b7897f603")),
    (0x2E4C657, bytes.fromhex("aa603a40f980")),
    (0x2E4C65F, bytes.fromhex("b4e10316aae2031faa01a28897602640f9c0")),
    (0x2E4C673, bytes.fromhex("b4")),
    (0x2E4C675, bytes.fromhex("0c40f980")),
    (0x2E4C67B, bytes.fromhex("b4e1031f2ae2031faaf2f29c97606e40f9e0")),
    (0x2E4C68F, bytes.fromhex("b4e1031faad6d49c9780")),
    (0x2E4C69B, bytes.fromhex("b4e1031f2ae2031faaeaf29c97603640f9e0")),
    (0x2E4C6AF, bytes.fromhex("b4e1031faaced49c9780")),
    (0x2E4C6BB, bytes.fromhex("b4e1031f2ae2031faae2f29c97605e40f9e0")),
    (0x2E4C6CF, bytes.fromhex("b4e1031faac6d49c9780")),
    (0x2E4C6DB, bytes.fromhex("b4e1031f2ae2031faadaf29c97606240f9e0")),
    (0x2E4C6EF, bytes.fromhex("b4e1031faabed49c9780")),
    (0x2E4C6FB, bytes.fromhex("b4e1031f2ae2031faad2f29c97f55b42a9f35341a9fd7bc4a8c0035fd6")),
    (0x2E4C800, bytes.fromhex("46315445414d")),
    (0x2E4C807, bytes.fromhex("736c6f7420256420706172202564")),
    (0x2E4C816, bytes.fromhex("7465616d20256420756964202564")),
    (0x2E4C900, bytes.fromhex("014c40b9882a40f96801")),
    (0x2E4C90B, bytes.fromhex("b4091940b93f01")),
    (0x2E4C913, bytes.fromhex("710d01")),
    (0x2E4C917, bytes.fromhex("543f")),
    (0x2E4C91B, bytes.fromhex("71ab")),
    (0x2E4C91F, bytes.fromhex("543f")),
    (0x2E4C922, bytes.fromhex("096b8b")),
    (0x2E4C927, bytes.fromhex("542105")),
    (0x2E4C92B, bytes.fromhex("5102")),
    (0x2E4C92F, bytes.fromhex("1401")),
    (0x2E4C932, bytes.fromhex("8052e066f817")),
    (0x2E4C940, bytes.fromhex("f66e")),
    (0x2E4C944, bytes.fromhex("ac6f")),
    (0x2E4C948, bytes.fromhex("cd70")),
    (0x2E4C94C, bytes.fromhex("c373")),
    (0x2E4C950, bytes.fromhex("5b74")),
    (0x2E4C954, bytes.fromhex("eb74")),
    (0x2E4C958, bytes.fromhex("3f72")),
    (0x2E4C95C, bytes.fromhex("c875")),
    (0x2E4C960, bytes.fromhex("5c76")),
    (0x2E4C964, bytes.fromhex("ae71")),
    (0x2E4C968, bytes.fromhex("46657272617269")),
    (0x2E4C978, bytes.fromhex("4d65726365646573")),
    (0x2E4C988, bytes.fromhex("5265642042756c6c")),
    (0x2E4C998, bytes.fromhex("4d634c6172656e")),
    (0x2E4C9A8, bytes.fromhex("416c70696e65")),
    (0x2E4C9B8, bytes.fromhex("416c7068615461757269")),
    (0x2E4C9C8, bytes.fromhex("4173746f6e204d617274696e")),
    (0x2E4C9D8, bytes.fromhex("57696c6c69616d73")),
    (0x2E4C9E8, bytes.fromhex("416c666120526f6d656f")),
    (0x2E4C9F8, bytes.fromhex("48616173")),
    (0x2E4CA08, bytes.fromhex("53656c656374207465616d")),
    (0x2E511E0, bytes.fromhex("48ecff17")),
    (0x2E51840, bytes.fromhex("f0eaff17")),
    (0x2E69090, bytes.fromhex("f353baa9f55b01a9f76302a9f96b03a9fb7304a9fd7b05a9fd430191f30301aaf40302aaf503032af603042af70305aaf803062af903072a689c")),
    (0x2E690CB, bytes.fromhex("d0083d44f9e00308aad1577a97689c")),
    (0x2E690DB, bytes.fromhex("d0083d44f9")),
    (0x2E690E1, bytes.fromhex("0140f9477c0a944004")),
    (0x2E690EB, bytes.fromhex("b4e1031faa64dbf897e003")),
    (0x2E690F7, bytes.fromhex("b4fa03")),
    (0x2E690FB, bytes.fromhex("aae0031aaae10313aae2031faa3411f397e0031aaae10314aae2031faa0f780294e0031aaae103152a5b780294e0031aaae103162a93780294e0031aaae10317aae2031faa0212f397e0031aaae103182ac7780294e0031aaae103192aff78029420")),
    (0x2E6915E, bytes.fromhex("805282310194e0031aaae1031f2ad03101941bffffd07b833a91e0031baa6ef8779793")),
    (0x2E69183, bytes.fromhex("b4e10313aae2031faadd6ab6976013")),
    (0x2E69193, bytes.fromhex("9168f8779794")),
    (0x2E6919B, bytes.fromhex("b4e10314aae2031faad76ab6976023")),
    (0x2E691AB, bytes.fromhex("9162f87797e103152ae2031faa1d6ab6976033")),
    (0x2E691BF, bytes.fromhex("915df87797e103162ae2031faa186ab6976043")),
    (0x2E691D3, bytes.fromhex("9158f87797e103182ae2031faa136ab6976053")),
    (0x2E691E7, bytes.fromhex("9153f87797e103192ae2031faa0e6ab6976063")),
    (0x2E691FB, bytes.fromhex("914ef8779797")),
    (0x2E69203, bytes.fromhex("b4e10317aae2031faabd6ab6976073")),
    (0x2E69213, bytes.fromhex("9148f8779721")),
    (0x2E6921A, bytes.fromhex("8052e2031faa036ab697e0031faa3c6bb697fd7b45a9fb7344a9f96b43a9f76342a9f55b41a9f353c6a8128ef417")),
    (0x2E69280, bytes.fromhex("fd7bbda9fd03")),
    (0x2E69287, bytes.fromhex("91f35301a9f513")),
    (0x2E6928F, bytes.fromhex("f9f303")),
    (0x2E69293, bytes.fromhex("aa13")),
    (0x2E69297, bytes.fromhex("94f403")),
    (0x2E6929B, bytes.fromhex("2ae00313aab48aff97e003142af51340f9f35341a9fd7bc3a8c0035fd6")),
    (0x2E692E0, bytes.fromhex("fa67bba90a920214")),
    (0x2E69300, bytes.fromhex("940e40f91402")),
    (0x2E69307, bytes.fromhex("b48a1a40b98b0a40f9ab01")),
    (0x2E69313, bytes.fromhex("b46b81")),
    (0x2E69317, bytes.fromhex("91ec031f2aed031f2a9f010a6bea")),
    (0x2E69327, bytes.fromhex("546e596cf86e")),
    (0x2E6932F, bytes.fromhex("b46e592df8ad05")),
    (0x2E69337, bytes.fromhex("118c05")),
    (0x2E6933B, bytes.fromhex("11f9ffff178d1a")),
    (0x2E69343, bytes.fromhex("b9e2aff817")),
    (0x2E69380, bytes.fromhex("940e40f91402")),
    (0x2E69387, bytes.fromhex("b48a1a40b98b0a40f9ab01")),
    (0x2E69393, bytes.fromhex("b46b81")),
    (0x2E69397, bytes.fromhex("91ec031f2aed031f2a9f010a6bea")),
    (0x2E693A7, bytes.fromhex("546e596cf86e")),
    (0x2E693AF, bytes.fromhex("b46e592df8ad05")),
    (0x2E693B7, bytes.fromhex("118c05")),
    (0x2E693BB, bytes.fromhex("11f9ffff178d1a")),
    (0x2E693C3, bytes.fromhex("b945b0f817")),
    (0x2E693E0, bytes.fromhex("62")),
    (0x2E693E3, bytes.fromhex("b420")),
    (0x2E693E6, bytes.fromhex("8052d5120214e0031f2ad3120214")),
    (0x2E69402, bytes.fromhex("8012ce120214")),
    (0x2E69420, bytes.fromhex("62")),
    (0x2E69423, bytes.fromhex("b420")),
    (0x2E69426, bytes.fromhex("805210150214e0031f2a0e150214")),
    (0x2E69442, bytes.fromhex("801209150214")),
    (0x2E69460, bytes.fromhex("600a40f9810a40f9e2031faafd7eca9760")),
    (0x2E69473, bytes.fromhex("34e0031f2ab1120214")),
    (0x2E6947E, bytes.fromhex("8012af120214")),
    (0x2E694A0, bytes.fromhex("600a40f9810a40f9e2031faaed7eca9760")),
    (0x2E694B3, bytes.fromhex("34e0031f2aec140214")),
    (0x2E694BE, bytes.fromhex("8012ea140214")),
    (0x2E69600, bytes.fromhex("fd7bbea9fd03")),
    (0x2E69607, bytes.fromhex("91e00701a9689c")),
    (0x2E6960F, bytes.fromhex("d0083d44f9e00308aa80567a97689c")),
    (0x2E6961F, bytes.fromhex("d0083d44f9")),
    (0x2E69625, bytes.fromhex("0140f9f67a0a94a0")),
    (0x2E6962F, bytes.fromhex("b4e1031faa13daf89740")),
    (0x2E6963B, bytes.fromhex("b4cd89ff97e00741a9fd7bc2a8f50f1df80268f717")),
    (0x2E69F40, bytes.fromhex("fd7bbea9fd03")),
    (0x2E69F47, bytes.fromhex("91e007bea9e20f1ff8689c")),
    (0x2E69F53, bytes.fromhex("d0083d44f9e00308aa2f547a97689c")),
    (0x2E69F63, bytes.fromhex("d0083d44f9")),
    (0x2E69F69, bytes.fromhex("0140f9a5780a946002")),
    (0x2E69F73, bytes.fromhex("b4e1031faac2d7f897")),
    (0x2E69F7D, bytes.fromhex("02")),
    (0x2E69F7F, bytes.fromhex("b47c87ff97689c")),
    (0x2E69F87, bytes.fromhex("d0083d44f9")),
    (0x2E69F8D, bytes.fromhex("0140f99c780a944001")),
    (0x2E69F97, bytes.fromhex("b4e1031faab9d7f897e0")),
    (0x2E69FA3, bytes.fromhex("b4e003")),
    (0x2E69FA7, bytes.fromhex("f920")),
    (0x2E69FAA, bytes.fromhex("8052ef2d0194e00340f9e1031f2a3d2e0194ff43")),
    (0x2E69FBF, bytes.fromhex("91e007c2a8fd7bc2a8f657bda99b7ef417")),
    (0x2E6A000, bytes.fromhex("fd7bbea9fd03")),
    (0x2E6A007, bytes.fromhex("91e007bea9689c")),
    (0x2E6A00F, bytes.fromhex("b0083d44f9e00308aa")),
    (0x2E6A019, bytes.fromhex("547a97689c")),
    (0x2E6A01F, bytes.fromhex("b0083d44f9")),
    (0x2E6A025, bytes.fromhex("0140f976780a94a0")),
    (0x2E6A02F, bytes.fromhex("b4e1031faa93d7f89740")),
    (0x2E6A03B, bytes.fromhex("b44d87ff97e007c2a8fd7bc2a8f50f1df8b28af41754")),
    (0x2E6A053, bytes.fromhex("b560c2ec17811a40b9a89d")),
    (0x2E6A05F, bytes.fromhex("b0086142f9080140f9e00308aaf1537a972bc1ec17")),
    (0x2ED3DF0, bytes.fromhex("1f2003d5")),
    (0x2EEDEA0, bytes.fromhex("01aabd")),
    (0x2EEDEBC, bytes.fromhex("33aabd")),
    (0x2EEDED0, bytes.fromhex("93a9bd")),
    (0x2EEDEEC, bytes.fromhex("b3a8bd")),
    (0x2EEDF1C, bytes.fromhex("20aabd35")),
    (0x2EEE790, bytes.fromhex("8164bd")),
    (0x2EEE7B0, bytes.fromhex("9364bd")),
    (0x2EEE7C8, bytes.fromhex("d363bd")),
    (0x2EEE7E8, bytes.fromhex("d362bd")),
    (0x2EEE848, bytes.fromhex("c062bd35")),
    (0x2F00570, bytes.fromhex("642efd17")),
    (0x2F00750, bytes.fromhex("ac2efd17")),
    (0x2F09B64, bytes.fromhex("7708fd17")),
    (0x2F0DB08, bytes.fromhex("de6dfd17")),
    (0x2F0DE7C, bytes.fromhex("c0035fd6")),
    (0x2F0DF6C, bytes.fromhex("c0035fd6")),
    (0x2F0E140, bytes.fromhex("c0035fd6")),
    (0x2F1386C, bytes.fromhex("28008052")),
    (0x2F22698, bytes.fromhex("28008052")),
    (0x2F23154, bytes.fromhex("28008052")),
    (0x2F24020, bytes.fromhex("28008052")),
    (0x2FE92C4, bytes.fromhex("af8bf917")),
    (0x2FFA90C, bytes.fromhex("28008052")),
    (0x30165F0, bytes.fromhex("6434f717")),
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


# ASN.1 / RSA (pure Python, stdlib only)


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


# APK Signature Scheme v2

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


# ZIP writer (4-byte aligns stored entries, like zipalign)

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


# main


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
