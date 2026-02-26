import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TariffBaseMixin(BaseModel):
    name: str
    description: str
    price: int = Field(..., ge=0)
    period_days: int = Field(..., gt=0)
    project_limit: int = Field(..., ge=0)
    room_limit: int = Field(..., ge=0)
    furniture_regeneration_limit: int = Field(..., ge=0)


class TariffCreate(TariffBaseMixin):
    pass


class TariffUpdate(TariffBaseMixin):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    period_days: Optional[int] = Field(None, gt=0)
    project_limit: Optional[int] = None
    room_limit: Optional[int] = None
    furniture_regeneration_limit: Optional[int] = None


class TariffRead(TariffBaseMixin):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
