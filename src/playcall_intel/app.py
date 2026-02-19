from __future__ import annotations

from pathlib import Path

import streamlit as st

from playcall_intel.game_index import (
    GameIndexConfig,
    list_matchup_games,
    list_opponents,
    list_teams,
    load_games_index,
)
from playcall_intel.game_report import write_game_report


def main() -> None:
    st.set_page_config(page_title="Playcall-Intel — Game Report", layout="wide")

    st.title("Playcall-Intel — Local Game Report")
    st.caption(
        "Pick a team, opponent, and game. Click generate to create a markdown report locally and view it here."
    )

    cfg = GameIndexConfig()
    if not cfg.raw_path.exists():
        st.error(
            "Raw data file not found.\n\n"
            f"Expected: `{cfg.raw_path}`\n\n"
            "Add the file locally, then refresh."
        )
        st.stop()

    with st.spinner("Loading game index..."):
        games = load_games_index(cfg)

    teams = list_teams(games)
    if not teams:
        st.error("No teams found in the game index.")
        st.stop()

    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

    with col1:
        team = st.selectbox("Team", teams, index=0)

    with col2:
        opps = list_opponents(games, team)
        if not opps:
            st.warning("No opponents found for selected team.")
            st.stop()
        opponent = st.selectbox("Opponent", opps, index=0)

    match_df = list_matchup_games(games, team, opponent)
    if match_df.empty:
        st.warning("No games found for that matchup.")
        st.stop()

    with col3:
        # Show friendly label, but we’ll use game_id underneath
        match_label = st.selectbox("Game", match_df["match_label"].tolist(), index=0)

    # Map selected label back to game_id
    selected = match_df[match_df["match_label"] == match_label].iloc[0]
    game_id = str(selected["game_id"])

    with col4:
        do_generate = st.button(
            "Generate game report",
            type="primary",
            use_container_width=True,
        )

    st.divider()

    if do_generate:
        with st.spinner("Generating report..."):
            out_path = write_game_report(game_id)

        if out_path is None:
            st.error("Report generation returned no path. Check `write_game_report()` return value.")
            st.stop()

        out_path = Path(out_path)
        if not out_path.exists():
            st.error(f"Expected report file not found: {out_path}")
            st.stop()

        md = out_path.read_text(encoding="utf-8")
        st.success(f"Generated: {out_path}")
        st.markdown(md)

    else:
        st.info("Pick a matchup and click **Generate game report**.")


if __name__ == "__main__":
    main()
