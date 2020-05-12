from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()


class Vote(BaseModel):
    identifier: str
    options: List[str]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/vote/")
def vote(vote: Vote):
    return vote
