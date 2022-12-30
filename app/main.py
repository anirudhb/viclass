from typing import Union
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.datastructures import URL


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

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
    return templates.TemplateResponse("video.html", {"request": request, "video_title": video_title, "profname": profname, "url": url})
    


if __name__ == "__main__":
    uvicorn.run("fastapi_code:app")