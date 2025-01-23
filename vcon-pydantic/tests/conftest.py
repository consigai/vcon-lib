import pytest
from datetime import datetime, timezone
from vcon_pydantic import VconModel
import json
from pathlib import Path
import xml.etree.ElementTree as ET  # heh ET :) - this never gets old

# File paths
DRAFT_PATH = Path("tests/data/draft-ietf-vcon-vcon-container-01.xml")

# JSON types
JSON_MIME_TYPES = ["json", "application/json"]

# Common identifiers
DEFAULT_UUID = "01234567-89ab-8def-0123-456789abcdef"
DEFAULT_VCON_VERSION = "0.0.1"

# Test data
DEFAULT_PHONE = "+1234567890"
DEFAULT_AGENT = "Sophia Florez"
DEFAULT_CALLER = "Sully from Southie"
DEFAULT_SUBJECT = "Pahkin' the cah in Hahvahd Yahd"
DEFAULT_MESSAGE = "Can't make it, stuck in traffic on Storrow Drive"

# MIME types for testing
TEST_MIME_TYPES = {
    "text": "text/plain",
    "audio": "audio/x-wav",
    "video": "video/x-mp4",
    "email": "message/rfc822",
}


@pytest.fixture
def test_datetime():
    """Provide a fixed datetime for testing."""
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def basic_party_data():
    """Provide basic party data for testing."""
    return {
        "tel": DEFAULT_PHONE,
        "name": DEFAULT_AGENT,
        "role": "agent",
        "civicaddress": {"country": "US", "a1": "Massachusetts", "a3": "Boston"},
    }


@pytest.fixture
def basic_dialog_data(test_datetime):
    """Provide basic dialog data for testing."""
    return {
        "type": "text",
        "start": test_datetime,
        "parties": [0],
        "mimetype": TEST_MIME_TYPES["text"],
        "body": DEFAULT_MESSAGE,
        "party_history": [{"party": 0, "event": "join", "time": test_datetime}],
    }


@pytest.fixture
def sample_vcon_data(test_datetime):
    """Provide sample vCon data for testing."""
    return {
        "uuid": DEFAULT_UUID,
        "vcon": DEFAULT_VCON_VERSION,
        "created_at": test_datetime,
        "subject": DEFAULT_SUBJECT,
        "parties": [{"tel": DEFAULT_PHONE, "name": DEFAULT_CALLER, "role": "caller"}],
        "dialog": [
            {
                "type": "text",
                "start": test_datetime,
                "parties": [0],
                "mimetype": TEST_MIME_TYPES["text"],
                "body": DEFAULT_MESSAGE,
            }
        ],
    }


@pytest.fixture
def sample_vcon(sample_vcon_data):
    """Provide a sample VconModel instance."""
    return VconModel(**sample_vcon_data)


def process_json_block(element: ET.Element, index: int) -> dict | None:
    """Process a single JSON sourcecode block."""
    if element.get("type", "").lower() in JSON_MIME_TYPES:
        print(f"\nProcessing sourcecode block {index} (marked as JSON):")
    else:
        print(f"\nProcessing sourcecode block {index}:")

    json_str = element.text.strip()
    print(f"Content preview: {json_str[:100]}..." if len(json_str) > 100 else json_str)

    json_obj = json.loads(json_str)
    if "vcon" in json_obj:
        print(f"✓ Valid vCon example found: {json_obj.get('subject', 'No subject')}")
        print(f"  Version: {json_obj.get('vcon')}")
        print(f"  Parties: {len(json_obj.get('parties', []))}")
        print(f"  Dialog: {len(json_obj.get('dialog', []))}")
        return json_obj
    print("✗ Not a vCon object (no 'vcon' field)")
    return None


def extract_json_examples_from_draft():
    """Extract JSON examples from the IETF draft document."""
    if not DRAFT_PATH.exists():
        print(f"Draft file not found: {DRAFT_PATH}")
        return []

    try:
        root = ET.parse(DRAFT_PATH).getroot()
        examples = []

        for i, element in enumerate(root.findall(".//sourcecode"), 1):
            try:
                if example := process_json_block(element, i):
                    examples.append(example)
            except (json.JSONDecodeError, Exception) as e:
                print(f"✗ Error processing block {i}: {e}")

        print(f"\nTotal valid vCon examples found: {len(examples)}")
        return examples

    except ET.ParseError as e:
        print(f"Failed to parse XML document: {e}")
        return []


@pytest.fixture(scope="session")
def ietf_examples():
    """Provide all vCon examples from the IETF draft."""
    return extract_json_examples_from_draft()
