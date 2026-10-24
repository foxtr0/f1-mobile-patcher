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

## What works

* **Boots fully offline** — no "network error" popup on startup; the game uses its
built-in offline profile.
* **Single races** — the `Duel` tile opens the offline race setup (track, race
type, laps, difficulty) and `Race` starts a normal race against AI, with HUD,
damage, and touch controls.
* **Graphics options** — `Game Options → Preferences` has a **Graphics quality**
row (removed from the new version), and the game is forced to its highest
profile: native resolution, 60 FPS target, 2048 px shadow cascades.

## What does not work

* **Career races** — signing a contract is a server (Nakama) request. The offer
screen opens and *Sign a contract* is enabled, but tapping it does nothing, so
no career weekend can be started. Career is browsing-only.
* **End-of-race results** — finishing a race does not show a results/leaderboard
screen. The single-race scene ships only a stub end panel, so you get the
race→menu transition screen instead. `Continue` still takes you back to the menu.
* **Everything online** — Events, Duel matchmaking, Showdown, Leagues, Shop /
purchases, leaderboards, cloud save, live challenges: all dead. The servers are
gone; this is not a server emulator.
* **Old progress** — the offline profile is new. Career/level/currency from the
live servers is gone.



