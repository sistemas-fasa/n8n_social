from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

SocialPostStatus = (
    "borrador",
    "pendiente_aprobacion",
    "aprobado",
    "programado",
    "publicado",
    "error",
    "cancelado",
)
SocialPostChannelStatus = SocialPostStatus
SocialPlatform = ("instagram", "facebook")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class UpdatedTimestampMixin(TimestampMixin):
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class SocialAsset(TimestampMixin, Base):
    __tablename__ = "social_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    public_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    width: Mapped[int | None] = mapped_column(nullable=True)
    height: Mapped[int | None] = mapped_column(nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    posts: Mapped[list["SocialPost"]] = relationship(back_populates="asset")


class SocialCampaign(UpdatedTimestampMixin, Base):
    __tablename__ = "social_campaigns"
    __table_args__ = (
        CheckConstraint(
            f"status in {SocialPostStatus}",
            name="ck_social_campaigns_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="borrador")

    posts: Mapped[list["SocialPost"]] = relationship(back_populates="campaign")


class SocialPost(UpdatedTimestampMixin, Base):
    __tablename__ = "social_posts"
    __table_args__ = (
        CheckConstraint(
            f"status in {SocialPostStatus}",
            name="ck_social_posts_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    piece_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("social_assets.id"), nullable=True)
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("social_campaigns.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="borrador")
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    asset: Mapped[SocialAsset | None] = relationship(back_populates="posts")
    campaign: Mapped[SocialCampaign | None] = relationship(back_populates="posts")
    channels: Mapped[list["SocialPostChannel"]] = relationship(back_populates="social_post")


class SocialPostChannel(UpdatedTimestampMixin, Base):
    __tablename__ = "social_post_channels"
    __table_args__ = (
        CheckConstraint(
            f"platform in {SocialPlatform}",
            name="ck_social_post_channels_platform",
        ),
        CheckConstraint(
            f"status in {SocialPostChannelStatus}",
            name="ck_social_post_channels_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    social_post_id: Mapped[int] = mapped_column(ForeignKey("social_posts.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="borrador")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meta_media_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_post_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_photo_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    permalink: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_publish_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    social_post: Mapped[SocialPost] = relationship(back_populates="channels")
    metric_snapshots: Mapped[list["SocialMetricSnapshot"]] = relationship(back_populates="social_post_channel")


class SocialMetricSnapshot(TimestampMixin, Base):
    __tablename__ = "social_metric_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    social_post_channel_id: Mapped[int] = mapped_column(ForeignKey("social_post_channels.id"), nullable=False)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    likes: Mapped[int | None] = mapped_column(nullable=True)
    comments: Mapped[int | None] = mapped_column(nullable=True)
    shares: Mapped[int | None] = mapped_column(nullable=True)
    saves: Mapped[int | None] = mapped_column(nullable=True)
    reactions: Mapped[int | None] = mapped_column(nullable=True)
    reach: Mapped[int | None] = mapped_column(nullable=True)
    impressions: Mapped[int | None] = mapped_column(nullable=True)
    engagements: Mapped[int | None] = mapped_column(nullable=True)
    raw_metrics_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    social_post_channel: Mapped[SocialPostChannel] = relationship(back_populates="metric_snapshots")
