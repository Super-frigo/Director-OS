# Migration Note

**compilers/seedance/compile.py** and **compilers/seedance/rules.py** have been merged into the canonical implementation:

- Enum-to-Seedance translation tables ➜ [director_os/compilers/seedance/mapper.py](/G:/Director%20OS/director_os/compilers/seedance/mapper.py)
- 4-stage compilation pipeline (project_reader → context_builder → platform_adapter → prompt_assembler) ➜ [director_os/compilers/seedance/compiler.py](/G:/Director%20OS/director_os/compilers/seedance/compiler.py)
- Deterministic tests ➜ [tests/test_seedance_mapper_coverage.py](/G:/Director%20OS/tests/test_seedance_mapper_coverage.py)

For project schema validation, use [schemas/project_schema.py](/G:/Director%20OS/schemas/project_schema.py).

The `director_os/` package is the single long-term implementation.  Do not add new code under `compilers/seedance/`.
