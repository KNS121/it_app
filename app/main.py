from fastapi import FastAPI
from app.routers import (
    users, 
    subjects, 
    materials, 
    assignments, 
    submissions, 
    auth
)
from app.database import engine, Base

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(subjects.router)
app.include_router(materials.router)
app.include_router(assignments.router)
app.include_router(submissions.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)