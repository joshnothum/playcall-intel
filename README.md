# Playcall-Intel

Contract-driven sports analytics pipeline that combines deterministic feature engineering with locally hosted LLM enrichment to produce reproducible, data-grounded NFL game reports.

---

## Quick Start

```bash
git clone https://github.com/joshnothum/playcall-intel
cd playcall-intel

python -m venv .venv
source .venv/bin/activate
pip install -e .

# start local model
ollama pull llama3.1:8b
ollama serve

# run the app
streamlit run src/playcall_intel/app.py
```

Open the local URL → select a game → generate a report.

---

## What the demo shows

- Select any NFL matchup from a structured game index
- Generate a full **data-grounded markdown game report**
- Deterministic box score and play counts
- WPA-based highlight extraction
- Local LLM recap built from validated structured data

No external APIs. Fully reproducible.

---

## Why this project exists

Most sports analytics workflows either:

- rely only on structured data, or
- use LLMs as unbounded text generators

This project demonstrates a third approach:

A **rules-first, contract-validated pipeline** where a local LLM performs
strictly controlled semantic enrichment on top of a deterministic baseline.

The model is a bounded component — not a source of truth.

---

## Core capabilities

- Stable, model-friendly **Play schema**
- Deterministic normalization from raw nflverse play-by-play
- Strict **Pydantic JSON contract** for all LLM output
- Batch processing with **reject capture**
- Local LLM provider via **Ollama**
- Interactive **Streamlit UI for game-level reports**
- Reproducible CLI pipeline for offline runs

---

## System architecture

```
nflverse play-by-play
        ↓
rules-first normalization (deterministic baseline)
        ↓
LLM enrichment from play_text (contract-bounded)
        ↓
schema validation
        ↓
normalized plays
        ↓
game aggregation
        ↓
markdown report + AI recap
```

---

## Design principles

- Deterministic first, AI second
- AI outputs are validated data — never free text
- Strict schema at system boundaries
- Model-agnostic LLM client (local or mock)
- Reproducible batch artifacts
- Raw data is never committed to Git

---

## Interactive UI

The Streamlit app provides:

- Team selector
- Opponent selector
- Game selector
- One-click report generation

The UI is powered by a precomputed **one-row-per-game index**, not ad-hoc filtering, ensuring fast and stable interaction.

---

## Batch normalization (CLI)

For pipeline demonstration and artifact generation:

```bash
LLM_PROVIDER=ollama python -m playcall_intel.batch_normalize
```

Outputs:

- `normalized_*.csv` → contract-validated plays
- `rejects_*.csv` → rows that failed validation

The batch run continues through bad rows and captures failures for inspection.

---

## Data

Expected raw data path:

```
data/raw/play_by_play_2025.csv.gz
```

Raw nflverse data is **not tracked by Git** and can be regenerated.

See `data/README.md` for taxonomy, field design, and normalization rules.

---

## Play text as a secondary data source

Structured nflverse columns provide:

- down
- distance
- yardline_100
- baseline play type
- yards gained

But they do not consistently capture:

- plain-language results
- player involvement
- contextual run/pass meaning
- penalty enforcement details
- edge cases with sparse flags

The pipeline treats:

- structured data → deterministic baseline
- `play_text` → LLM enrichment input

The model **adds meaning on top of the baseline — it never replaces it.**

---

## Result classification (rules-first)

Initial stable result labels:

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

This small, consistent taxonomy provides a reliable downstream signal across seasons.

---

## Tech stack

- Python
- pandas
- Pydantic
- Streamlit
- Ollama (local LLaMA 3.1 8B)

---

## Project scope

### Implemented

- Play schema and normalization pipeline
- Rules-first result classification
- Contract-validated LLM enrichment
- Batch runner with rejects
- WPA highlight extraction
- Data-grounded AI recap
- Game-level aggregation
- Streamlit interactive UI

### Deferred

- Caching layer for batch runs
- Expanded enrichment feature set
- Additional visualization views

---

## What this project demonstrates

- LLM integration inside a **strict data contract**
- Safe extraction of structure from inconsistent real-world text
- Separation of deterministic logic and AI responsibility
- Reproducible, local-first AI workflows
- End-to-end analytics system design — not a notebook

---

## Project status

Portfolio project — stable demo build.
