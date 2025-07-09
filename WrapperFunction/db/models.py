from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from WrapperFunction.db.session import Base
from datetime import datetime

class Project(Base):
    __tablename__ = "projects"

    projectid = Column(String(30), primary_key=True)
    projectname = Column(String(240), nullable=False)
    country_code = Column(String(60), nullable=False)
    location = Column(String(255))
    startdate = Column(DateTime, nullable=False)
    endate = Column(DateTime)

    # Relationship with assets
    assets = relationship("AssetDS", back_populates="project_info")

class AssetDS(Base):
    __tablename__ = "asset_ds"

    assetid = Column(Integer, primary_key=True, autoincrement=False)
    assettype = Column(String(60), nullable=False)
    assetdesc = Column(String(255), nullable=False)
    projectid = Column(String(30), ForeignKey("projects.projectid"), nullable=False)
    farmname = Column(String(255))
    latitude = Column(Numeric(16, 4))
    longitude = Column(Numeric(16, 4))
    meas_campaign_period = Column(Numeric(16, 4))
    projection = Column(String(30))
    timezone = Column(String(30))
    startdate = Column(DateTime, nullable=False)
    enddate = Column(DateTime, nullable=False)
    interval = Column(Integer)
    interval_label = Column(String(30))
    simulateddate = Column(DateTime)
    simulatedby = Column(String(120))
    reviewedby = Column(String(120))
    simulationdetails = Column(Text)
    createdby = Column(String(120))
    createddate = Column(DateTime)
    modifiedby = Column(String(120))
    modifieddate = Column(DateTime)
    deltapath = Column(String(210))
    # Relationship with project
    project_info = relationship("Project", back_populates="assets") 