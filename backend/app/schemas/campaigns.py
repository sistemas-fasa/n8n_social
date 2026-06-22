from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.social import SocialPostStatus


class CampaignBase(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    status: str | None = Field(default=None)

    @model_validator(mode="after")
    def validate_dates_and_status(self) -> "CampaignBase":
        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            raise ValueError("ends_at cannot be before starts_at")
        if self.status is not None and self.status not in SocialPostStatus:
            raise ValueError("invalid campaign status")
        return self


class CampaignCreate(CampaignBase):
    name: str = Field(min_length=1, max_length=255)
    status: str = "borrador"


class CampaignUpdate(CampaignBase):
    pass


class CampaignRead(BaseModel):
    id: int
    name: str
    description: str | None
    starts_at: datetime | None
    ends_at: datetime | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
