from pytest_bdd import scenario

# Path is relative to this test file's location
@scenario('../../features/api/api.contracts.feature', 'OpenAPI exists and is valid after API changes')
def test_openapi_contract():
    """Runs the API contract feature scenarios."""
    pass
