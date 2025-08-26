Feature: Lockfile consistency
  In order to keep builds reproducible
  As DevOps
  The project must ensure `poetry.lock` matches `pyproject.toml` changes

  Scenario: pyproject changed but lockfile not updated
    Given a PR changes `pyproject.toml`
    When CI lockfile-check runs
    Then the check must fail if `poetry.lock` was not regenerated
    And the PR should contain instructions to run `poetry lock`
