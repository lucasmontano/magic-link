from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from redis import Redis
from rq import Queue
import jwt
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

INVALID_IDENTIFIER = "Please, check identifier."

app = FastAPI()

redis_conn = Redis()
magic_link_queue = Queue('send_magic_links', connection=redis_conn)

class MagicLink(BaseModel):
    identifier: str
    payload: dict


def confirm_identifier(magic: MagicLink):
    encoded = str(jwt.encode(jsonable_encoder(magic.dict()), 'secret', algorithm='HS256'))
    print("Payload enconded to JWT: " + encoded)
    print("sending confirmation to: " + magic.identifier)
    message = Mail(
        from_email='evoluindo@lucasmontano.com',
        to_emails=magic.identifier,
        subject='Are you a bot?',
        html_content='<a href="http://127.0.0.1:8000/confirm/' + encoded + '">Confirm you are human or a super smart bot: </a>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.body)

    return magic.payload


def validate_identifier(magic: MagicLink):
    # TODO validate identifier with regex
    return True


@app.post("/validate/", status_code=204)
def validate(jwt: str):
    # TODO validate JWT
    print(jwt.jobs)

@app.post("/send/", status_code=204)
def send(magic: MagicLink):
    if validate_identifier(magic):
        magic_link_queue.enqueue(confirm_identifier, magic)
    else:
        error_detail = jsonable_encoder({
            "message": INVALID_IDENTIFIER            
        })
        raise HTTPException(status_code=400, detail=error_detail)
