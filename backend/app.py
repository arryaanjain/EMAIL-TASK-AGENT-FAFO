from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.email import router as email_router
from api.auth import router as auth_router
from api.tasks import router as tasks_router
from db import init_db

from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="Email Task Agent")

# Database initialization
init_db(app)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(email_router, prefix="/api/email", tags=["email"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)