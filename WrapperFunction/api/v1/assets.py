from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
from WrapperFunction.db.session import get_db
from sqlalchemy.orm import Session
import json
import pandas as pd
import io
from WrapperFunction.core.config import settings
import zipfile


router = APIRouter()

from WrapperFunction.services.project_service import ProjectService
from WrapperFunction.services.asset_service import AssetService
from WrapperFunction.utils.util import to_dict

from WrapperFunction.schemas.schemas import (
    Project,
    ProjectCreate,
    AssetDS,
    AssetDSCreate,
    AssetDataResponse,
    ProjectCombo,
    AssetWindResponse,
    AssetSolarResponse
)

project_service = ProjectService()
asset_service = AssetService()

@router.get("/projects/", response_model=List[ProjectCombo])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = project_service.get_projects(db, skip, limit)
    return projects

@router.get("/assets/{asset_id}", response_model=AssetDS)
def read_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = asset_service.get_asset_by_id(db, asset_id)
    if hasattr(asset, "simulationdetails") and isinstance(asset.simulationdetails, str):
        try:
            asset.simulationdetails = json.loads(asset.simulationdetails)
        except Exception:
            asset.simulationdetails = {}
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.get("/data/{asset_id}", response_description="Download zipped data")
def get_assets_data(
    asset_id: int,
    db: Session = Depends(get_db)
):
    """
    Returns a ZIP file containing CSV data for the asset. StreamingResponse, not validated by response_model.
    """
    asset, result = asset_service.get_asset_with_data(db, asset_id)
    
    if result is None or result.get("data") is None:
        raise HTTPException(status_code=404, detail="Asset or data not found")
    
    
    df = pd.DataFrame(result["data"])
    
    if asset.assettype == "Solar":
        df = df[['datetimekey','ncf_dc','ncf_ac']]
    else:
        df = df[['datetimekey [local_time]','ncf']]
        df.rename(columns={'datetimekey [local_time]':'datetimekey'},inplace=True)
        
    df['year'] = df.datetimekey.dt.year
    df['hour_of_the_year'] = ((df["datetimekey"] - df["datetimekey"].dt.normalize().dt.year.map(lambda y: pd.Timestamp(f"{y}-01-01")))\
            .dt.total_seconds() // 3600 + 1).astype(int)
        
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = io.BytesIO(csv_buffer.getvalue().encode('utf-8'))
    filename = f"Asset_Generation_{asset.assetdesc}"
    zip_filename = f"Asset_Generation_{asset.assetid}_data"
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f"{zip_filename}.csv", csv_bytes.getvalue())

    zip_buffer.seek(0)  # Reset pointer

    # Return as streaming response
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={filename}.zip"}
    )


@router.get("/wind", response_model=List[AssetWindResponse])
def get_assets_wind(
    project: Optional[str] = Query(None, description="Project ID"),
    unique_desc: Optional[str] = Query(None, description="Unique Description"),
    farmname: Optional[str] = Query(None, description="Farm Name"),
    turbine_type: Optional[str] = Query(None, description="Turbine Type"),
    installed_capcity: Optional[float] = Query(None, description="Installed Capacity"),
    meas_period: Optional[float] = Query(None, description="Measuring Campaign Length"),
    db: Session = Depends(get_db)
):
    assets = asset_service.get_assets_by_filter_wind(db, project, 'Wind',unique_desc, farmname, turbine_type, installed_capcity, meas_period)
    result = []
    for asset,project in assets:
        
        if hasattr(asset, "simulationdetails") and isinstance(asset.simulationdetails, str):
            try:
                asset.simulationdetails = json.loads(asset.simulationdetails)
            except Exception:
                asset.simulationdetails = {}
        asset_dict = to_dict(asset)
        project_dict = to_dict(project)
        # Optionally, prefix project fields to avoid key collisions
        HOST = settings.HOST
        asset_url = f"{HOST}/api/v1/assets/data/{asset.assetid}"
        combined = {"data_file_url":asset_url,**{**asset_dict, **{"project_" + k: v for k, v in project_dict.items()}}}
        result.append(combined)
    if not assets:
        raise HTTPException(status_code=404, detail="No assets found for this project")
    
    return result


@router.get("/solar", response_model=List[AssetSolarResponse])
def get_assets_solar(
    project: Optional[str] = Query(None, description="Project ID"),
    unique_desc: Optional[str] = Query(None, description="Unique Description"),
    farmname: Optional[str] = Query(None, description="Farm Name"),
    pv_make: Optional[str] = Query(None, description="PV Make"),
    pv_model: Optional[float] = Query(None, description="PV Model"),
    installed_capacity_ac: Optional[float] = Query(None, description="Installed Capacity AC"),
    dc_ac_ratio: Optional[float] = Query(None, description="DC:AC Ratio"),
    meas_period: Optional[float] = Query(None, description="Measuring Campaign Length"),
    db: Session = Depends(get_db)
):
    assets = asset_service.get_assets_by_filter_solar(db, project, 'Solar',unique_desc, farmname, pv_make, pv_model, installed_capacity_ac, dc_ac_ratio, meas_period)
    result = []
    for asset,project in assets:
        if hasattr(asset, "simulationdetails") and isinstance(asset.simulationdetails, str):
            try:
                asset.simulationdetails = json.loads(asset.simulationdetails)
            except Exception:
                asset.simulationdetails = {}
        asset_dict = to_dict(asset)
        project_dict = to_dict(project)
        # Optionally, prefix project fields to avoid key collisions
        HOST = settings.HOST
        asset_url = f"{HOST}/api/v1/assets/data/{asset.assetid}"
        combined = {"data_file_url":asset_url,**{**asset_dict, **{"project_" + k: v for k, v in project_dict.items()}}}
        result.append(combined)
    if not assets:
        raise HTTPException(status_code=404, detail="No assets found for this project")
    
    return result