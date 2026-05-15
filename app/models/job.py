from datetime import datetime
from app.extensions import db

VALID_STATUSES = {"applied", "interview", "offer", "rejected", "withdrawn"}


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), default="applied")
    job_description = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(150), nullable=True)
    salary = db.Column(db.String(100), nullable=True)
    applied_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "role": self.role,
            "status": self.status,
            "job_description": self.job_description,
            "notes": self.notes,
            "location": self.location,
            "salary": self.salary,
            "applied_date": self.applied_date.isoformat() if self.applied_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
