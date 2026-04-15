from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router


app = FastAPI(
    title="Xapien Entity Resolution Assistant",
    version="0.1.0",
    description="LLM-assisted person matching across structured profiles and news-style sources.",
)

app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
