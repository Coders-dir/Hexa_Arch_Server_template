#!/usr/bin/env python3
"""Simple validator for role requirement YAML files.

Checks that each YAML file under service-template/roles/ contains required fields.
"""
import glob
import yaml
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROLES_DIR = ROOT / 'service-template' / 'roles'

required = ['id', 'title', 'owner', 'risk_level', 'sensitive_flags', 'acceptance_gherkin']


def validate_file(path: Path):
    try:
        data = yaml.safe_load(path.read_text())
    except Exception as e:
        print(f"ERROR reading {path}: {e}")
        return False
    ok = True
    for k in required:
        if k not in data:
            print(f"{path}: missing required field '{k}'")
            ok = False
    return ok


def main():
    files = glob.glob(str(ROLES_DIR / '*.yaml'))
    if not files:
        print('No role YAML files found under', ROLES_DIR)
        sys.exit(1)
    all_ok = True
    for f in files:
        p = Path(f)
        ok = validate_file(p)
        all_ok = all_ok and ok
    if not all_ok:
        print('Requirement validation failed')
        sys.exit(2)
    print('All requirement YAML files validated')


if __name__ == '__main__':
    main()
