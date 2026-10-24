# f1-mobile-patcher
F1 Mobile Racing 5.4.11 — offline patcher (v40)
A single-file Python program that turns someone's own original 5.4.11 APK into
the offline-patched build.
```
f1mobile_patcher.py      the whole tool (Python 3.8+, standard library only)
```
What it needs
The original `com.codemasters.F1Mobile` 5.4.11 APK (versionCode `24001341`).
The tool verifies the `libil2cpp.so` SHA-256 before touching anything and
refuses to run on a different build.
Python 3 on a PC (Windows/macOS/Linux).
Usage
```bash
python f1mobile_patcher.py com.codemasters.F1Mobile_5.4.11.apk
# -> com.codemasters.F1Mobile_5.4.11-offline-patched.apk

# or choose the output name
python f1mobile_patcher.py input.apk -o patched.apk
```
On Windows you can also drag the APK onto `f1mobile_patcher.py` if `.py` files are
associated with Python.
It reads the APK, patches `lib/arm64-v8a/libil2cpp.so`, rebuilds the ZIP (keeping
`resources.arsc` uncompressed and 4-byte aligned), signs it with APK Signature
Scheme v2 and writes the result (~71 MB).
What the patch changes
Only `lib/arm64-v8a/libil2cpp.so`, 70 instruction edits:
Area	Effect
Offline mode	no network error at startup, built-in offline profile
Main menu	`PLAY` opens the original hub (Events / Duel / Showdown / Career)
Single race	the `Duel` tile opens the offline race setup (track / type / laps / difficulty)
Race HUD	no freeze when opening the in-race settings menu
Career	step / contract screens reachable, requisites cleared (signing itself needs the dead server)
Graphics	`Game Options → Preferences` gains a Graphics quality row
Quality	Q100 profile, native render resolution, 60 FPS target, 2048 px shadow cascades
Installing the result
The APK is signed with a local key, not EA's, so Android will not update the
store version in place. The phone must not have the store build installed:
```bash
# 1. back the OBB up first - uninstalling deletes it
adb pull /sdcard/Android/obb/com.codemasters.F1Mobile/main.24001341.com.codemasters.F1Mobile.obb

# 2. remove the store version, install the patched one
adb uninstall com.codemasters.F1Mobile
adb install -r com.codemasters.F1Mobile_5.4.11-offline-patched.apk

# 3. put the OBB back under its exact name
adb shell mkdir -p /sdcard/Android/obb/com.codemasters.F1Mobile
adb push main.24001341.com.codemasters.F1Mobile.obb /sdcard/Android/obb/com.codemasters.F1Mobile/
```
Without ADB: copy the OBB somewhere safe, uninstall F1 Mobile from the app
drawer, tap the patched APK (allow "install unknown apps"), then copy the OBB back
to `Android/obb/com.codemasters.F1Mobile/`.
Rooted phones (no data loss)
Instead of reinstalling, replace the library in place — the signature never
changes, so downloaded tracks and saves stay:
```bash
adb push libil2cpp.so /sdcard/Download/          # the patched .so produced by the tool
adb shell pm path com.codemasters.F1Mobile
# -> /data/app/~~XXXX/com.codemasters.F1Mobile-YYYY/base.apk
adb shell
su
cd /data/app/~~XXXX/com.codemasters.F1Mobile-YYYY/lib/arm64/
cp libil2cpp.so libil2cpp.so.orig
cp /sdcard/Download/libil2cpp.so .
chown $(stat -c %u:%g libil2cpp.so.orig) libil2cpp.so
chmod 644 libil2cpp.so
restorecon libil2cpp.so
```
(To get `libil2cpp.so` alone, point the tool at an APK and take the library out of
the produced APK, or simply run the tool and install — both give the same
library.)
Caveats
arm64 only. The patch rewrites `lib/arm64-v8a/libil2cpp.so`; a 32-bit phone
would still run the unpatched `armeabi-v7a` library.
v2 signature only. Fine for Android 7+ (the signed APK reports
`minSdkVersion 24` when verifying). A device on Android 6 or older would need
the JAR (v1) signature as well, which this tool does not create.
Uninstalling loses the track cache. The OBB ships only Silverstone; every
other circuit lives in the app's `UnityCache` and cannot be re-downloaded now
the servers are gone. The rooted route avoids this.
No store updates. The install is re-signed and will never update from Play.
Everything server-side (events, online races, purchases, leaderboards, career
contracts) stays dead. The tool only makes the offline part playable.
Verification
The patched library hash is checked inside the tool: the output must be
`e6667708…` for the v40 patch set, otherwise it aborts. The produced APK can be
checked with:
```bash
apksigner verify --min-sdk-version 24 -v patched.apk
# Verified using v2 scheme (APK Signature Scheme v2): true
```
