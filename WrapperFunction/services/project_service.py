from sqlalchemy.orm import Session
from WrapperFunction.db.models import Project, AssetDS

class ProjectService:
    def __init__(self):
        # Initialize ADLS Gen2 client
        self.CONSTANT = 1
        
    def get_projects(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Project).order_by(Project.projectid).offset(skip).limit(limit).all()
