# ranked-voting
This is the second edition of #umaStackQueNaoDomino. Python Edition.
The project offer API for a Preferential Voting System using the ranked voting method.

# First things first 
You need to have pip (of course).
 
- `python3 -m venv env`
- `source env/bin/activate`
- `which python`
- `pip install fastapi`
- `pip install uvicorn`
- `pip install rq`
- `pip install redis`

## How to Run
### Running FastAPI
- `uvicorn main:app --reload`

### Running Redis Server
- `redis-server`

### Listening the Queue
- `rq worker votes`   

## links