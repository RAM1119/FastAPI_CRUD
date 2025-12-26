from fastapi import FastAPI, HTTPException, Request, Depends
from datetime import datetime
from typing import Any, Dict, Annotated, List, Generic, TypeVar
from random import randint
from sqlmodel import create_engine, SQLModel, Session, select, Field
from contextlib import asynccontextmanager
from pydantic import BaseModel

###################### SQL MODEL ######################################################

class Campaign(SQLModel, table=True):
    campaign_id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(default=None, index=True)
    due_date: datetime | None = Field(default=None, index=True)
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(), index=True)
    
class CampaignCreate(SQLModel):
    name: str | None = None
    due_date: datetime | None = None
################### SQL ################################################################

sqlite_file_name = 'database.db'
sqlite_url = f'sqlite:///{sqlite_file_name}'

connect_args = {'check_same_thread':False}
engine = create_engine(sqlite_url,connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session,Depends(get_session)]
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(name = 'Sai Ram Gunturu', due_date = datetime.now()),
                Campaign(name = 'Srujana Duggineni', due_date = datetime.now())
            ])
            session.commit()
    yield
        
    
app = FastAPI(root_path='/api/v1',lifespan=lifespan)
T = TypeVar('T')

################################# App with Database ##########################################

class Response(BaseModel,Generic[T]):
    data: T

@app.get('/campaigns', response_model = Response[List[Campaign]])
async def campaigns(session: SessionDep):
    data = session.exec(select(Campaign)).all()
    return {'data':data}

# Path parameter is the below
# Query parameter is the one we will see after ? 

@app.get('/campaign/{id}',response_model = Response[Campaign])
async def read_campaign(session: SessionDep,id):
    data = session.get(Campaign,id)
    if not data:
        raise HTTPException(status_code=404)
    return {'data':data}

@app.post('/campaigns',status_code=201,response_model = Response[Campaign])
async def create_campaign(campaign: CampaignCreate,session: SessionDep):
    db_campaign = Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {'data':db_campaign}


@app.put('/campaigns/{id}', response_model=Response[Campaign])
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


@app.delete('/campaign_delete/{id}',status_code=204)
async def campaign_delete(id:int, session: SessionDep):
    data = session.get(Campaign,id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()
    return {'Successfully deleted Campaign with ID':id}
################################# App with dummy data ##########################################

# """
# Campaigns
# - campaign_id
# - name
# - due_date
# - created_at
# """

# data: Any = [
#     {
#         'campaign_id':1 , 
#         'name': 'Sai Ram Gunturu' , 
#         'due_date': datetime.now() ,
#         'created_at': datetime.now()
#     },
#     {
#         'campaign_id':2 , 
#         'name': 'Somesh Yadav' , 
#         'due_date': datetime.now() ,
#         'created_at': datetime.now()
#     },
#     {
#         'campaign_id':3 , 
#         'name': 'Tony Kakkar' , 
#         'due_date': datetime.now() ,
#         'created_at': datetime.now()
#     }
# ]

# @app.get('/')
# async def root():
#     return {'message':'Hello World'}

# @app.get('/campaigns')
# async def read_campaigns():
#     return {'campaign': data}

# @app.get('/campaigns/{id}')
# async def read_campaign(id: int):
#     for campaign in data:
#         if campaign.get('campaign_id') == id:
#             return {'campaign':campaign}
#     raise HTTPException(status_code=404)

# @app.post('/campaigns')
# async def create_campaign(body: Dict[str,Any]):
#     new = {
#         'campaign_id':randint(100,10000000), 
#         'name': body.get('name') , 
#         'due_date': body.get('due_date') ,
#         'created_at': datetime.now()   
#     }
#     data.append(new)
#     return {'campaign': new}

# @app.put('/update_campaign/{id}')
# async def update_campaign(id: int,body: Dict[str,Any]):
#     for index,campaign in enumerate(data):
#         if campaign.get('campaign_id') == id:
#             updated: Any = {
#                     'campaign_id':id, 
#                     'name': body.get('name') , 
#                     'due_date': body.get('due_date') ,
#                     'created_at': campaign.get('created_at') 
#                 }
#             data[index] = updated  
#             return {'Updated campaign': updated}
#     raise HTTPException(status_code=404,detail='Campaign data not found')


# @app.delete('/delete_campaign/{id}',status_code=204) # it will return 204 directly if it is success
# async def delete_campaign(id: int):
#     for index, campaign in enumerate(data):
#         if campaign.get('campaign_id') == id:
#             deleted_item = campaign
#             data.remove(campaign)
#             return {'Deleted Campaign':deleted_item}
#     raise HTTPException(status_code=404,detail='Campaign not found')
            
