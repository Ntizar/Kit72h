#!/usr/bin/env python3
"""Runner para el briefing del consejero"""
import subprocess
import sys

result = subprocess.run(
    ["python3", "scripts/kit72h-consejero.py", "--briefing"],
    capture_output=True,
    text=True,
    cwd="/home/nan/Projects/kit72h"
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr, file=sys.stderr)
sys.exit(result.returncode)