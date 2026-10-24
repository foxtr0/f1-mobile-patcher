# F1 Mobile Racing 5.4.11 - offline patcher

A single-file Python program that turns **your own original 5.4.11 APK** into
the offline-patched build. 


## What it needs

* The original `com.codemasters.F1Mobile` **5.4.11** APK (versionCode `24001341`).
  The tool verifies the `libil2cpp.so` SHA-256 before touching anything and
  refuses to run on a different build.
* Python 3 on a PC (Windows/macOS/Linux). 

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

* **Boots fully offline** - no "network error" popup on startup; the game uses its
built-in offline profile.
* **Single races** - the `Duel` tile opens the offline race setup (track, race
type, laps, difficulty) and `Race` starts a normal race against AI, with HUD,
damage, and touch controls.
* **Graphics options**- `Game Options → Preferences` has a **Graphics quality**
row (removed from the new version), and the game is forced to its highest
profile: native resolution, 60 FPS target, 2048 px shadow cascades.

## What does not work

* **Career races** - signing a contract is a server (Nakama) request. The offer
screen opens and *Sign a contract* is enabled, but tapping it does nothing, so
no career weekend can be started. Career is browsing-only.
* **End-of-race results** - finishing a race does not show a results/leaderboard
screen. The single-race scene ships only a stub end panel, so you get the
race→menu transition screen instead. `Continue` still takes you back to the menu.
* **Everything online** - Events, Duel matchmaking, Showdown, Leagues, Shop /
purchases, leaderboards, cloud save, live challenges: all dead. The servers are
gone; this is not a server emulator.

## How it works

### 1. Static reconnaissance

Unpack the APK and the OBB, confirm it is an IL2CPP Unity build (a 72 MB
`libil2cpp.so` plus `global-metadata.dat`), then run **Il2CppDumper** to get
`dump.cs` (every type, field, method with its RVA) and `script.json` (RVA → method
name). The string table (`string_literals.json`) is used to locate the code
around user-visible text, e.g. the network-error dialog or the quality labels.

### 2. Dynamic evidence from a real device

Every symptom was reproduced on the phone with `adb`, and the *logcat stack trace*
was treated as ground truth. A trace like

```
NullReferenceException
  at Eden.F1.Race.AutoDrivingHandler.StopPlayerToAutomaticDriving(IRaceMode)
  at IRaceMode.OnGameResumed  <- PauseManager.ResumeGame()
```

names the failing method directly, which is far cheaper than reading 31 MB of
`dump.cs`. Screenshots and repeated taps were used to confirm what the game was
actually doing (frozen clock, missing panel, wrong screen) before touching code.

### 3. Localisation

Method name → RVA from `script.json` → file offset (identity below `0x3faf5e8`)
→ disassemble that range with **Capstone** → read the actual logic (which field
is tested, which branch raises the error, which call returns null). Only after
the control flow was understood was a patch chosen.

### 4. Patch selection

A small menu of tactics, always preferring the least invasive:

| Tactic | When |
|---|---|
| force a predicate (getter / inline flag) | the code already has an offline/quality branch, it just tests the wrong value |
| stub with `ret` | the method is an online-only side effect that throws or blocks |
| retarget a branch | a null check raises where it should return, or the wrong UI path is taken |
| code cave (`b` + custom sequence) | the fix needs more than one instruction, e.g. calling a different API |

### 5. Verification

Every patch is applied to a **pristine copy**, with the original instruction
disassembled and asserted first; the finished library must match a pinned
SHA-256 or the build aborts. That makes the process reproducible and tells you
immediately when a different game version is fed in.



