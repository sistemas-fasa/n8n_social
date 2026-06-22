from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models.social import SocialCampaign
from app.schemas.campaigns import CampaignCreate, CampaignRead, CampaignUpdate

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def get_campaign_or_404(session: Session, campaign_id: int) -> SocialCampaign:
    campaign = session.get(SocialCampaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("", response_model=list[CampaignRead])
def list_campaigns(session: Session = Depends(get_session)) -> list[SocialCampaign]:
    return list(session.scalars(select(SocialCampaign).order_by(SocialCampaign.id)))


@router.post("", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
def create_campaign(payload: CampaignCreate, session: Session = Depends(get_session)) -> SocialCampaign:
    campaign = SocialCampaign(**payload.model_dump())
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(campaign_id: int, session: Session = Depends(get_session)) -> SocialCampaign:
    return get_campaign_or_404(session, campaign_id)


@router.put("/{campaign_id}", response_model=CampaignRead)
def update_campaign(
    campaign_id: int,
    payload: CampaignUpdate,
    session: Session = Depends(get_session),
) -> SocialCampaign:
    campaign = get_campaign_or_404(session, campaign_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    session.commit()
    session.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_campaign(campaign_id: int, session: Session = Depends(get_session)) -> Response:
    campaign = get_campaign_or_404(session, campaign_id)
    campaign.status = "cancelado"
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
