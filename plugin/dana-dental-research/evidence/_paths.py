"""
evidence/_paths.py

Shared import bootstrap for the v1.2 evidence-intelligence layer.

The plugin ships as plain directories (no installable package, no __init__.py), matching the
existing `clinical/` and `connectors/` layout. Each evidence module therefore imports this first
so that `shared.*` (the connector-layer helpers) and its sibling evidence modules resolve
identically whether a module is run as a script, imported by a test, or invoked through the
Bash tool by a skill.

No network. No side effects other than sys.path.
"""
import os
import sys

EVIDENCE_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(EVIDENCE_DIR)
CONNECTORS_DIR = os.path.join(PLUGIN_ROOT, "connectors")

for _p in (EVIDENCE_DIR, CONNECTORS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)
