# Release process

Pixel Fight currently targets Windows x64 for packaged builds. PyInstaller is
not a cross-compiler, so the Windows artifact must be produced on Windows.
Other packaged platforms are not currently supported.

## Version policy

The plain-text `VERSION` file is the release version. `CHANGELOG.md` follows
Semantic Versioning:

- patch: compatible fixes and documentation;
- minor: compatible gameplay/features;
- major: intentionally incompatible controls, saves, or supported runtime.

Before tagging, move relevant entries from `Unreleased` into a dated version
whose number matches `VERSION`.

## Local Windows build

From a clean checkout with Python 3.13:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt -r requirements-build.txt
python -m pytest
python scripts/validate_assets.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

The script produces `dist/PixelFight-windows-x64.zip`. It builds an onedir
bundle, verifies every packaged asset by SHA-256, checks required documentation,
and performs an SDL-dummy executable startup check.

Extract the archive before running `PixelFight.exe`; do not run it from inside
the ZIP. Windows SmartScreen may warn because the executable is not code-signed.

## Automation

`.github/workflows/windows-build.yml` runs on manual dispatch and `v*` tags. It
validates the source, creates the Windows ZIP, and uploads it as a workflow
artifact. It deliberately does not create a public GitHub Release.

## Public-release gate

Do not publish the generated artifact until:

1. `THIRD_PARTY_NOTICES.md` maps every bundled asset to an exact source and
   redistribution license;
2. the project owner chooses a source-code license and adds its license file;
3. the ZIP is tested on a clean Windows x64 machine with a visible display;
4. menu, selector, one complete match, pause, restart, and exit are exercised;
5. the tag, `VERSION`, and changelog version agree.

After those checks, a release maintainer may create a GitHub Release manually
and attach the already validated ZIP. This repository does not currently
authorize that publication automatically.
