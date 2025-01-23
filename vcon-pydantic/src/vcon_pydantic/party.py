from .base import VconBase
from .civic_address import CivicAddressModel
from typing import Optional, Dict, Any
from datetime import datetime
from vcon.party import Party, PartyHistory


class PartyModel(VconBase):
    tel: Optional[str] = None
    stir: Optional[str] = None
    mailto: Optional[str] = None
    name: Optional[str] = None
    validation: Optional[str] = None
    gmlpos: Optional[str] = None
    civicaddress: Optional[CivicAddressModel] = None
    uuid: Optional[str] = None
    role: Optional[str] = None
    contact_list: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    def to_party(self) -> Party:
        """Convert to original Party instance"""
        data = self.model_dump(exclude_none=True)
        if self.civicaddress:
            data["civicaddress"] = self.civicaddress.to_civic_address()
        return Party(**data)


class PartyHistoryModel(VconBase):
    party: int
    event: str
    time: datetime

    def to_party_history(self) -> PartyHistory:
        """Convert to original PartyHistory instance"""
        return PartyHistory(**self.model_dump())
