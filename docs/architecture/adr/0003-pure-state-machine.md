# ADR-0003: State machine as a pure function of time and inputs

**Status:** Accepted

## Context
Every state depends on timers (2 s pause, 3 s turn, 40 s stuck, 8 s water timeout). With
`time.time()` and `enviar()` inside, testing would take real minutes and need a serial port.

## Decision
`BeachBotFsm.tick(now, detection, water)` returns the commands and the sleep time. It never reads the
clock or sends anything. `apps/master_app.run()` does the I/O.

## Consequences
- (+) Minutes of robot behaviour are simulated in milliseconds.
- (+) Golden tests can compare it with the original line by line.
- (−) The caller must pass `now`; documented in the development view.
