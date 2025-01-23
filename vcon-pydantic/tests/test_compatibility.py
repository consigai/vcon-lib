from datetime import datetime, timezone
from vcon.vcon import Vcon
from vcon.party import Party, PartyHistory
from vcon.dialog import Dialog
from vcon_pydantic import VconModel, PartyModel, DialogModel, PartyHistoryModel
import pytest
from conftest import (
    DEFAULT_UUID,
    DEFAULT_VCON_VERSION,
)


def test_vcon_compatibility():
    """Test compatibility between original Vcon and Pydantic VconModel"""
    now = datetime.now(timezone.utc)

    original_vcon = Vcon(
        {
            "uuid": DEFAULT_UUID,
            "vcon": DEFAULT_VCON_VERSION,
            "subject": "Test Compatibility",
            "created_at": now.isoformat(),
            "parties": [],
            "dialog": [],
        }
    )
    original_party = Party(tel="+1234567890", name="Sophia Florez", role="caller")
    original_vcon.add_party(original_party)

    original_dialog = Dialog(
        type="text",
        start=now,
        parties=[0],
        mimetype="text/plain",
        body="Headin' to Dunks, need anythin'?",
        party_history=[PartyHistory(0, "join", now)],
    )
    original_vcon.add_dialog(original_dialog)

    pydantic_vcon = VconModel(
        uuid=original_vcon.uuid,
        vcon="0.0.1",
        created_at=now,
        subject="Test Compatibility",
        parties=[PartyModel(tel="+1234567890", name="Sophia Florez", role="caller")],
        dialog=[
            DialogModel(
                type="text",
                start=now,
                parties=[0],
                mimetype="text/plain",
                body="Headin' to Dunks, need anythin'?",
                party_history=[PartyHistoryModel(party=0, event="join", time=now)],
            )
        ],
    )

    converted_vcon = pydantic_vcon.to_vcon()

    assert original_vcon.subject == converted_vcon.subject
    assert original_vcon.uuid == converted_vcon.uuid
    assert original_vcon.vcon == converted_vcon.vcon
    assert len(original_vcon.parties) == len(converted_vcon.parties)
    assert len(original_vcon.dialog) == len(converted_vcon.dialog)

    orig_party = original_vcon.parties[0]
    conv_party = converted_vcon.parties[0]
    assert orig_party.tel == conv_party.tel
    assert orig_party.name == conv_party.name
    assert orig_party.role == conv_party.role

    orig_dialog = original_vcon.dialog[0]
    conv_dialog = converted_vcon.dialog[0]
    assert orig_dialog["type"] == conv_dialog["type"]
    assert orig_dialog["mimetype"] == conv_dialog["mimetype"]
    assert orig_dialog["body"] == conv_dialog["body"]
    assert orig_dialog["parties"] == conv_dialog["parties"]

    assert len(orig_dialog["party_history"]) == len(conv_dialog["party_history"])
    orig_ph = orig_dialog["party_history"][0]
    conv_ph = conv_dialog["party_history"][0]
    assert orig_ph["party"] == conv_ph["party"]
    assert orig_ph["event"] == conv_ph["event"]


def compare_vcon_dicts(original: dict, converted: dict):
    """Helper to compare vCon dictionaries accounting for differences"""
    orig = original.copy()
    conv = converted.copy()

    if "created_at" in orig and "created_at" in conv:
        orig_dt = datetime.fromisoformat(orig["created_at"])
        conv_dt = datetime.fromisoformat(conv["created_at"])
        assert abs((orig_dt - conv_dt).total_seconds()) < 1
        del orig["created_at"]
        del conv["created_at"]

    for key in list(orig.keys()):
        if isinstance(orig[key], (list, dict)) and not orig[key]:
            del orig[key]

    for key in list(conv.keys()):
        if isinstance(conv[key], (list, dict)) and not conv[key]:
            del conv[key]

    assert orig == conv


def test_roundtrip_conversion():
    """Test round-trip conversion between original and Pydantic models"""
    original = Vcon(
        {
            "uuid": "01234567-89ab-cdef-0123-456789abcdef",
            "vcon": "0.0.1",
            "subject": "Round Trip Test",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "parties": [],
            "dialog": [],
        }
    )

    pydantic = VconModel.model_validate(original.to_dict())
    assert pydantic.subject == original.subject

    roundtrip = pydantic.to_vcon()

    compare_vcon_dicts(original.to_dict(), roundtrip.to_dict())


def test_complex_vcon_compatibility():
    """Test compatibility with more complex vCon structures"""
    now = datetime.now(timezone.utc)

    original = Vcon(
        {
            "uuid": "01234567-89ab-cdef-0123-456789abcdef",
            "vcon": "0.0.1",
            "subject": "Complex Test",
            "created_at": now.isoformat(),
            "parties": [],
            "dialog": [],
        }
    )

    original.add_party(Party(tel="+1111", name="Alice", role="caller"))
    original.add_party(Party(tel="+2222", name="Bob", role="agent"))

    original.add_dialog(
        Dialog(
            type="text", start=now, parties=[0, 1], mimetype="text/plain", body="Hello"
        )
    )
    original.add_dialog(
        Dialog(
            type="audio",
            start=now,
            parties=[0, 1],
            mimetype="audio/x-wav",
            url="https://example.com/audio.wav",
        )
    )

    pydantic = VconModel.model_validate(original.to_dict())
    converted = pydantic.to_vcon()

    compare_vcon_dicts(original.to_dict(), converted.to_dict())


def test_none_handling_compatibility():
    """Test that None values are properly excluded in both implementations"""
    now = datetime.now(timezone.utc)

    original = Vcon(
        {
            "uuid": "01234567-89ab-cdef-0123-456789abcdef",
            "vcon": "0.0.1",
            "created_at": now.isoformat(),
            "parties": [],
            "dialog": [],
        }
    )

    original.add_party(
        Party(
            tel="+1111",
            role="caller",  # omit name and other stuffs to check None handlings
        )
    )

    original.add_dialog(
        Dialog(
            type="text",
            start=now,
            parties=[0],
            body="Hello",  # omit optionals - good for testing None stuffs
        )
    )

    pydantic = VconModel.model_validate(original.to_dict())
    converted = pydantic.to_vcon()

    compare_vcon_dicts(original.to_dict(), converted.to_dict())


def test_edge_cases():
    """Test edge cases and potential error conditions"""
    now = datetime.now(timezone.utc)

    original = Vcon(
        {
            "uuid": "01234567-89ab-cdef-0123-456789abcdef",
            "vcon": "0.0.1",
            "created_at": now.isoformat(),
            "dialog": [],
            "parties": [],
        }
    )

    pydantic = VconModel.model_validate(original.to_dict())
    converted = pydantic.to_vcon()

    compare_vcon_dicts(original.to_dict(), converted.to_dict())

    # w/ nested None vals
    original = Vcon(
        {
            "uuid": "01234567-89ab-cdef-0123-456789abcdef",
            "vcon": "0.0.1",
            "created_at": now.isoformat(),
            "parties": [{"tel": "+1111", "role": "test"}],
            "dialog": [],
        }
    )

    # with nested meta containing None vals
    original.add_dialog(
        Dialog(
            type="text",
            start=now,
            parties=[0],  # valid now that we have a party
            meta={
                "key2": "",  # empties gotta stay empty, yo
                "key3": {
                    "nested2": ""  # empties gotta stay empty, yo
                },
            },
        )
    )

    pydantic = VconModel.model_validate(original.to_dict())
    converted = pydantic.to_vcon()

    compare_vcon_dicts(original.to_dict(), converted.to_dict())


def test_error_conditions():
    """Test error handling and validation"""
    now = datetime.now(timezone.utc)

    # invalid MIME type
    with pytest.raises(ValueError, match="Invalid MIME type"):
        DialogModel(type="text", start=now, parties=[0], mimetype="invalid/type")

    # invalid encoding
    with pytest.raises(ValueError, match="Invalid encoding"):
        DialogModel(type="text", start=now, parties=[0], encoding="invalid")

    # invalid party index at VconModel level
    with pytest.raises(ValueError, match="Invalid party index"):
        VconModel(
            uuid="01234567-89ab-cdef-0123-456789abcdef",
            vcon="0.0.1",
            created_at=now,
            parties=[],
            dialog=[
                DialogModel(
                    type="text",
                    start=now,
                    parties=[0],  # this should yield a nope
                    body="test",
                )
            ],
        )
