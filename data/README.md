# Data

This project uses nflverse play-by-play data.

## Raw data

The raw dataset is stored locally and is not tracked by Git.

Expected path:

data/raw/play_by_play_2025.csv.gz

## Source

https://github.com/nflverse/nflverse-data

Data can be regenerated/downloaded rather than versioned.

## Play type normalization

The pipeline maps nflverse play-by-play rows into a small, stable set of
play-type categories. These are derived from structured nflverse fields
(e.g., rush, pass, punt_attempt) before introducing any LLM-based parsing.

### Core offensive plays

- run
- pass

### QB clock / game-management plays

- qb_kneel
- qb_spike

### Special teams

- kickoff
- punt
- field_goal
- extra_point
- two_point_attempt

### Administrative / non-plays

- penalty
- no_play

### Fallback

- other

### Design notes

- This is a first-pass, rules-based normalization layer.
- The goal is a consistent, model-friendly play class that is stable across seasons.
- More detailed play concepts (e.g., screen, play action, RPO) are intentionally
  deferred to a later layer once the base pipeline is validated.
- LLM-based parsing will eventually map ambiguous or text-only cases into
  this same set of categories.

