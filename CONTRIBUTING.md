# Contributing

Guide for the next KATA-bot team.

1. **Read first:** [Software Architecture Document](docs/architecture/00-software-architecture-document.md),
   then the view for the part you will touch.
2. **Set up:** `pip install -e ".[dev]"` and `make test` (everything must pass before you change anything).
3. **Tune, don't edit logic:** thresholds, gains and timings are in `src/kata_bot/config.py` and
   `firmware/esp32/kata_firmware/config.h`.
4. **Add behaviour in a new class** with one responsibility and a unit test, then wire it in
   `control/fsm.py` or `vision/pipeline.py`.
5. **Protocol changes** go in `domain/messages.py` / `domain/commands.py` and in the firmware, with
   tests on both sides.
6. **Golden tests** (`tests/test_golden_*.py`) protect the competition behaviour. If you change behaviour
   on purpose, update the scenario, explain why in `CHANGELOG.md` and, if it is a design decision, add an ADR
   in `docs/architecture/adr/`.
7. **Field-test** with the checklist in [docs/rup/03-test-plan.md](docs/rup/03-test-plan.md) before a competition.

Priority improvements: implement the master commands the firmware ignores
([process view §4](docs/architecture/03-process-view.md#4-known-gap-commands-the-firmware-ignores)),
then document the motors, battery and door actuator in the physical view.
