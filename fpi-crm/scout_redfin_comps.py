#!/usr/bin/env python3
"""Shim — Scout helpers moved to /home/shanem/FPI-Corp/Scout/"""
import runpy
import sys
from pathlib import Path
sys.argv[0] = str(Path("/home/shanem/FPI-Corp/Scout/scout_redfin_comps.py"))
runpy.run_path("/home/shanem/FPI-Corp/Scout/scout_redfin_comps.py", run_name="__main__")
