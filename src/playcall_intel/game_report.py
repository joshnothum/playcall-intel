from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from playcall_intel.client_factory import get_llm_client
from playcall_intel.recap_generate import generate_game_recap_v1
import pandas as pd


RAW_PATH = Path("data/raw/play_by_play_2025.csv.gz")
OUT_DIR = Path("reports/games")


@dataclass(frozen=True)
class BoxScore:
    game_id: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int

    # team-level quick stats
    home_off_plays: int
    home_total_yards: int
    away_off_plays: int
    away_total_yards: int
    home_pass: int
    home_run: int
    away_pass: int
    away_run: int

    # optional “nice to have”
    home_turnovers: int
    away_turnovers: int
    home_sacks: int
    away_sacks: int


def _first_existing_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _safe_int(x) -> int:
    try:
        if pd.isna(x):
            return 0
        return int(x)
    except Exception:
        return 0


def load_game_df(game_id: str) -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH, compression="gzip", low_memory=False)
    g = df[df["game_id"] == game_id].copy()
    if g.empty:
        raise ValueError(f"game_id not found: {game_id}")
    # chronological order
    if "play_id" in g.columns:
        g = g.sort_values("play_id")
    return g


def compute_box_score(game_id: str) -> BoxScore:
    g = load_game_df(game_id)

    # Teams
    home_team = str(g["home_team"].dropna().iloc[0])
    away_team = str(g["away_team"].dropna().iloc[0])

    # Final score: nflverse commonly provides one of these columns
    home_score_col = _first_existing_col(g, ["total_home_score", "home_score"])
    away_score_col = _first_existing_col(g, ["total_away_score", "away_score"])

    if not home_score_col or not away_score_col:
        # Fallback: try last non-null posteam/defteam score columns (less ideal)
        raise ValueError(
            "Could not find final score columns (expected total_home_score/total_away_score or home_score/away_score)."
        )

    last_scored = g[[home_score_col, away_score_col]].dropna().tail(1)
    if last_scored.empty:
        # if still empty, treat as 0-0 (rare edge)
        home_score, away_score = 0, 0
    else:
        home_score = _safe_int(last_scored.iloc[0][home_score_col])
        away_score = _safe_int(last_scored.iloc[0][away_score_col])

    # “Offensive plays” proxy: rows where posteam exists (filters out many administrative rows)
    off = g[g["posteam"].notna()].copy()

    # Pass/run counts (nflverse has pass=1 and rush=1 flags in most pbp files)
    pass_col = _first_existing_col(off, ["pass"])
    rush_col = _first_existing_col(off, ["rush"])

    def team_counts(team: str) -> tuple[int, int, int]:
        t = off[off["posteam"] == team]
        plays = len(t)
        p = int(t[pass_col].fillna(0).sum()) if pass_col else 0
        r = int(t[rush_col].fillna(0).sum()) if rush_col else 0
        return plays, p, r

    home_plays, home_pass, home_run = team_counts(home_team)
    away_plays, away_pass, away_run = team_counts(away_team)

    # turnovers + sacks (optional columns vary)
    inter_col = _first_existing_col(off, ["interception"])
    fumble_lost_col = _first_existing_col(off, ["fumble_lost"])
    sack_col = _first_existing_col(off, ["sack"])

    def team_misc(team: str) -> tuple[int, int]:
        t = off[off["posteam"] == team]
        ints = int(t[inter_col].fillna(0).sum()) if inter_col else 0
        fum = int(t[fumble_lost_col].fillna(0).sum()) if fumble_lost_col else 0
        to = ints + fum
        sacks = int(t[sack_col].fillna(0).sum()) if sack_col else 0
        return to, sacks

    home_to, home_sacks = team_misc(home_team)
    away_to, away_sacks = team_misc(away_team)

    def team_total_yards(team: str) -> int:
        t = off[off["posteam"] == team]
        if "yards_gained" not in t.columns:
            return 0
        return int(t["yards_gained"].fillna(0).sum())

    home_total_yards = team_total_yards(home_team)
    away_total_yards = team_total_yards(away_team)


    return BoxScore(
        game_id=game_id,
        home_team=home_team,
        away_team=away_team,
        home_score=home_score,
        away_score=away_score,
        home_off_plays=home_plays,
        away_off_plays=away_plays,
        home_pass=home_pass,
        home_run=home_run,
        away_pass=away_pass,
        away_run=away_run,
        home_turnovers=home_to,
        away_turnovers=away_to,
        home_sacks=home_sacks,
        away_sacks=away_sacks,
        home_total_yards=home_total_yards,
        away_total_yards=away_total_yards,

    )


def make_brief_summary(bs: BoxScore) -> str:
    # Winner
    if bs.home_score > bs.away_score:
        winner, loser = bs.home_team, bs.away_team
        w, l = bs.home_score, bs.away_score
    elif bs.away_score > bs.home_score:
        winner, loser = bs.away_team, bs.home_team
        w, l = bs.away_score, bs.home_score
    else:
        winner, loser = "Neither team", "the other"
        w, l = bs.home_score, bs.away_score

    # Tendencies
    home_style = "pass-heavy" if bs.home_pass > bs.home_run else "run-heavy"
    away_style = "pass-heavy" if bs.away_pass > bs.away_run else "run-heavy"

    lines = []
    lines.append(f"{winner} took this one {w}–{l} in game **{bs.game_id}**.")
    lines.append(
        f"{bs.home_team} ran {bs.home_off_plays} offensive plays ({home_style}), while "
        f"{bs.away_team} ran {bs.away_off_plays} ({away_style})."
    )
    lines.append(
        f"Turnovers: {bs.away_team} {bs.away_turnovers}, {bs.home_team} {bs.home_turnovers}. "
        f"Sacks: {bs.away_team} {bs.away_sacks}, {bs.home_team} {bs.home_sacks}."
    )
    return " ".join(lines)

def top_wpa_plays_by_team(g: pd.DataFrame, team: str, n: int = 3) -> list[tuple[float, str]]:
    """
    Returns [(wpa, desc), ...] for the top N WPA plays credited to `posteam`.
    Uses raw WPA (positive swing for that team’s offense).
    """
    if not {"wpa", "posteam", "desc"}.issubset(g.columns):
        return []

    t = g[(g["posteam"] == team)].dropna(subset=["wpa", "desc"]).copy()
    if t.empty:
        return []

    top = t.sort_values("wpa", ascending=False).head(n)
    return [(float(r["wpa"]), str(r["desc"])) for _, r in top.iterrows()]

def _fmt_wpa_list(items: list[tuple[float, str]]) -> str:
    if not items:
        return "_No WPA highlights available._"
    return "\n".join([f"- **{wpa:+.3f} WPA** — {desc}" for wpa, desc in items])


def write_game_report(game_id: str) -> Path:
    # Load the full game play stream (for highlights) and compute the box score (source of truth)
    g = load_game_df(game_id)
    bs = compute_box_score(game_id)

    # Top WPA plays per team (offense)
    away_top_wpa = top_wpa_plays_by_team(g, bs.away_team, n=3)
    home_top_wpa = top_wpa_plays_by_team(g, bs.home_team, n=3)

    away_wpa_md = _fmt_wpa_list(away_top_wpa)
    home_wpa_md = _fmt_wpa_list(home_top_wpa)

    # High-signal highlights for the LLM recap (top |WPA| swings)
    highlights: list[str] = []
    if {"wpa", "desc"}.issubset(g.columns):
        highlights = (
            g.dropna(subset=["wpa", "desc"])
            .assign(abs_wpa=lambda x: x["wpa"].abs())
            .sort_values("abs_wpa", ascending=False)
            .head(10)["desc"]
            .astype(str)
            .tolist()
        )

    # Default recap (rules-only) in case the LLM call fails
    recap_text = make_brief_summary(bs)

    # Try LLM recap (2 paragraphs) using ONLY stats + highlights
    try:
        client = get_llm_client()
        recap = generate_game_recap_v1(bs, highlights, client)
        recap_text = f"{recap.paragraph_1}\n\n{recap.paragraph_2}"
    except Exception:
        # Keep the report reliable — never fail the whole report for narrative generation
        pass

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{game_id}.md"

    md = f"""# Game Report: {bs.away_team} @ {bs.home_team}

## Final
**{bs.away_team} {bs.away_score} — {bs.home_team} {bs.home_score}**

## Brief recap
{recap_text}

## Box score
| Team | Score | Off plays | Pass | Run | Total yards | Turnovers | Sacks |
|---|---:|---:|---:|---:|---:|---:|---:|
| {bs.away_team} | {bs.away_score} | {bs.away_off_plays} | {bs.away_pass} | {bs.away_run} | {bs.away_total_yards} | {bs.away_turnovers} | {bs.away_sacks} |
| {bs.home_team} | {bs.home_score} | {bs.home_off_plays} | {bs.home_pass} | {bs.home_run} | {bs.home_total_yards} | {bs.home_turnovers} | {bs.home_sacks} |

## Top WPA plays (offense)

### {bs.away_team} — top 3
{away_wpa_md}

### {bs.home_team} — top 3
{home_wpa_md}
"""
    out_path.write_text(md, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    # Convenient default for quick manual runs:
    # python -m playcall_intel.game_report  (after setting GAME_ID env var)
    import os

    gid = os.getenv("GAME_ID")
    if not gid:
        raise SystemExit("Set GAME_ID, e.g. GAME_ID=2025_01_ARI_NO python -m playcall_intel.game_report")

    p = write_game_report(gid)
    print(f"Wrote {p}")
