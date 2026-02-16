# Playcall-Intel — Build Log

## Entry 0 — Project Framing

### Problem
Raw football play descriptions are unstructured and not machine-queryable.

### Goal
Convert natural-language play text into a normalized, structured representation using an LLM-assisted pipeline.

### Why LLM
Rule-based parsing breaks on linguistic variability in play descriptions.
LLMs allow flexible semantic interpretation with consistent structured output.

### Initial Success Criteria
- Deterministic JSON output for a fixed set of sample plays
- Reproducible local environment
- Installable Python package (`pip install -e .`)

### Environment
- Python (project-local venv)
- src-layout package structure
- setuptools-based build via `pyproject.toml`

### Next Steps
- Config management via `.env`
- Define input/output schema
- First normalization prototype
