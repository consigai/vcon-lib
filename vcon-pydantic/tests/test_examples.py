from vcon_pydantic import VconModel
import pytest
from conftest import (
    DEFAULT_UUID,
    DEFAULT_VCON_VERSION,
)


def test_all_ietf_examples(ietf_examples):
    """Test that all examples from the IETF draft can be parsed"""
    for example in ietf_examples:
        vcon = VconModel.model_validate(example)
        assert vcon.vcon is not None

        orig_vcon = vcon.to_vcon()
        vcon_dict = orig_vcon.to_dict()
        VconModel.model_validate(vcon_dict)


@pytest.fixture
def example_vcons():
    """Provide known vCon examples for testing"""
    return [
        {
            "uuid": DEFAULT_UUID,
            "vcon": DEFAULT_VCON_VERSION,
            "created_at": "2023-01-01T12:00:00Z",
            "subject": "Talkin' about the Sox game",
            "parties": [
                {
                    "tel": "+18005551212",
                    "role": "caller",
                    "name": "Murph from Dorchester",
                },
                {"tel": "+18005551213", "role": "agent", "name": "Sophia Florez"},
            ],
            "dialog": [
                {
                    "type": "voice",
                    "start": "2023-01-01T12:00:00Z",
                    "parties": [0, 1],
                    "mimetype": "audio/x-wav",
                    "url": "https://example.com/wicked_good_convo.wav",
                }
            ],
        }
    ]


@pytest.mark.parametrize(
    "example_name,expected_values",
    [
        (
            "basic_call",
            {
                "subject": "Talkin' about the Sox game",
                "party_count": 2,
                "dialog_count": 1,
            },
        ),
    ],
)
def matches_example(example: dict, name: str) -> bool:
    """Helper to identify specific examples from the draft"""
    if name == "basic_call":
        return (
            example.get("subject", "").lower().startswith("talkin'")
            and len(example.get("parties", [])) == 2
            and any(p.get("role") == "agent" for p in example.get("parties", []))
        )
    return False
