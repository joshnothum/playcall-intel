from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class GameIndexConfig:
    raw_path: Path = Path("data/raw/play_by_play_2025.csv.gz")
    max_games: Optional[int] = None  # leave None for full season


def pick_date_col(cols: list[str]) -> Optional[str]:
    """
    nflverse schemas can vary. Prefer a real date/datetime column if present.
    """
    candidates = [
        "game_date",
        "game_start_time",
        "game_datetime",
        "start_time",
    ]
    for c in candidates:
        if c in cols:
            return c
    return None


def load_games_index(cfg: GameIndexConfig = GameIndexConfig()) -> pd.DataFrame:
    """
    Returns a one-row-per-game index with:
      - game_id, home_team, away_team
      - date_label (best available)
      - match_label (for UI display: "<date> — AWAY @ HOME")
    """
    df = pd.read_csv(cfg.raw_path, compression="gzip", low_memory=False)

    required = {"game_id", "home_team", "away_team"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in pbp file: {sorted(missing)}")

    date_col = pick_date_col(list(df.columns))

    keep_cols = ["game_id", "home_team", "away_team"]

    # Optional context fields (used for fallback label)
    for c in ["season", "week", "season_type"]:
        if c in df.columns:
            keep_cols.append(c)

    if date_col:
        keep_cols.append(date_col)

    games = df[keep_cols].drop_duplicates(subset=["game_id"]).copy()

    # Build a friendly date label
    if date_col:
        games["date_label"] = games[date_col].astype(str)
    else:
        season = games["season"].astype(str) if "season" in games.columns else "?"
        week = games["week"].astype(str) if "week" in games.columns else "?"
        stype = games["season_type"].astype(str) if "season_type" in games.columns else ""
        stype_fmt = f" {stype}" if stype is not None else ""
        games["date_label"] = "Season " + season + " • Week " + week + stype_fmt

    games["match_label"] = games.apply(
        lambda r: f"{r['date_label']} — {r['away_team']} @ {r['home_team']}",
        axis=1,
    )

    # Optional: limit (useful if performance ever annoys you)
    if cfg.max_games is not None:
        games = games.head(cfg.max_games)

    # Sort for stable UI ordering
    games = games.sort_values(["date_label", "game_id"]).reset_index(drop=True)
    return games


def list_teams(games: pd.DataFrame) -> list[str]:
    return sorted(set(games["home_team"]).union(set(games["away_team"])))


def list_opponents(games: pd.DataFrame, team: str) -> list[str]:
    subset = games[(games["home_team"] == team) | (games["away_team"] == team)]
    opps = []
    for _, r in subset.iterrows():
        opps.append(r["away_team"] if r["home_team"] == team else r["home_team"])
    return sorted(set(opps))


def list_matchup_games(games: pd.DataFrame, team: str, opponent: str) -> pd.DataFrame:
    """
    Returns a filtered games DataFrame for the matchup, with match_label for dropdown display.
    """
    subset = games[
        ((games["home_team"] == team) & (games["away_team"] == opponent))
        | ((games["home_team"] == opponent) & (games["away_team"] == team))
    ].copy()

    return subset.sort_values(["date_label", "game_id"]).reset_index(drop=True)
