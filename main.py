from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from redis import Redis
from rq import Queue
import jwt

INVALID_OPTIONS = "You are trying to vote in one or more invalid options, please check the available options."

app = FastAPI()

redis_conn = Redis()
votes_queue = Queue('votes', connection=redis_conn)

# todo load current_options from database
redis_conn.sadd('poll_options', 'COBOL', 'VB', 'Delphi')


class Vote(BaseModel):
    identifier: str
    options: set


def confirm_vote(vote: Vote):    
    encoded = str(jwt.encode(jsonable_encoder(vote.dict()),'secret', algorithm='HS256'))
    print("vote enconded to JWT: " + encoded)
    print("sending confirmation to: " + vote.identifier)    
    return vote.options


def check_valid_options(vote: Vote):
    for option in vote.options:
        if not redis_conn.sismember("poll_options", option):
            return False
    return True


@app.get("/")
def read_root():
    print(votes_queue.jobs)
    return {"Hello": "World"}


@app.post("/vote/", status_code=204)
def vote(vote: Vote):
    if check_valid_options(vote):
        votes_queue.enqueue(confirm_vote, vote)
    else:
        error_detail = jsonable_encoder({
            "message": INVALID_OPTIONS,
            "options": redis_conn.smembers("poll_options")
        })
        raise HTTPException(status_code=400, detail=error_detail)
