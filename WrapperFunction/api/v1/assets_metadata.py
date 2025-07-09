from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, UploadFile, File, Form
from typing import List, Optional
from WrapperFunction.db.session import get_db
from sqlalchemy.orm import Session
import json
from WrapperFunction.schemas.schemas import (
    AssetWindResponseSimple,
    AssetSolarResponseSimple
)

router = APIRouter()

from WrapperFunction.services.project_service import ProjectService
from WrapperFunction.services.asset_service import AssetService
from WrapperFunction.utils.util import to_dict

from WrapperFunction.schemas.schemas import (
    AssetDS,
)

project_service = ProjectService()
asset_service = AssetService()


@router.get("/wind", response_model=List[AssetWindResponseSimple])
def get_asset_metadata(db: Session = Depends(get_db)):
    result = asset_service.get_asset_filter_unique_values("Wind",db)
    return result

@router.get("/solar", response_model=List[AssetSolarResponseSimple])
def get_asset_metadata(db: Session = Depends(get_db)):
    result = asset_service.get_asset_filter_unique_values("Solar",db)
    return result