from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

# Create engine using class method
engine = create_engine(Config.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

def init_db(app):
    """Initialize database"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Add database dependency to FastAPI app
    @app.on_event("startup")
    async def startup():
        Base.metadata.create_all(bind=engine)
    
    @app.on_event("shutdown")
    async def shutdown():
        SessionLocal.close_all()

# Dependency for routes
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()