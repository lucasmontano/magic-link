from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from redis import Redis
from rq import Queue

INVALID_OPTIONS = "The current poll only accept voting in the following options: "

app = FastAPI()

redis_conn = Redis()
votes_queue = Queue('votes', connection=redis_conn)

current_options = {'COBOL', 'VB', 'Delphi'}
# TODO save dict/set into redis
redis_conn.sadd("current_poll_options", current_options)


class Vote(BaseModel):
    identifier: str
    options: List[str]


def confirm_vote(vote: Vote):
    print(vote.identifier)
    return vote.options


def check_invalid_options(vote: Vote):
    # TODO check if current_poll_options contains all vote.options
    invalid_options: List[str]
    for option in vote.options:
        if not redis_conn.hexists("current_poll_options", option):
            invalid_options.append(option)
    return invalid_options


@app.get("/")
def read_root():
    print(votes_queue.jobs)
    return {"Hello": "World"}


@app.post("/vote/")
def vote(vote: Vote):
    invalid_options = check_invalid_options(vote)
    if len(invalid_options) == 0:
        votes_queue.enqueue(confirm_vote, vote)
        return ""
    else:
        return {
            "message": INVALID_OPTIONS + invalid_options.__str__()
        }
