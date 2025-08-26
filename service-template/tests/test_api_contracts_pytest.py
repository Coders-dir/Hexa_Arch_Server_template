import os
import subprocess
import json


def test_openapi_generation_and_contract_check():
    # Mark PR-modified controllers (for scripts that might read this env)
    os.environ['PR_MODIFIES_API_CONTROLLERS'] = '1'

    # Generate OpenAPI
    res = subprocess.run(['python3', 'service-template/tools/generate_openapi.py'], capture_output=True, text=True)
    assert res.returncode == 0, f"generate_openapi failed: {res.stdout}\n{res.stderr}"

    # Validate OpenAPI JSON
    path = 'service-template/src/app/openapi.json'
    assert os.path.exists(path), 'OpenAPI file not generated'
    with open(path, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    assert isinstance(data, dict)

    # Run contract check
    res2 = subprocess.run(['python3', 'monolith-template/tools/contract_check.py'], capture_output=True, text=True)
    if res2.returncode != 0:
        print(res2.stdout)
        print(res2.stderr)
    assert res2.returncode == 0

    # Soft-check for CODEOWNERS (log but don't fail locally)
    if not (os.path.exists('CODEOWNERS') or os.path.exists('.github/CODEOWNERS')):
        print('NOTE: No CODEOWNERS file; ensure API owner approval is enforced in CI')
