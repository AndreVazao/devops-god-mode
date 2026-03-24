from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="DevOps God Mode")

@app.get("/")
def root():
    return {"status": "DevOps God Mode backend alive"}

app.include_router(router)
