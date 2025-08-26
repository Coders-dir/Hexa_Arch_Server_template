# Ensure step definitions are imported so pytest-bdd can match steps
import importlib.util
import os
this_dir = os.path.dirname(__file__)
steps_path = os.path.join(this_dir, 'steps', 'policy_steps.py')
spec = importlib.util.spec_from_file_location('policy_steps', steps_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from pytest_bdd import scenario

# Path is relative to this test file's location
@scenario('../../features/api/api.contracts.feature', 'OpenAPI exists and is valid after API changes')
def test_openapi_contract():
    """Runs the API contract feature scenarios."""
    pass
