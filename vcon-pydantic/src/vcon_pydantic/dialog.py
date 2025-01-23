from .base import VconBase
from .party import PartyHistoryModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field, field_validator
from vcon.dialog import Dialog
from vcon.party import PartyHistory

MIME_TYPES = [
    "text/plain",
    "audio/x-wav",
    "audio/x-mp3",
    "audio/x-mp4",
    "audio/ogg",
    "video/x-mp4",
    "video/ogg",
    "multipart/mixed",
    "message/external-body",
    "message/rfc822",
]


class DialogModel(VconBase):
    """Pydantic model for vCon dialog entry."""

    type: str
    start: datetime
    parties: List[int]
    originator: Optional[int] = None
    mimetype: Optional[str] = Field(None, description="MIME type of the dialog content")
    filename: Optional[str] = None
    body: Optional[str] = None
    encoding: Optional[str] = None
    url: Optional[str] = None
    alg: Optional[str] = None
    signature: Optional[str] = None
    disposition: Optional[str] = None
    party_history: Optional[List[PartyHistoryModel]] = None
    transferee: Optional[int] = None
    transferor: Optional[int] = None
    transfer_target: Optional[int] = None
    original: Optional[int] = None
    consultation: Optional[int] = None
    target_dialog: Optional[int] = None
    campaign: Optional[str] = None
    interaction: Optional[str] = None
    skill: Optional[str] = None
    duration: Optional[float] = None
    meta: Optional[Dict[str, Any]] = None

    @field_validator("mimetype")
    def validate_mimetype(cls, v):
        """Validates MIME type."""
        if v and v not in MIME_TYPES:
            raise ValueError(
                f"Invalid MIME type. Must be one of: {', '.join(MIME_TYPES)}"
            )
        return v

    @field_validator("encoding")
    def validate_encoding(cls, v):
        """Validates encoding."""
        if v and v not in ["json", "none", "base64url"]:
            raise ValueError("Invalid encoding. Must be one of: json, none, base64url")
        return v

    @field_validator("parties")
    def validate_parties(cls, v, info):
        """Validate that party indices are valid"""
        # Only validate party indices when we have context
        if info.context and isinstance(info.context, dict):
            parent = info.context.get("parent")
            if parent and hasattr(parent, "parties"):
                max_party = len(parent.parties)
                for party_idx in v:
                    if party_idx >= max_party:
                        raise ValueError(
                            f"Invalid party index {party_idx}, max valid index is {max_party - 1}"
                        )
        return v

    def to_dialog(self) -> Dialog:
        """Returns an original Dialog instance."""
        data = self.model_dump(exclude_none=True)

        if data.get("start"):
            data["start"] = data["start"].isoformat()

        if self.party_history:
            data["party_history"] = [
                PartyHistory(ph.party, ph.event, ph.time.isoformat())
                for ph in self.party_history
            ]

        if "meta" in data and not data["meta"]:
            del data["meta"]

        return Dialog(**data)

    def is_text(self) -> bool:
        """Returns True if dialog is text type."""
        return self.mimetype == "text/plain"

    def is_audio(self) -> bool:
        """Returns True if dialog is audio type."""
        return self.mimetype in [
            "audio/x-wav",
            "audio/x-mp3",
            "audio/x-mp4",
            "audio/ogg",
        ]

    def is_video(self) -> bool:
        """Returns True if dialog is video type."""
        return self.mimetype in ["video/x-mp4", "video/ogg"]

    def is_email(self) -> bool:
        """Returns True if dialog is email type."""
        return self.mimetype == "message/rfc822"

    def is_external_data(self) -> bool:
        """Returns True if dialog contains external data."""
        return bool(self.url)

    def is_inline_data(self) -> bool:
        """Returns True if dialog contains inline data."""
        return not self.is_external_data()
