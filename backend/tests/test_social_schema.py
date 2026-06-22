from app.db import Base
from app.models import social


def test_social_schema_tables_are_registered() -> None:
    expected_tables = {
        "social_assets",
        "social_campaigns",
        "social_posts",
        "social_post_channels",
        "social_metric_snapshots",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())


def test_social_schema_relationships_are_defined() -> None:
    posts = Base.metadata.tables["social_posts"]
    channels = Base.metadata.tables["social_post_channels"]
    metric_snapshots = Base.metadata.tables["social_metric_snapshots"]

    assert posts.c.asset_id.foreign_keys
    assert posts.c.campaign_id.foreign_keys
    assert channels.c.social_post_id.foreign_keys
    assert metric_snapshots.c.social_post_channel_id.foreign_keys


def test_social_schema_controls_statuses_and_platforms() -> None:
    post_statuses = set(social.SocialPostStatus)
    channel_statuses = set(social.SocialPostChannelStatus)
    platforms = set(social.SocialPlatform)

    assert {
        "borrador",
        "pendiente_aprobacion",
        "aprobado",
        "programado",
        "publicado",
        "error",
        "cancelado",
    }.issubset(post_statuses)
    assert {"instagram", "facebook"} == platforms
    assert post_statuses.issubset(channel_statuses)


def test_social_schema_can_store_raw_external_responses() -> None:
    channels = Base.metadata.tables["social_post_channels"]
    metric_snapshots = Base.metadata.tables["social_metric_snapshots"]

    assert "raw_publish_response" in channels.c
    assert "raw_metrics_response" in metric_snapshots.c
