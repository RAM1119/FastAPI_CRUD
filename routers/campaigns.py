from fastapi import APIRouter, HTTPException, Depends
from typing import List
from database import SessionDep
from models import Campaign
from schemas import CampaignCreate, Response
from sqlmodel import select
from routers.auth import get_current_user

router = APIRouter(prefix='/campaigns', tags=['campaigns'])

@router.get('/', response_model=Response[List[Campaign]])
async def get_campaigns(session: SessionDep, user_id: int = Depends(get_current_user)):
    data = session.exec(select(Campaign)).all()
    return {'data': data}

@router.get('/{id}', response_model=Response[Campaign])
async def get_campaign(session: SessionDep, id: int, user_id: int = Depends(get_current_user)):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    return {'data': data}

@router.post('/', status_code=201, response_model=Response[Campaign])
async def create_campaign(campaign: CampaignCreate, session: SessionDep, user_id: int = Depends(get_current_user)):
    db_campaign = Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {'data': db_campaign}

@router.put('/{id}', response_model=Response[Campaign])
async def update_campaign(session: SessionDep, id: int, campaign: CampaignCreate):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    data.name = campaign.name
    data.due_date = campaign.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {'data': data}

@router.delete('/{id}', status_code=204)
async def delete_campaign(id: int, session: SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()
    return None