# models/analysis.py
import datetime
import uuid
from . import db

# [1] Written with guidance from ChatGPT to match expected schema and ensure serializable output format for analysis records.
class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    # Primary key as UUID stored as string
    request_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lab_id = db.Column(db.String(20), nullable=False)
    patient_id = db.Column(db.String(11), nullable=False)  # Medicare number (11 digits)
    result = db.Column(db.String(10), nullable=False, default="pending")  # pending, covid, h5n1, healthy, failed
    urgent = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow, 
                            onupdate=datetime.datetime.utcnow)
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            'request_id': self.request_id,
            'lab_id': self.lab_id,
            'patient_id': self.patient_id,
            'result': self.result,
            'urgent': self.urgent,
            'created_at': self.created_at.isoformat() + "Z" if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + "Z" if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Analysis {self.request_id} {self.lab_id} {self.patient_id} {self.result}>'
