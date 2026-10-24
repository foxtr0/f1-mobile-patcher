# F1 Mobile Racing 5.4.11 — offline patcher (v40)

A single-file Python program that turns **someone's own original 5.4.11 APK** into
the offline-patched build. 
```
f1mobile_patcher.py      the whole tool (Python 3.8+, standard library only)
```

## What it needs

* The original `com.codemasters.F1Mobile` **5.4.11** APK (versionCode `24001341`).
  The tool verifies the `libil2cpp.so` SHA-256 before touching anything and
  refuses to run on a different build.
* Python 3 on a PC (Windows/macOS/Linux). No Java, no Android SDK, no adb is
  needed to *produce* the patched APK.

## Usage

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

## What the patch changes

Only `lib/arm64-v8a/libil2cpp.so`, 70 instruction edits:

| Area | Effect |
|---|---|
| Offline mode | no network error at startup, built-in offline profile |
| Main menu | `PLAY` opens the original hub (Events / Duel / Showdown / Career) |
| Single race | the `Duel` tile opens the offline race setup (track / type / laps / difficulty) |
| Race HUD | no freeze when opening the in-race settings menu |
| Career | step / contract screens reachable, requisites cleared (signing itself needs the dead server) |
| Graphics | `Game Options → Preferences` gains a **Graphics quality** row |
| Quality | Q100 profile, native render resolution, 60 FPS target, 2048 px shadow cascades |


