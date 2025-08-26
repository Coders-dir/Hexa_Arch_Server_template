Feature: API contract ownership
  In order to protect API consumers
  As the API Owner
  The project must validate and require approvals for API contract changes

  Scenario: OpenAPI exists and is valid after API changes
    Given a PR modifies API controller files
    When OpenAPI generation is executed
    Then OpenAPI must be valid JSON
    And contract tests must pass
    And API Owner approval is required before merge
