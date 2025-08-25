Feature: Architectural dependency direction
  In order to avoid spaghetti coupling
  As the Architect role
  The repository must enforce that outer layers do not import inner layers

  Scenario: No adapter imports into domain or usecase layers
    Given the repository Python files
    When the architecture enforcement check is executed
    Then zero import violations must be reported
    And any accepted exception requires an ADR and Architect approval
