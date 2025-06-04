from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, email, tasks

app = FastAPI(title="Email Task Agent")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(email.router, prefix="/api/email", tags=["email"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)