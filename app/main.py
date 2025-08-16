from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, tasks, users
from .core.db import init_db

app = FastAPI(title="Task Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/users", tags=["users"])

@app.on_event("startup")
def on_startup():
    init_db()
