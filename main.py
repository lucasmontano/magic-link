from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from redis import Redis
from rq import Queue

app = FastAPI()


class Vote(BaseModel):
    identifier: str
    options: List[str]

def confirm_vote(vote):
    print(vote.identifier)
    return vote.options

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/vote/")
def vote(vote: Vote):
    redis_conn = Redis()
    q = Queue('votes', connection=redis_conn)
    q.enqueue(confirm_vote, vote)
    return vote
