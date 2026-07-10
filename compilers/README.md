# Director OS — Compilers

## Contract

| File                  | Version | Status   |
|-----------------------|---------|----------|
| COMPILER_CONTRACT.md  | 1.0     | Accepted |

## Platform Compilers

| Compiler  | Status     |
|-----------|------------|
| Seedance  | Planned    |
| Veo       | Planned    |
| Kling     | Planned    |
| Runway    | Planned    |

## Architecture

```
Production Intent
        |
        v
Compiler Layer  ──►  COMPILER_CONTRACT.md
        |
        v
Execution Package
        |
        v
AI Model
```

## Design Rules

- Compiler cannot modify creative intent
- Compiler must be replaceable (new platform = new compiler)
- Compiler knowledge is platform knowledge only
- Compiler should be deterministic
