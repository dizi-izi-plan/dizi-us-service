import uuid
import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schema.tariff import TariffRead


class SubscriptionBase(BaseModel):
    start_date: datetime.datetime
    end_date: datetime.datetime
    is_active: bool
    tariff_id: uuid.UUID


class SubscriptionCreate(SubscriptionBase):
    user_id: uuid.UUID


class SubscriptionUpdate(BaseModel):
    is_active: Optional[bool] = None
    end_date: Optional[datetime.datetime] = None


class SubscriptionRead(SubscriptionBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class SubscriptionShortRead(BaseModel):
    id: uuid.UUID
    start_date: datetime.datetime
    end_date: datetime.datetime
    is_active: bool
    tariff: TariffRead

    model_config = ConfigDict(from_attributes=True)
