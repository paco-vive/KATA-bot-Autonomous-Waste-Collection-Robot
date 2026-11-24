# ADR-0004: Golden tests against the TMR 2026 code

**Status:** Accepted

## Context
The robot placed 5th with the original code. A refactor that changes its behaviour by accident would
be worse than no refactor, and it cannot be re-tested in the arena easily.

## Decision
Keep verbatim copies of the competition scripts in `tests/reference/` and run them with the same
simulated clock and inputs as the new code. The command sequences must be identical.

## Consequences
- (+) Proof that the refactor preserves behaviour, including timing quirks.
- (+) Future intentional changes are visible: the golden test fails and must be updated on purpose.
- (−) The reference copies must never be "fixed"; they are a frozen baseline.
