#!/usr/bin/env python3
"""Simple architecture check: ensure imports follow the intended layering.

This script implements a conservative heuristic: it scans Python files under `src/`
and fails if files under `adapters/` import from `services/` or `domain/` in the wrong direction.
It's intentionally small and easy to extend; for real projects consider import-linter.
"""
import sys
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
#!/usr/bin/env python3
"""AST-based architecture check: ensure imports follow the intended layering.

Layers (outer -> inner): adapters, ports, services/usecases, domain

Rule: a file may import modules in the same layer or more-inner layers
(e.g., adapters can import usecases and domain), but must not import modules
from a more-outer layer (e.g., domain must not import adapters).

This script scans Python files under `src/` and uses AST to find imports. It
attempts to resolve import module names heuristically against project paths.
"""
import sys
from pathlib import Path
import ast
from typing import Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

# Layer order: lower index = more central (inner)
LAYER_ORDER = ["domain", "ports", "usecases", "services", "adapters"]
LAYER_INDEX = {name: idx for idx, name in enumerate(LAYER_ORDER)}


def find_python_files(root: Path):
    for p in root.rglob("*.py"):
        yield p


def detect_layer_from_path(path: Path) -> Optional[str]:
    """Detect layer keyword from path parts under src/app."""
    try:
        rel = path.relative_to(SRC / "app")
    except Exception:
        return None
    parts = rel.parts
    for part in parts:
        if part in LAYER_INDEX:
            return part
    return None


def imported_module_layer(name: str) -> Optional[str]:
    """Heuristic: map an imported module name to a known layer if it contains the layer keyword."""
    if not name:
        return None
    for layer in LAYER_INDEX:
        if f".{layer}." in name or name.endswith(f".{layer}") or name.startswith(f"{layer}.") or f"/{layer}/" in name:
            return layer
    return None


def extract_imports(path: Path):
    src = path.read_text(errors="ignore")
    try:
        tree = ast.parse(src)
    except Exception:
        return []
    mods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                mods.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module
            if mod:
                mods.append(mod)
            else:
                # relative import: attempt to resolve to package path
                # we won't fully resolve; leave as None
                mods.append(None)
    return mods


def main():
    violations = []
    for f in find_python_files(SRC / "app"):
        cur_layer = detect_layer_from_path(f)
        if cur_layer is None:
            # ignore files not in recognized layers
            continue
        cur_idx = LAYER_INDEX[cur_layer]
        imports = extract_imports(f)
        for mod in imports:
            if mod is None:
                continue
            imp_layer = imported_module_layer(mod)
            if imp_layer is None:
                continue
            imp_idx = LAYER_INDEX[imp_layer]
            # violation if imported layer is more outer (higher index) than current
            if imp_idx > cur_idx:
                violations.append((f, cur_layer, mod, imp_layer))

    if violations:
        print("Architecture import-direction violations detected:")
        for f, cur_layer, mod, imp_layer in violations:
            print(f" - {f.relative_to(ROOT)} (layer={cur_layer}) imports {mod} (layer={imp_layer})")
        print("")
        print("To accept an exception: create an ADR and add a TODO comment referencing the ADR file path.")
        return 2

    print("No architecture import violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
