import csv
import gzip
from pathlib import Path
from typing import Iterator, Dict, Any


def iter_pbp_rows_gz(path: str | Path) -> Iterator[Dict[str, Any]]:
    """
    Stream rows from a gzipped play-by-play CSV

    - Keeps ingestion lightweight (no pandas dependency yet)
    - Lets me test the pipeline on real data without loading the full season
    - Provides the raw input shape the normalizer/LLM will standardize later
    """
    p = Path(path).expanduser()
    with gzip.open(p, mode="rt", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        yield from reader


def first_pbp_row_gz(path: str | Path) -> Dict[str, Any]:
    """
    Grab a single row for quick, repeatable smoke tests

    - Gives me a stable “one play” harness while plumbing evolves
    - Avoids false confidence from hand-made samples
    """
    return next(iter_pbp_rows_gz(path))
