from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from datetime import datetime
from database import create_db_and_tables, engine
from models import Campaign
from routers import campaigns, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(name='Sai Ram Gunturu', due_date=datetime.now()),
                Campaign(name='Srujana Duggineni', due_date=datetime.now())
            ])
            session.commit()
    yield

app = FastAPI(root_path='/api/v1', lifespan=lifespan)
app.include_router(campaigns.router)
app.include_router(auth.router)