# ADR-0001: Two processes linked by named pipes

**Status:** Accepted (decision made for TMR 2026, recorded in 2026-11)

## Context
Vision is CPU-heavy and can block on the camera; control must keep a steady rate and react to water.

## Decision
Run vision and master as separate processes. Vision writes text lines to two FIFOs: one for targets
and one dedicated to water, so a water alert is never queued behind target messages.

## Consequences
- (+) A slow frame does not freeze control; each process can be restarted.
- (+) Messages are human-readable (`cat /tmp/error_tracking` for debugging).
- (−) Linux-only; start-up order matters (vision blocks until the master opens the pipe).
