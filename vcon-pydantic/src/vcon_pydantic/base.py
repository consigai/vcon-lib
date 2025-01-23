from pydantic import BaseModel, ConfigDict


class VconBase(BaseModel):
    """Base model with common configuration for all vCon Pydantic models"""

    model_config = ConfigDict(
        extra="allow", # definitely wanna allow forward compatibility for when I don't get around to updating anything here and future me hates past me for this
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )
