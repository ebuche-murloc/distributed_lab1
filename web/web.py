import json
from os import environ

from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session

import models, schemas, crud
from database import SessionLocal, engine

import sender

SERVER_NAME = environ.get("NAME")

app = FastAPI()

models.Base.metadata.create_all(bind = engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello Worlddddddddd"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/links/", response_model=schemas.Link) #response_model вроде просто для отображения и сама по себе не роляет (не уверен, дочекаю)
def create_link(link: schemas.LinkCreate, db: Session = Depends(get_db)):
    db_link = crud.create_link(db, link)
    sender.send_massage_to_queue(json.dumps(db_link.as_dict(), default=str))
    return db_link


@app.get("/links/{link_id}", response_model=schemas.Link)
def read_link(link_id: int, db: Session = Depends(get_db)):
    db_link = crud.get_link(db, link_id=link_id)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return db_link

@app.put("/links/{link_id}", response_model=schemas.Link)
def update_link(link_id: int, link: schemas.LinkUpdate, db: Session = Depends(get_db)):
    print(str(link.status) + " update_link", flush=True)
    db_link = crud.update_link(db, link_id=link_id, link_update=link)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return db_link

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Server-Name"] = SERVER_NAME
    return response