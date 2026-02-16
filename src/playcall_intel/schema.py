from dataclasses import dataclass
from typing import Optional


@dataclass
class Play:

    """
    Canonical structured representation of a single play

    - Defines the normalization target for all parsing paths
    - Uses yardline_100 (1–99) for side-independent field position
    - Prioritizes model- and query-friendly representations over display format
    """

    offense_team: str
    defense_team: str
    quarter: int
    down: int
    distance: int
    yardline_100: int
    play_type: str   # 1–99, distance from opponent end zone (side-independent; nflverse canonical field position)
    yards_gained: Optional[int] = None
    result: Optional[str] = None
