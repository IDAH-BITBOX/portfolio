# -*- coding: utf-8 -*-
## basic modules load ##
import os, sys
import uvicorn
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, Request, UploadFile, Depends, Security, status
from fastapi.security import APIKeyHeader
from fastapi.security.api_key import APIKey
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from fastapi import HTTPException #차후 에러문을 위한 HTTPException import
from datetime import timedelta
import datetime
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi_utilities import repeat_every


## Elastic Search ##
# es = Elasticsearch("")


# from jina import Client, Document
# from transformers import T5ForConditionalGeneration, T5Tokenizer

'''model = T5ForConditionalGeneration.from_pretrained('j5ng/et5-typos-corrector')
tokenizer = T5Tokenizer.from_pretrained('j5ng/et5-typos-corrector')
typos_corrector = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    device=-1,
    framework="pt",
    )'''

# model_name = "gogamza/kobart-base-v2"
## 'text2text-generation'
## mrm8488/t5-base-finetuned-question-generation-ap
from transformers import pipeline

#model_name = "gogamza/kobart-base-v2"
model_name = "heegyu/kobart-text-style-transfer"
model_path = 'components/models/yjoh_model/'
#nlg_pipeline = pipeline('text2text-generation',model=model_path, tokenizer=model_name)


from sentence_transformers import SentenceTransformer

similarity_model = SentenceTransformer('jhgan/ko-sbert-multitask')
#similarity_model = SentenceTransformer('jhgan/ko-sroberta-multitask')


## components load ##
from components.toss_bomb_game import *
from components.libs.basic import *


## Jina API ##
# client = Client(host='0.0.0.0:9097', asyncio=True)

## API ##
api = FastAPI()
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
#api.mount("/", StaticFiles(directory="./"), name="static")
templates = Jinja2Templates(directory="templates")
origins = [
    ""
]

## API 암호화 ##
SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def custom_openapi():
    if api.openapi_schema:
        return api.openapi_schema
    openapi_schema = get_openapi(
        title="Bomb Toss API",
        version="0.0.1",
        description="질문 폭탄 게임 API SWAGGER 입니다",
        routes=api.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    api.openapi_schema = openapi_schema
    return api.openapi_schema

api.openapi = custom_openapi

### Objects ###
class Notifier:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.connections_meta: Dict[str, List[WebSocket]] = {}
        #self.connection_by: Dict[str, List[WebSocket]] = {}
        # self.data: Dict[str, dict] = {}
        self.generator = self.get_notification_generator()

    async def get_notification_generator(self):
        while True:
            try:
                param = yield
                if param is not None:
                    await self._notify(param)
            except RuntimeError as e:
                print(e)
                
    async def push(self, data: dict):
        await self.generator.asend(data)

    async def connect(self, websocket: WebSocket, roomId: str):
        await websocket.accept()
        self.connections.append(websocket)
        if roomId in self.connections_meta:
            self.connections_meta[roomId].append(websocket)
        else:
            self.connections_meta[roomId] = [websocket]

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def _notify(self, data: dict):
        roomId = data['roomId']
        data_ = data['data']
        conn_meta_buf = []
        if roomId in self.connections_meta:
            for websocket in self.connections_meta[roomId]:
                await websocket.send_json(data_)
                conn_meta_buf.append(websocket)
                print("OHOHOHOHH")
            self.connections_meta[roomId] = conn_meta_buf


class tossBombRoomObject(BaseModel):
    room_theme:str
    question:str

class tossBombUserObject(BaseModel):
    nickname:str

class tossBombGameObject(BaseModel):
    initQuestion:str
    currTimer:int

class tossBombGameObject2(BaseModel):
    currNickname:str
    currPosition:int
    currQuestion:str
    currAnswer:str
    currRound:int
    currTimer:int

class tossBombUserObject2(BaseModel):
    nickname:str
    status:str
    position:int

class tossBombUserObject2Bulk(BaseModel):
    bulk: list[tossBombUserObject2]

class tossBombAnswerObject(BaseModel):
    question:str
    answer:str

class tossBombQuestionObject(BaseModel):
    question:str
    past_question:str

class tossBombQAObject(BaseModel):
    targetNickname:str
    pastQuestion:str
    pastAnswer:str
    questionPrompt:str


## for API User Basic ##

class CreateUser(BaseModel):
    email:str
    username:str
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class User(BaseModel):
    username: str
    email: str = None
    disabled: bool = None

class UserInDB(User):
    hashed_password: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    db = load_db_to_df(True, 'user', [])
    db = db[db['username']==username]
    if len(db) > 0:
        return UserInDB(username=db.loc[0, 'username'], email=db.loc[0, 'email'], hashed_password=db.loc[0, 'hashed_password'])

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


### API Routes ###
@api.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api.post("/user/create")
async def create_new_user(create_user: CreateUser, current_user: User = Depends(get_current_active_user)):
    df = pd.DataFrame()
    df['username'] = [create_user.username]
    df['email'] = [create_user.email]
    df['hashed_password'] = [get_password_hash(create_user.password)]
    insert_df_to_db(True, "user", df)
    return {"username":create_user.username, "email":create_user.email}

@api.post("/createRoom/{roomId}/{roomMaxCnt}/{gameOverTimer}")
async def createRoom(roomId:str, roomMaxCnt:int, gameOverTimer:int, tossBombRoomObject:tossBombRoomObject, current_user: User = Depends(get_current_active_user)):
    result = await create_room(similarity_model, roomId, roomMaxCnt, gameOverTimer, tossBombRoomObject.room_theme, tossBombRoomObject.question)
    return result

@api.post("/registerUser/{roomId}/{hostCheck}")
async def registerUser(roomId:str, tossBombUserObject:tossBombUserObject, hostCheck:bool, current_user: User = Depends(get_current_active_user)):
    result = await register_user(roomId, tossBombUserObject.nickname, hostCheck)
    return result

@api.get("/gameStart/{roomId}/{hostCheck}")
async def gameStart(roomId:str, hostCheck:bool, current_user: User = Depends(get_current_active_user)):
    result = await game_start(roomId, hostCheck)
    return result

@api.post("/createGameDataInfo/{roomId}")
async def createGameDataInfo(roomId:str, tossBombGameObject:tossBombGameObject, current_user: User = Depends(get_current_active_user)):
    result = await create_game_data_info(roomId, tossBombGameObject.initQuestion, tossBombGameObject.currTimer)
    return result


notifierGameReady = Notifier()
notifierGameProgress = Notifier()


@api.on_event("startup")
async def startup():
    # Prime the push notification generator
    await notifierGameReady.generator.asend(None)
    await notifierGameProgress.generator.asend(None)


@api.get("/gameReadyResult/{roomId}")
async def gameReadyResult(roomId:str):
    result = await room_user_info(roomId)
    print(result)
    await notifierGameReady.push({"roomId":roomId, "data":result})
    '''try:
        await notifierGameReady.push({"roomId":roomId, "data":result})
    except:
        pass'''


@api.post("/gameProgressResult/{roomId}")
async def gameProgressResult(roomId:str, tossBombGameObject2:tossBombGameObject2):
    currNickname = tossBombGameObject2.currNickname
    currPosition = tossBombGameObject2.currPosition
    currQuestion = tossBombGameObject2.currQuestion
    currAnswer = tossBombGameObject2.currAnswer
    currRound = tossBombGameObject2.currRound
    currTimer = tossBombGameObject2.currTimer


    result = await update_game_data_info(roomId, currNickname, currPosition, currQuestion, currAnswer, currRound, currTimer)
    result_1 = await room_user_info(roomId)
    result_2 = await get_game_data_info(roomId)
    result["object"] = {
        "frontData":result_2["object"],
        "frontUserData":result_1["object"]
    }
    print(result)
    try:
        await notifierGameProgress.push({"roomId":roomId, "data":result})
    except:
        pass

@api.websocket("/ws/gameReady/{roomId}")
async def gameReady(websocket:WebSocket, roomId:str):
    await notifierGameReady.connect(websocket, roomId)
    
    try:
        while True:
            clientData = await websocket.receive_json()
            roomId = str(clientData['roomId'])
            print(websocket.client, roomId)
            result = await room_user_info(roomId)
            await websocket.send_json(result)

    except WebSocketDisconnect:
        try:
            notifierGameReady.remove(websocket)
        except:
            pass
        finally:
            notifierGameReady.connect(websocket, roomId)


### websocket need ###
@api.websocket("/ws/gameProgress/{roomId}")
async def gameProgress(websocket:WebSocket, roomId:str):
    await notifierGameProgress.connect(websocket, roomId)
    try:
        while True:
            clientData = await websocket.receive_json()
            print(websocket.client)
            roomId = str(clientData['roomId'])
            currNickname = str(clientData['currNickname'])
            currPosition = int(clientData['currPosition'])
            currQuestion = str(clientData['currQuestion'])
            currAnswer = str(clientData['currAnswer'])
            currRound = int(clientData['currRound'])
            currTimer = int(clientData['currTimer'])

            result = await room_user_info(roomId)
            result_2 = await get_game_data_info(roomId)
            result_3 = await update_game_data_info(roomId, currNickname, currPosition, currQuestion, currAnswer, currRound, currTimer)
            result["object"] = {
                "frontData":result_2["object"],
                "frontUserData":result["object"]
            }
            await websocket.send_json(result)
    except WebSocketDisconnect:
        try:
            notifierGameProgress.remove(websocket)
        except:
            pass
        finally:
            notifierGameProgress.connect(websocket, roomId)

@api.get("/roomUserInfo/{roomId}")
async def roomUserInfo(roomId:str, current_user: User = Depends(get_current_active_user)):
    result = await room_user_info(roomId)
    return result

@api.get("/getGameDataInfo/{roomId}")
async def getGameDataInfo(roomId:str, current_user: User = Depends(get_current_active_user)):
    result = await get_game_data_info(roomId)
    return result

@api.post("/updateGameDataInfo/{roomId}")
async def updateGameDataInfo(roomId:str, tossBombGameObject2:tossBombGameObject2, current_user: User = Depends(get_current_active_user)):
    result = await update_game_data_info(roomId, tossBombGameObject2.currNickname, tossBombGameObject2.currPosition, tossBombGameObject2.currQuestion, tossBombGameObject2.currAnswer, tossBombGameObject2.currRound, tossBombGameObject2.currTimer)
    return result


@api.post("/gameUserUpdate/{roomId}")
async def gameUserUpdate(roomId:str, tossBombUserObject2Bulk:tossBombUserObject2Bulk, current_user: User = Depends(get_current_active_user)):
    for item in tossBombUserObject2Bulk.bulk:
        result = await game_user_update(roomId, item.nickname, item.status, item.position)
    return result


@api.post("/gameAnswerCheck/{roomId}")
async def gameAnswerCheck(roomId:str, tossBombAnswerObject:tossBombAnswerObject, current_user: User = Depends(get_current_active_user)):
    result = await answer_check(similarity_model, roomId, tossBombAnswerObject.question, tossBombAnswerObject.answer)
    return result

@api.post("/gameQuestionCheck/{roomId}")
async def gameQuestionCheck(roomId:str, tossBombQuestionObject:tossBombQuestionObject, current_user: User = Depends(get_current_active_user)):
    result = await question_check(similarity_model, roomId, tossBombQuestionObject.past_question, tossBombQuestionObject.question)
    return result

@api.post("/generateQuestion/{roomId}")
async def generateQuestion(roomId:str, tossBombQAObject:tossBombQAObject, current_user: User = Depends(get_current_active_user)):
    result = await generate_question(similarity_model, tossBombQAObject.targetNickname, roomId, tossBombQAObject.pastQuestion, tossBombQAObject.pastAnswer, tossBombQAObject.questionPrompt)
    return result


### Render ERP Page ###
@api.get("/", response_class=HTMLResponse)
async def index():
    return "bomb api"


if __name__ == "__main__":
    port = sys.argv[1]
    uvicorn.run(api, host="0.0.0.0", port=port)