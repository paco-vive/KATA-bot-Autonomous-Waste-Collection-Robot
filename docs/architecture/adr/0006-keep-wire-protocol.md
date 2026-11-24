# ADR-0006: Keep the pipe and UART protocols unchanged

**Status:** Accepted

## Context
The master sends commands (`CR`, `CL`, `BL`, `BK`, `BA`, `DO`, `DC`, `F`, `J`, `M`) that the recovered
firmware does not implement in autonomous mode. Their exact motor behaviour (curve radius, door actuator,
pins) is not recorded anywhere in the repository.

## Decision
Keep both protocols byte-for-byte. Do not guess the missing firmware behaviour; document the gap
(process view §4) and centralise the command names in `domain/commands.py` so they are easy to implement.

## Consequences
- (+) The refactored Pi software works with any firmware that worked before.
- (−) The gap remains until the team implements those commands and tests them on the robot.
