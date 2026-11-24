# ADR-0002: Ports and adapters with `typing.Protocol`

**Status:** Accepted

## Context
The original scripts mixed algorithms with OpenCV capture, pipes and serial I/O, so nothing could be
tested without the robot.

## Decision
Define narrow ports in `ports.py` (structural `Protocol`s, no inheritance needed). Algorithms depend
on ports; adapters in `adapters/` implement them; composition roots in `apps/` wire them.

## Consequences
- (+) The FSM and the vision pipeline run in tests with fakes.
- (+) Changing transport (e.g. to ROS 2) touches adapters only.
- (−) More files than two scripts; mitigated by the development view and this documentation.
