import pandas as pd
from pathlib import Path

from playcall_intel.mapper import row_to_play_first_pass, is_scrimmage_play
from playcall_intel.client_factory import get_llm_client
from playcall_intel.llm_normalize import normalize_with_llm_v1, apply_llm_enrichment


RAW_PATH = Path("data/raw/play_by_play_2025.csv.gz")
OUT_PATH = Path("data/processed/normalized_sample.csv")


def run_batch(sample_size: int = 25) -> None:
    df = pd.read_csv(RAW_PATH, compression="gzip", low_memory=False)

    df = df.head(sample_size)

    client = get_llm_client()

    rows = []

    for _, row in df.iterrows():

        if not is_scrimmage_play(row):
            continue

        base_play = row_to_play_first_pass(row)

        llm_out = normalize_with_llm_v1(base_play, client)
        enriched = apply_llm_enrichment(base_play, llm_out)

        rows.append({
            "posteam": enriched.offense_team,
            "defteam": enriched.defense_team,
            "down": enriched.down,
            "distance": enriched.distance,
            "yardline_100": enriched.yardline_100,
            "play_type": enriched.play_type,
            "result": enriched.result,
            "yards_gained": enriched.yards_gained,
            "play_text": enriched.play_text,
        })

    out_df = pd.DataFrame(rows)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUT_PATH, index=False)

    print(f"Wrote {len(out_df)} rows → {OUT_PATH}")


if __name__ == "__main__":
    run_batch()
