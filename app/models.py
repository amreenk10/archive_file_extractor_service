import os
from datetime import datetime, timezone
from app.db import db

class ExtractionLog(db.Model):
    __tablename__ ="extraction_log"
    
    id =db.Column(db.String(36),primary_key=True)
    status=db.Column(db.String(30), nullable=False, default="PENDING")
    pattern= db.Column(db.String(255),nullable=False)
    source_name=db.Column(db.String(255),nullable=False)
    submitted_at=db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(timezone.utc))
    completed_at=db.Column(db.DateTime,nullable=True)
    error_message=db.Column(db.Text,nullable=True)

    def to_dict(self):
        return {
            "job_id":self.id,
            "status":self.status,
            "pattern":self.pattern,
            "source_name":self.source_name,
            "submitted_at": self.submitted_at.isoformat(),
            "completed_at":self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error_message
        }


class ExtractedFile(db.Model):
    __tablename__= "extracted_file"

    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.String(36),db.ForeignKey("extraction_log.id",ondelete="CASCADE"), nullable=False)
    full_path=db.Column(db.Text, nullable=False)
    file_name=db.Column(db.String(255), nullable=False)
    file_size= db.Column(db.BigInteger,nullable=False)
    nesting_depth =db.Column(db.Integer,nullable=False)
    extracted_at= db.Column(db.DateTime,nullable=False,default=lambda:datetime.now(timezone.utc))
    source_archive_name = db.Column(db.String(255), nullable=True)
    extraction_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "full_path":self.full_path,
            "file_name":self.file_name,
            "file_size": self.file_size,
            "nesting_depth":self.nesting_depth,
            "extracted_at": self.extracted_at.isoformat(),
            "source_archive_name":self.source_archive_name,
            "extraction_timestamp":self.extraction_timestamp.isoformat() if self.extraction_timestamp else None
        }
