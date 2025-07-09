from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List,  Dict, Any
from decimal import Decimal

class ProjectBase(BaseModel):
    projectid: str
    projectname: str
    country_code: str
    location: Optional[str] = None
    startdate: datetime
    endate: Optional[datetime] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    class Config:
        from_attributes = True

class ProjectCombo(ProjectBase):
    projectid: str
    projectname: str

class AssetDSBase(BaseModel):
    assettype: str
    assetdesc: str
    projectid: str
    farmname: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    meas_campaign_period: Optional[Decimal] = None
    projection: Optional[str] = None
    timezone: Optional[str] = None
    startdate: datetime
    enddate: datetime
    interval: Optional[int] = None
    interval_label: Optional[str] = None
    simulateddate: Optional[datetime] = None
    simulatedby: Optional[str] = None
    reviewedby: Optional[str] = None
    simulationdetails: Optional[Dict[str, Any]]  # Add this line
    createdby: Optional[str] = None
    createddate: Optional[datetime] = None
    modifiedby: Optional[str] = None
    modifieddate: Optional[datetime] = None
    deltapath: Optional[str] = None

class AssetDSCreate(AssetDSBase):
    pass

class AssetDS(AssetDSBase):
    assetid: int
    project_info: Optional[Project] = None

    class Config:
        from_attributes = True

class AssetDataResponse(BaseModel):
    asset: AssetDS
    data: Optional[dict] = None  # For time series data from ADLS Gen2 


class AssetWindResponse(BaseModel):
    data_file_url: str
    assetid: int
    assettype: str
    assetdesc: str
    projectid: str
    farmname: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    meas_campaign_period: Optional[Decimal] = None
    projection: Optional[str] = None
    timezone: Optional[str] = None
    startdate: datetime
    enddate: datetime
    interval: Optional[int] = None
    interval_label: Optional[str] = None
    simulateddate: Optional[datetime] = None
    simulatedby: Optional[str] = None
    reviewedby: Optional[str] = None
    simulationdetails: Optional[Dict[str, Any]] = None
    createdby: Optional[str] = None
    createddate: Optional[datetime] = None
    modifiedby: Optional[str] = None
    modifieddate: Optional[datetime] = None
    deltapath: Optional[str] = None
    # Project fields (prefixed)
    project_projectid: Optional[str] = None
    project_projectname: Optional[str] = None
    project_country_code: Optional[str] = None
    project_location: Optional[str] = None
    project_startdate: Optional[datetime] = None
    project_endate: Optional[datetime] = None

class AssetSolarResponse(AssetWindResponse):
    # Inherits all fields; can be extended if solar-specific fields are needed
    pass


class AssetWindResponseSimple(BaseModel):
    projectid: str
    unique_desc: str
    farmname: str
    turbine_type: str
    installed_capcity: float
    meas_period: float
    projectname: str
    country_code: str
    location: str

class AssetSolarResponseSimple(BaseModel):
    projectid: str
    unique_desc: str
    farmname: str
    pv_make: str
    pv_model: str
    installed_capacity_ac: float
    dc_ac_ratio: float
    meas_period: float
    projectname: str
    country_code: str
    location: str




