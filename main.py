import databases, sqlalchemy, uuid
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime



## Postgres DataBase
DATABASE_URL = 'postgresql://postgres:1232323@localhost/usertest'
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "py_users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String  ),
    sqlalchemy.Column("password", sqlalchemy.String  ),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String ),
    sqlalchemy.Column("Gender", sqlalchemy.CHAR      ),
    sqlalchemy.Column("create_at", sqlalchemy.String ), 
    sqlalchemy.Column("status", sqlalchemy.CHAR      )

)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


## Models 
class UserList(BaseModel):
    id          :str
    username    :str
    password    :str
    first_name  :str
    last_name   :str
    Gender      :str
    create_at   :str
    status      :str


class UserEntry(BaseModel):
    id          :str = Field(...,example='XAZ')
    username    :str = Field(...,example='XAZ')
    password    :str = Field(...,example='XAZ')
    first_name  :str = Field(...,example='Emirka')
    last_name   :str = Field(...,example='Universe')
    Gender      :str = Field(...,example='M')


class UserUpdate(BaseModel):
    id          :str = Field(...,example='XAZ')
    first_name  :str = Field(...,example='Emirka')
    last_name   :str = Field(...,example='Universe')
    Gender      :str = Field(...,example='M')
    status      :str = Field(...,example='1')

class UserDelete(BaseModel):
    id          :str = Field(...,example='XAZ')





app = FastAPI()

@app.on_event('startup')
async def startup():
    await database.connect()

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()

@app.get('/users', response_model=List[UserList])
async def find_all_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get('/users/{userID}', response_model=UserList)
async def find_user_by_id(userID:str):
    query=users.select().where(users.c.id == userID)
    return await database.fetch_one(query)




@app.post('/users', response_model=UserList)
async def register_user(user: UserEntry):
    gen_id = str(uuid.uuid1())
    gen_date = str(datetime.now())
    query = users.insert().values(id = gen_id, username=user.username,
                                  password = user.password, 
                                  first_name=user.first_name, last_name=user.last_name,
                                  Gender = user.Gender, create_at=gen_date, status='1')
    
    await database.execute(query)
    return {'id':gen_id,**user.dict(), 'create_at':gen_date,'status':'1'}


@app.put('/users', response_model=UserList)
async def update_user(user:UserUpdate):
    gen_date = str(datetime.now())
    query = users.update().\
        where(users.c.id==user.id).\
        values(
            first_name =user.first_name,
            last_name  = user.last_name,
            Gender     = user.Gender,
            status     = user.status,
            create_at  = gen_date
        )
    await database.execute(query)
    return await find_user_by_id(user.id)

@app.delete('/users/{userID}')
async def delete_user_by_id(user:UserDelete):
    query=users.delete().where(users.c.id == user.id)
    await database.execute(query)
    return 'Удаление выполнено'


