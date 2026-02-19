# Playcall-Intel

Contract-driven pipeline that converts raw nflverse play-by-play into
validated, analytics-ready football features using a rules-first baseline
and a local LLM for text enrichment.

---

## What this project does

- Builds a **stable, model-friendly Play schema**
- Maps messy nflverse rows into a **deterministic baseline**
- Uses a **local LLaMA model (Ollama)** only where text adds new meaning
- Enforces a **strict JSON contract (Pydantic-validated)**
- Produces a reproducible processed dataset slice for inspection

The LLM is used as a **bounded enrichment step**, not as a source of truth.

---

## Pipeline overview

nflverse pbp CSV
↓
rules-first mapper (deterministic baseline)
↓
LLM normalization (play_text → structured labels)
↓
contract validation
↓
enriched Play objects
↓
processed sample + rejects file

Batch runs:

- continue through bad rows
- capture failures for later inspection

---

## One-command demo

LLM_PROVIDER=ollama python -m playcall_intel.batch_normalize

---

## Quickstart

### 1) Create environment

python -m venv .venv
source .venv/bin/activate
pip install -e .

### 2) Install and start Ollama

ollama pull llama3.1:8b
ollama serve

### 3) Add the raw data

Expected path:
data/raw/play_by_play_2025.csv.gz

### 4) Run the demo batch

---

## Output

- **normalized_sample.csv** → contract-validated enriched plays
- **rejects_sample.csv** → rows that failed validation

Raw data is **not tracked by Git** and can be regenerated.

---



## Result classification (first pass)

A simple, rules-first `result` label provides a stable downstream signal.

### v1 result categories

- tackle
- complete
- incomplete
- touchdown
- interception
- fumble
- sack
- out_of_bounds
- penalty
- no_play
- other

This is intentionally small and consistent across seasons.

---

## Play text as a secondary data source

In addition to structured nflverse fields, the pipeline carries the raw
play description (`desc`) as `play_text`.

### Why this exists

Structured columns are enough for:

- down
- distance
- yardline_100
- baseline play_type
- yards_gained

…but they do **not** capture the full football meaning of the play.

The narrative is the only consistently human-readable source for:

- plain-language result (tackle, interception, touchdown, etc.)
- player involvement
- run direction / pass context
- penalty enforcement details
- edge cases where flags are sparse or ambiguous

### Design approach

- Structured data = deterministic baseline
- `play_text` = input for LLM enrichment
- The model **adds meaning on top of the baseline — it never replaces it**

---

## Design principles

- Deterministic first, AI second
- AI outputs are data, not text
- Strict schema at system boundaries
- Model-agnostic client (local or mock)
- Reproducible batch artifact for demos

---

## Current scope

Implemented:

- Play schema
- Rules-first mapper
- LLM contract + prompt
- Local Ollama client
- Batch normalization runner
- Rejects capture

Deferred:

- caching
- expanded enrichment feature set
- visualization layer
- game-level reporting

---

## Summary

This project shows how to use an LLM to:

- extract structure from inconsistent real-world text
- operate inside a strict validation contract
- behave as a controlled component in a data pipeline

—not as a text generator.

---

## Status

Demo-ready.
