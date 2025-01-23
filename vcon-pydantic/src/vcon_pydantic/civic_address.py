from .base import VconBase
from typing import Optional
from pydantic import Field
from vcon.civic_address import CivicAddress


class CivicAddressModel(VconBase):
    country: Optional[str] = Field(
        None, description="Country code (ISO 3166-1 alpha-2)"
    )
    a1: Optional[str] = Field(
        None, description="Administrative area 1 (state/province)"
    )
    a2: Optional[str] = Field(
        None, description="Administrative area 2 (county/municipality)"
    )
    a3: Optional[str] = Field(None, description="Administrative area 3 (city/town)")
    a4: Optional[str] = Field(
        None, description="Administrative area 4 (neighborhood/district)"
    )
    a5: Optional[str] = Field(None, description="Administrative area 5")
    a6: Optional[str] = Field(None, description="Administrative area 6")
    prd: Optional[str] = Field(None, description="Premier")
    pod: Optional[str] = Field(None, description="Post office box")
    sts: Optional[str] = Field(None, description="Street name")
    hno: Optional[str] = Field(None, description="House number")
    hns: Optional[str] = Field(None, description="House name")
    lmk: Optional[str] = Field(None, description="Landmark")
    loc: Optional[str] = Field(None, description="Location")
    flr: Optional[str] = Field(None, description="Floor")
    nam: Optional[str] = Field(None, description="Name")
    pc: Optional[str] = Field(None, description="Postal code")

    def to_civic_address(self) -> CivicAddress:
        """Convert to original CivicAddress instance"""
        return CivicAddress(**self.model_dump(exclude_none=True))
