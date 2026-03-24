from fastapi import FastAPI

app = FastAPI(title="DevOps God Mode")

@app.get("/")
def root():
    return {"status": "DevOps God Mode backend alive"}
