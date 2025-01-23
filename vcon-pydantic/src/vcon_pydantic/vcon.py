from datetime import datetime, timezone
from .base import VconBase
from .party import PartyModel
from .dialog import DialogModel
from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator, model_validator

from vcon.vcon import Vcon


class VconModel(VconBase):
    """Pydantic model for vCon container."""

    uuid: str = Field(..., description="UUID v8 identifier")
    vcon: str = Field(..., description="vCon version")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    subject: Optional[str] = None
    redacted: Dict[str, Any] = Field(default_factory=dict)
    appended: Optional[Dict[str, Any]] = None
    group: List[str] = Field(default_factory=list)
    parties: List[PartyModel] = Field(default_factory=list)
    dialog: List[DialogModel] = Field(default_factory=list)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    analysis: List[Dict[str, Any]] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("uuid")
    def validate_uuid(cls, v):
        return v

    @model_validator(mode="after")
    def validate_dialog_parties(self):
        """Validates that dialog party indices are valid."""
        if self.dialog:
            max_party = len(self.parties)
            for dialog in self.dialog:
                if not self.parties and not dialog.parties:
                    continue

                for party_idx in dialog.parties:
                    if party_idx >= max_party:
                        raise ValueError(
                            f"Invalid party index {party_idx}, max valid index is {max_party - 1}"
                        )
        return self

    def to_vcon(self) -> Vcon:
        """Returns an original Vcon instance."""
        data = self.model_dump(exclude_none=True)

        if data.get("created_at"):
            data["created_at"] = data["created_at"].isoformat()
        if data.get("updated_at"):
            data["updated_at"] = data["updated_at"].isoformat()

        if "parties" in data:
            data["parties"] = [p.to_party().to_dict() for p in self.parties]
        if "dialog" in data:
            dialogs = [d.to_dialog() for d in self.dialog]
            data["dialog"] = [d.to_dict() for d in dialogs]

        for key in ["group", "attachments", "analysis", "redacted", "meta"]:
            if key in data and not data[key]:
                del data[key]

        return Vcon(data)

    @classmethod
    def build_new(cls) -> "VconModel":
        """Returns a new VconModel with default values."""
        return cls(
            uuid=Vcon.build_new().uuid,
            vcon="0.0.1",
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def uuid8_domain_name(domain_name: str) -> str:
        """Returns a UUID8 for the given domain name."""
        return Vcon.uuid8_domain_name(domain_name)
