import os
import importlib.util

# Import step definitions so pytest-bdd can match steps (use absolute path)
here = os.path.dirname(__file__)
steps_path = os.path.join(here, 'steps', 'policy_steps.py')
spec = importlib.util.spec_from_file_location('policy_steps', steps_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from pytest_bdd import scenario

feature_path = os.path.join(here, '..', 'features', 'api', 'api.contracts.feature')

@scenario(feature_path, 'OpenAPI exists and is valid after API changes')
def test_openapi_contract():
    """Runs the API contract feature scenarios."""
    pass
