from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from config import init_db
from routes.auth import router as auth_router
from routes.roadmap import router as roadmap_router
from dotenv import load_dotenv
from config import engine
from sqlalchemy import text

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(roadmap_router, prefix="/roadmap", tags=["Roadmap"])

@app.get("/health")
def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    return {"server": "ok", "db": db_status} 