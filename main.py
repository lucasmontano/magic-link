from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr
from redis import Redis
from rq import Queue
import jwt
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

INVALID_IDENTIFIER = "Please, check identifier."
INVALID_JWT = "Of course! You shall not pass!"

JWT_SECRET = os.environ.get('JWT_SECRET')

app = FastAPI()

redis_conn = Redis()
magic_link_queue = Queue('send_magic_links', connection=redis_conn)


class MagicLink(BaseModel):
    identifier: EmailStr
    payload: dict


def confirm_identifier(magic: MagicLink):
    encoded = jwt.encode(jsonable_encoder(magic.dict()), JWT_SECRET, algorithm='HS256').decode('utf-8')
    print("Payload enconded to JWT: " + encoded)
    print("sending confirmation to: " + magic.identifier)
    message = Mail(
        from_email=os.environ.get('SENDGRID_SENDER'),
        to_emails=magic.identifier,
        subject='Are you a bot?',
        html_content='<a href="http://127.0.0.1:8000/validate/?token=' + encoded + '">Confirm you are human or a super smart bot: </a>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.body)

    return magic.payload


@app.get("/validate/", status_code=204)
def validate(token: str):    
    try:        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        # TODO add identifier validation status to the database
        print(payload)
    except Exception as e:
        print(e)
        error_detail = jsonable_encoder({
            "message": INVALID_JWT
        })
        raise HTTPException(status_code=400, detail=error_detail)
        

@app.post("/send/", status_code=204)
def send(magic: MagicLink):
    magic_link_queue.enqueue(confirm_identifier, magic)
