from typing import Optional, Literal

from pydantic import BaseModel, Field


PlayType = Literal[
    "run",
    "pass",
    "qb_kneel",
    "qb_spike",
    "kickoff",
    "punt",
    "field_goal",
    "extra_point",
    "two_point_attempt",
    "penalty",
    "no_play",
    "other",
]

ResultType = Literal[
    "tackle",
    "complete",
    "incomplete",
    "touchdown",
    "interception",
    "fumble",
    "sack",
    "out_of_bounds",
    "penalty",
    "no_play",
    "other",
]

RunDirection = Literal["left", "middle", "right", "unknown"]


class LLMNormalizationV1(BaseModel):
    """
    V1 structured output expected from the LLM

    - Keeps model output constrained to the same category sets as the rules-first pipeline
    - Gives us a strict validation gate before any AI output touches analytics
    - Makes prompt/model swaps safer because the contract stays stable
    """

    play_type: PlayType = Field(..., description="Normalized play type category")
    result: ResultType = Field(..., description="Normalized play result category")
    yards_gained: Optional[int] = Field(None, description="Yards gained (optional cross-check)")
    run_direction: RunDirection = Field("unknown", description="Run direction for run-like plays (left/middle/right). Use unknown if not a run or unclear.",
)


