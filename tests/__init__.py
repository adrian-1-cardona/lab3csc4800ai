"""Tests for the uninformed search lab."""

import sys
from pathlib import Path

source_folder = Path(__file__).resolve().parents[1] / "src"
if str(source_folder) not in sys.path:
    sys.path.insert(0, str(source_folder))
