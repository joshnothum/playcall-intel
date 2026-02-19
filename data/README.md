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

- run- pass

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

## Play text as a secondary data source

In addition to structured nflverse fields, the pipeline carries the raw
play description (`desc`) as `play_text`.

### Why this exists

The structured columns are enough to build a stable, rules-first baseline
(down, distance, yardline_100, play_type, yards_gained), but they do not
capture the full meaning of the play.

The original narrative is the only place where certain football semantics
appear in a consistent, human-readable form.

### What the text enables that the flags do not

- The actual result of the play in plain terms
  (tackle, incomplete, interception, touchdown, sack, etc.)

- Player involvement
  (ball carrier, passer, receiver, tackler, interceptor)

- Run direction and pass context
  (left / middle / right, scramble vs designed run)

- Penalty details
  (type, enforcement, accepted/declined, “no play” reasons)

- Edge cases where structured fields are sparse or ambiguous

### Design approach

- Structured fields remain the deterministic baseline.
- `play_text` is the source input for any LLM-based enrichment.
- The model adds meaning on top of the baseline; it does not replace it.

## Result classification (first pass)

In addition to play_type, the pipeline assigns a simple `result` label as a
rules-first baseline. This is intentionally small and stable so downstream
logic can rely on it.

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

### Notes

- This is a first-pass label derived from nflverse structured outcome flags.
- It is not meant to capture every nuance (e.g., “pass defensed”, “lateral”, etc.).
- The LLM step can later refine or fill gaps when the narrative contains meaning
  the structured fields do not.

### Design notes

- This is a first-pass, rules-based normalization layer.
- The goal is a consistent, model-friendly play class that is stable across seasons.
- More detailed play concepts (e.g., screen, play action, RPO) are intentionally
  deferred to a later layer once the base pipeline is validated.
- LLM-based parsing will eventually map ambiguous or text-only cases into
  this same set of categories.
