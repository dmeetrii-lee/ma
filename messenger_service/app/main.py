import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Form, Header
from typing import Annotated
from keycloak import KeycloakOpenID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database import database as database
from database.database import Message
from datetime import datetime

app = FastAPI()
database.Base.metadata.create_all(bind=database.engine)

KEYCLOAK_URL = "http://keycloak:8080/"
KEYCLOAK_CLIENT_ID = "testClient"
KEYCLOAK_REALM = "testRealm"
KEYCLOAK_CLIENT_SECRET = "**********"

user_token = ""
keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                  client_id=KEYCLOAK_CLIENT_ID,
                                  realm_name=KEYCLOAK_REALM,
                                  client_secret_key=KEYCLOAK_CLIENT_SECRET)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
author = ""

from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

@app.post("/get_token")
async def get_token(username: str = Form(...), password: str = Form(...)):
    try:
        token = keycloak_openid.token(grant_type=["password"],
                                      username=username,
                                      password=password)
        return token
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Не удалось получить токен")

def check_user_roles(token):
    try:
        token_info = keycloak_openid.introspect(token)
        if "test" not in token_info["realm_access"]["roles"]:
            raise HTTPException(status_code=403, detail="Access denied")
        return token_info
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or access denied")

@app.get("/health", status_code=status.HTTP_200_OK)
async def service_alive(token: str = Header()):
    if (check_user_roles(token)):
        return {'message': 'service alive'}
    else:
        return "Wrong JWT Token"

@app.post("/login", status_code=status.HTTP_200_OK)
async def login(name: str, token: str = Header()):
    if (check_user_roles(token)):
        global author
        author = name
        return f"You logged in as {author}"
    else:
        return "Wrong JWT Token"

@app.post("/send_message")
async def send_message(receiver_name: str, text: str, db: db_dependency, token: str = Header()):
    if (check_user_roles(token)):
        message_db = Message(sender_name=author,
                             receiver_name=receiver_name,
                             datetime=datetime.now(),
                             text=text)
        try:
            db.add(message_db)
            db.commit()
            db.refresh(message_db)
            return "Success"
        except Exception as e:
            return "Cant add message"
    else:
        return "Wrong JWT Token"

@app.get("/get_messages_with_user")
async def get_messages_from_user(username: str, db: db_dependency, token: str = Header()):
    if (check_user_roles(token)):
        try:
            result = db.query(Message).filter(
                or_(
                    and_(Message.receiver_name == author, Message.sender_name == username),
                    and_(Message.receiver_name == username, Message.sender_name == author)
                )
            ).all()
            return result
        except Exception as e:
            raise HTTPException(status_code=404, detail="Messages not found")
    else:
        return "Wrong JWT Token"

@app.get("/get_messages_from")
async def get_messages_from_user(username: str, db: db_dependency, token: str = Header()):
    if (check_user_roles(token)):
        try:
            result = db.query(Message).filter(
                and_(
                    Message.receiver_name == author,
                    Message.sender_name == username
                )
            ).all()
            return result
        except Exception as e:
            raise HTTPException(status_code=404, detail="Messages not found")
    else:
        return "Wrong JWT Token"

@app.get("/get_messages_to_user")
async def get_messages_to_user(username: str, db: db_dependency, token: str = Header()):
    if (check_user_roles(token)):
        try:
            result = db.query(Message).filter(
                and_(
                    Message.receiver_name == username,
                    Message.sender_name == author
                )
            ).all()
            return result
        except Exception as e:
            raise HTTPException(status_code=404, detail="Messages not found")
    else:
        return "Wrong JWT Token"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))