import os
import pytest
import socket

from playcall_intel.client_factory import get_llm_client
from playcall_intel.llm_normalize import normalize_with_llm_v1
from playcall_intel.schema import Play

def _ollama_up(host: str = "localhost", port: int = 11434) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(
    os.getenv("LLM_PROVIDER") != "ollama" or not _ollama_up(),
    reason="Ollama integration test requires LLM_PROVIDER=ollama and a running Ollama server on localhost:11434.",
)
def test_ollama_local_llama_contract_valid_output():
    client = get_llm_client()

    play = Play(
        offense_team="ARI",
        defense_team="NO",
        quarter=1,
        down=1,
        distance=10,
        yardline_100=78,
        play_type="run",
        play_text="(14:56) 6-J.Conner right tackle to ARI 25 for 3 yards (92-D.Godchaux).",
        yards_gained=3,
        result="tackle",
    )

    out = normalize_with_llm_v1(play, client)

    # If this returns, it passed contract validation (Pydantic would have thrown otherwise)
    assert out.play_type in {
        "run", "pass", "qb_kneel", "qb_spike", "kickoff", "punt",
        "field_goal", "extra_point", "two_point_attempt", "penalty",
        "no_play", "other",
    }
    assert out.result in {
        "tackle", "complete", "incomplete", "touchdown", "interception",
        "fumble", "sack", "out_of_bounds", "penalty", "no_play", "other",
    }
