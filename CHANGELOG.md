# Changelog

## 2.0.0 (2026-11-24): architecture refactor, same behaviour

- Python code reorganised into the `kata_bot` package (ports and adapters, SOLID). `scripts/vision.py`
  and `scripts/maestro.py` still start the robot exactly as before.
- State machine made pure (injected clock); all parameters moved to `config.py`.
- ESP32 firmware split into `config.h`, `DriveTrain`, `CommandProcessor` and adapters; Wi-Fi credentials
  can be overridden in a git-ignored `secrets.h`. Folder renamed `kata_marzo` → `kata_firmware`.
- Tests: golden tests against the TMR 2026 code, unit tests, synthetic vision tests, firmware host tests.
- Documentation: RUP Vision, SRS, SAD, 4+1 views, SOLID mapping, ADRs, test plan, glossary.
- Added the MIT `LICENSE` file the README already referred to.
- No intentional behaviour change. The original scripts are tagged `tmr-2026`.

## 1.x: TMR 2026

- `vision.py` v6, `maestro.py` v8, firmware March–April 2026. 5th place nationally.
