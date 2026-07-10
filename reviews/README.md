# Director OS — Reviews

Reserved for review instances and review workflow.

## Review Modules

- narrative/
- visual/
- character/
- cinematography/
- consistency/
- technical/

## Architecture

Review provides the feedback loop:

```
Generation
    ↓
Review
    ↓
Human/System Validation
    ↓
Library / Engine Improvement
```

## Design Rules

- Review must reference intent (never evaluate generated output alone)
- Review does NOT become creative authority (it suggests, not decides)
- Review is independent from Compiler and Model implementations
- Review data can become knowledge (pattern discovery -> Library improvement)
