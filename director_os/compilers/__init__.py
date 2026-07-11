"""Compiler layer — translates ProductionIntent into ExecutionPackage.

Architecture per ADR-002 (Compiler Isolation):

    Production Intent
        |
    ┌─────────────────┐
    │ Seedance Compiler│  (or Veo, Kling, Runway…)
    └─────────────────┘
        |
    Execution Package
        |
    AI Model (Seedance / Veo / …)
"""
