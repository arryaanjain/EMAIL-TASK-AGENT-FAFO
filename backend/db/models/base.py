from datetime import datetime
from .. import db

class BaseModel(db.Model):
    """Abstract base model with common fields"""
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        """Save model instance to database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete model instance from database"""
        db.session.delete(self)
        db.session.commit()