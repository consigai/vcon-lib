from datetime import datetime, timezone
from vcon_pydantic import (
    VconModel,
    PartyModel,
    DialogModel,
    CivicAddressModel,
    PartyHistoryModel,
)
import pytest
from conftest import (
    DEFAULT_UUID,
    DEFAULT_VCON_VERSION,
)


def test_civic_address_model():
    """Test CivicAddressModel creation and conversion"""
    address_data = {
        "country": "US",
        "a1": "California",
        "a3": "San Francisco",
        "sts": "Market Street",
        "hno": "123",
        "pc": "94105",
    }

    address = CivicAddressModel(**address_data)
    assert address.country == "US"
    assert address.a1 == "California"

    orig_address = address.to_civic_address()
    assert orig_address.country == "US"
    assert orig_address.a1 == "California"


def test_party_model():
    """Test PartyModel creation and conversion"""
    party_data = {
        "tel": "+1234567890",
        "name": "Sophia Florez",
        "role": "caller",
        "civicaddress": {"country": "US", "a1": "California"},
    }

    party = PartyModel(**party_data)
    assert party.tel == "+1234567890"
    assert party.name == "Sophia Florez"
    assert isinstance(party.civicaddress, CivicAddressModel)

    orig_party = party.to_party()
    assert orig_party.tel == "+1234567890"
    assert orig_party.name == "Sophia Florez"


def test_party_history_model():
    """Test PartyHistoryModel creation and conversion"""
    history_data = {"party": 1, "event": "join", "time": datetime.now(timezone.utc)}

    history = PartyHistoryModel(**history_data)
    assert history.party == 1
    assert history.event == "join"

    orig_history = history.to_party_history()
    assert orig_history.party == 1
    assert orig_history.event == "join"


def test_dialog_model():
    """Test DialogModel creation and validation"""
    now = datetime.now(timezone.utc)
    dialog_data = {
        "type": "text",
        "start": now,
        "parties": [0],
        "mimetype": "text/plain",
        "body": "Wicked smaht meetin' today at Strolid Headquarters",
        "party_history": [{"party": 0, "event": "join", "time": now}],
    }

    dialog = DialogModel(**dialog_data)
    assert dialog.type == "text"
    assert dialog.parties == [0]
    assert dialog.is_text() is True


def test_vcon_model():
    """Test VconModel creation and conversion"""
    vcon = VconModel.build_new()
    assert vcon.vcon == "0.0.1"
    assert vcon.uuid is not None

    vcon_data = {
        "uuid": vcon.uuid,
        "vcon": "0.0.1",
        "created_at": datetime.now(timezone.utc),
        "subject": "Test vCon",
        "parties": [{"tel": "+1234567890", "name": "Sophia Florez", "role": "caller"}],
        "dialog": [
            {
                "type": "text",
                "start": datetime.now(timezone.utc),
                "parties": [0],
                "mimetype": "text/plain",
                "body": "Hello, world!",
            }
        ],
    }

    vcon = VconModel(**vcon_data)
    assert len(vcon.parties) == 1
    assert len(vcon.dialog) == 1
    assert isinstance(vcon.parties[0], PartyModel)
    assert isinstance(vcon.dialog[0], DialogModel)

    orig_vcon = vcon.to_vcon()
    assert orig_vcon.subject == "Test vCon"
    assert len(orig_vcon.parties) == 1
    assert len(orig_vcon.dialog) == 1


def test_dialog_model_validations():
    """Test DialogModel validation methods"""
    from datetime import datetime, timezone

    dialog_data = {
        "type": "text",
        "start": datetime.now(timezone.utc),
        "parties": [1, 2],
        "mimetype": "text/plain",
    }
    dialog = DialogModel(**dialog_data)
    assert dialog.mimetype == "text/plain"

    with pytest.raises(ValueError, match="Invalid MIME type"):
        DialogModel(**{**dialog_data, "mimetype": "invalid/type"})

    for encoding in ["json", "none", "base64url"]:
        dialog = DialogModel(**{**dialog_data, "encoding": encoding})
        assert dialog.encoding == encoding  # Test the return value

    with pytest.raises(ValueError, match="Invalid encoding"):
        DialogModel(**{**dialog_data, "encoding": "invalid"})


def test_dialog_model_type_checks():
    """Test DialogModel type check methods"""
    from datetime import datetime, timezone

    dialog = DialogModel(
        type="text",
        start=datetime.now(timezone.utc),
        parties=[1],
        mimetype="text/plain",
    )
    assert dialog.is_text() is True
    assert dialog.is_audio() is False
    assert dialog.is_video() is False
    assert dialog.is_email() is False

    dialog = DialogModel(
        type="audio",
        start=datetime.now(timezone.utc),
        parties=[1],
        mimetype="audio/x-wav",
    )
    assert dialog.is_text() is False
    assert dialog.is_audio() is True
    assert dialog.is_video() is False

    dialog = DialogModel(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[1],
        mimetype="video/x-mp4",
    )
    assert dialog.is_text() is False
    assert dialog.is_audio() is False
    assert dialog.is_video() is True

    dialog = DialogModel(
        type="email",
        start=datetime.now(timezone.utc),
        parties=[1],
        mimetype="message/rfc822",
    )
    assert dialog.is_text() is False
    assert dialog.is_email() is True


def test_dialog_model_data_location():
    """Test DialogModel data location methods"""
    from datetime import datetime, timezone

    dialog = DialogModel(
        type="audio",
        start=datetime.now(timezone.utc),
        parties=[1],
        url="https://example.com/audio.wav",
    )
    assert dialog.is_external_data() is True
    assert dialog.is_inline_data() is False

    dialog = DialogModel(
        type="text", start=datetime.now(timezone.utc), parties=[1], body="Hello, world!"
    )
    assert dialog.is_external_data() is False
    assert dialog.is_inline_data() is True


def test_dialog_model_with_party_history():
    """Test DialogModel with party history conversion"""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    dialog_data = {
        "type": "text",
        "start": now,
        "parties": [1, 2],
        "party_history": [
            {"party": 1, "event": "join", "time": now},
            {"party": 2, "event": "join", "time": now},
        ],
    }

    dialog = DialogModel(**dialog_data)
    assert len(dialog.party_history) == 2
    assert all(isinstance(ph, PartyHistoryModel) for ph in dialog.party_history)

    orig_dialog = dialog.to_dialog()
    assert len(orig_dialog.party_history) == 2
    assert all(hasattr(ph, "to_dict") for ph in orig_dialog.party_history)

    for i, ph in enumerate(orig_dialog.party_history):
        assert ph.party == dialog_data["party_history"][i]["party"]
        assert ph.event == dialog_data["party_history"][i]["event"]


def test_dialog_model_parent_validation():
    """Tests party index validation with parent context."""
    now = datetime.now(timezone.utc)

    class MockParent:
        def __init__(self):
            self.parties = [1, 2, 3]

    dialog = DialogModel(type="text", start=now, parties=[0, 1, 2], body="test")

    info = type("ValidationInfo", (), {"context": {"parent": MockParent()}})()
    result = dialog.validate_parties(dialog.parties, info)
    assert result == [0, 1, 2]

    with pytest.raises(ValueError, match="Invalid party index"):
        dialog = DialogModel(type="text", start=now, parties=[3], body="test")
        dialog.validate_parties(dialog.parties, info)


def test_dialog_model_video():
    """Test DialogModel video type handling"""
    from datetime import datetime, timezone

    dialog = DialogModel(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        mimetype="video/x-mp4",
    )
    assert dialog.is_video() is True

    dialog = DialogModel(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        mimetype="video/ogg",
    )
    assert dialog.is_video() is True


def test_dialog_model_video_negative():
    """Test DialogModel video type handling - negative cases"""
    dialog = DialogModel(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        mimetype="text/plain",  # Not a video mimetype
    )
    assert dialog.is_video() is False


def test_vcon_model_uuid_validation():
    """Test VconModel UUID validation"""
    vcon = VconModel(
        uuid=DEFAULT_UUID,
        vcon=DEFAULT_VCON_VERSION,
        created_at=datetime.now(timezone.utc),
    )
    assert vcon.uuid == DEFAULT_UUID


def test_vcon_model_uuid_validation_complete():
    """Test VconModel UUID validation - complete coverage"""
    assert VconModel.validate_uuid("test-uuid") == "test-uuid"

    vcon = VconModel(
        uuid="invalid-but-currently-allowed",
        vcon="0.0.1",
        created_at=datetime.now(timezone.utc),
    )
    assert vcon.uuid == "invalid-but-currently-allowed"


def test_vcon_model_updated_at():
    """Test VconModel updated_at handling"""
    now = datetime.now(timezone.utc)

    vcon = VconModel(
        uuid="01234567-89ab-cdef-0123-456789abcdef",
        vcon="0.0.1",
        created_at=now,
        updated_at=now,
    )

    converted = vcon.to_vcon()

    assert isinstance(converted.to_dict()["updated_at"], str)


def test_vcon_model_updated_at_none():
    """Test VconModel updated_at handling when None"""
    now = datetime.now(timezone.utc)

    vcon = VconModel(
        uuid="01234567-89ab-cdef-0123-456789abcdef",
        vcon="0.0.1",
        created_at=now,
        updated_at=None,  # explicitly so
    )

    converted = vcon.to_vcon()

    assert converted.updated_at is None
