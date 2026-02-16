from playcall_intel.llm_client import MockLLMClient
from playcall_intel.llm_normalize import normalize_with_llm_v1
from playcall_intel.schema import Play


def test_llm_normalize_v1_mock_happy_path():
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

    client = MockLLMClient(fixed_play_type="run", fixed_result="tackle", fixed_yards_gained=3)
    out = normalize_with_llm_v1(play, client)

    assert out.play_type == "run"
    assert out.result == "tackle"
    assert out.yards_gained == 3
