import uvicorn
from fastapi import FastAPI
from api.routes import router as api_router
from auth.routes import router as auth_router
import os

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)