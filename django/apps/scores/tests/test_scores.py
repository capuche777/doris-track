"""Tests for scores app (Task #223 / DT-04)."""
import ast
import os
import sys

# Verify syntax of all Python files
BASE = "/opt/data/home/doris-track/django/apps/scores"
files = [
    f"{BASE}/__init__.py",
    f"{BASE}/apps.py",
    f"{BASE}/models.py",
    f"{BASE}/services.py",
    f"{BASE}/selectors.py",
    f"{BASE}/views.py",
    f"{BASE}/urls.py",
    f"{BASE}/admin.py",
]
ok = True
for f in files:
    if not os.path.exists(f):
        print(f"MISSING: {f}")
        ok = False
        continue
    with open(f) as fh:
        src = fh.read()
    try:
        ast.parse(src)
        print(f"OK: {os.path.basename(f)}")
    except SyntaxError as e:
        print(f"SYNTAX ERROR in {f}: {e}")
        ok = False

# Verify templates exist
tmpl_dir = "/opt/data/home/doris-track/templates/scores"
templates = ["score_list.html", "score_entry.html", "score_charts.html"]
for t in templates:
    path = f"{tmpl_dir}/{t}"
    if os.path.exists(path):
        print(f"OK: template {t}")
    else:
        print(f"MISSING: template {t}")
        ok = False

# Verify migration file
mig = f"{BASE}/migrations/0001_initial.py"
if os.path.exists(mig):
    with open(mig) as fh:
        src = fh.read()
    try:
        ast.parse(src)
        print(f"OK: migration")
    except SyntaxError as e:
        print(f"SYNTAX ERROR in migration: {e}")
        ok = False
else:
    print(f"MISSING: migration")
    ok = False

sys.exit(0 if ok else 1)