#!/usr/bin/env python3
"""Entry point kept for compatibility: `python3 scripts/vision.py`.

The implementation lives in src/kata_bot (see docs/architecture).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from kata_bot.apps.vision_app import main  # noqa: E402

if __name__ == "__main__":
    main()
