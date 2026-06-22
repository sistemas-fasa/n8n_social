"""create initial social schema

Revision ID: 20260622_0001
Revises:
Create Date: 2026-06-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260622_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

post_status_check = "'borrador','pendiente_aprobacion','aprobado','programado','publicado','error','cancelado'"
platform_check = "'instagram','facebook'"


def upgrade() -> None:
    op.create_table(
        "social_assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("public_url", sa.String(length=1024), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "social_campaigns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(f"status in ({post_status_check})", name="ck_social_campaigns_status"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "social_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("piece_id", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=True),
        sa.Column("product_name", sa.String(length=255), nullable=True),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("campaign_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("approved_by", sa.String(length=255), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(f"status in ({post_status_check})", name="ck_social_posts_status"),
        sa.ForeignKeyConstraint(["asset_id"], ["social_assets.id"]),
        sa.ForeignKeyConstraint(["campaign_id"], ["social_campaigns.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("piece_id", name="uq_social_posts_piece_id"),
    )
    op.create_table(
        "social_post_channels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("social_post_id", sa.Integer(), nullable=False),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("hashtags", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta_media_id", sa.String(length=255), nullable=True),
        sa.Column("meta_post_id", sa.String(length=255), nullable=True),
        sa.Column("meta_photo_id", sa.String(length=255), nullable=True),
        sa.Column("permalink", sa.String(length=1024), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("raw_publish_response", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(f"platform in ({platform_check})", name="ck_social_post_channels_platform"),
        sa.CheckConstraint(f"status in ({post_status_check})", name="ck_social_post_channels_status"),
        sa.ForeignKeyConstraint(["social_post_id"], ["social_posts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "social_metric_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("social_post_channel_id", sa.Integer(), nullable=False),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("likes", sa.Integer(), nullable=True),
        sa.Column("comments", sa.Integer(), nullable=True),
        sa.Column("shares", sa.Integer(), nullable=True),
        sa.Column("saves", sa.Integer(), nullable=True),
        sa.Column("reactions", sa.Integer(), nullable=True),
        sa.Column("reach", sa.Integer(), nullable=True),
        sa.Column("impressions", sa.Integer(), nullable=True),
        sa.Column("engagements", sa.Integer(), nullable=True),
        sa.Column("raw_metrics_response", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["social_post_channel_id"], ["social_post_channels.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("social_metric_snapshots")
    op.drop_table("social_post_channels")
    op.drop_table("social_posts")
    op.drop_table("social_campaigns")
    op.drop_table("social_assets")
