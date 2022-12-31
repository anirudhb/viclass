from typing import Union, List
from fastapi import FastAPI, Request, Form, File, UploadFile, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.datastructures import URL
from pydantic import BaseModel


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get("/home")
def get_home(request: Request):
    return templates.TemplateResponse("homechat.html", {"request": request})

@app.get("/chat")
def get_chat(request: Request):
    return templates.TemplateResponse("chatchat.html", {"request": request})


@app.get("/api/current_user")
def get_user(request: Request):
    return request.cookies.get("X-Authorization")


class RegisterValidator(BaseModel):
    username: str

    class Config:
        orm_mode = True


@app.post("/api/register")
def register_user(user: RegisterValidator, response: Response):
    response.set_cookie(key="X-Authorization", value=user.username, httponly=True)


class SocketManager:
    def __init__(self):
        self.active_connections: List[(WebSocket, str)] = []

    async def connect(self, websocket: WebSocket, user: str):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket, user: str):
        self.active_connections.remove((websocket, user))

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            await connection[0].send_json(data)


manager = SocketManager()


@app.websocket("/api/chat")
async def chat(websocket: WebSocket):
    sender = websocket.cookies.get("X-Authorization")
    if sender:
        await manager.connect(websocket, sender)
        response = {
            "sender": sender,
            "message": "got connected"
        }
        await manager.broadcast(response)
        try:
            while True:
                data = await websocket.receive_json()
                await manager.broadcast(data)
        except WebSocketDisconnect:
            manager.disconnect(websocket, sender)
            response['message'] = "left"
            await manager.broadcast(response)



@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/create')
def create(request: Request):
    return templates.TemplateResponse("generic.html", {"request": request})


@app.get('/prof')
def profform(request: Request):
    return templates.TemplateResponse("prof.html", {"request": request})




@app.post("/submitform", response_class=RedirectResponse, status_code=302)
async def handle_form(video_title: str = Form(...), url: str = Form(...), profname: str = Form(...)):
    print(video_title)
    print(url)
    print(profname)
    return '/video/'+profname+"/"+video_title+"/"+url

@app.get("/video/{profname}/{video_title}/{url}", response_class=HTMLResponse)
async def read_item(request: Request, profname: str,video_title: str, url: str):
    video_url = "https://www.youtube.com/embed/" + url
    print(video_url)
    return templates.TemplateResponse("video.html", {"request": request, "video_title": video_title, "profname": profname, "url": video_url})
    


if __name__ == "__main__":
    uvicorn.run("fastapi_code:app")