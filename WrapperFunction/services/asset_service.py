from sqlalchemy.orm import Session
from fastapi import HTTPException
from WrapperFunction.db.models import Project, AssetDS
from sqlalchemy import text
import os
import logging

from WrapperFunction.services.adls_service import DeltaLakeService
from WrapperFunction.utils.util import to_dict
import json

dl_service = DeltaLakeService()
# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler()  # Keep this if you also want logs in the console
    ]
)

logger = logging.getLogger(__name__)

class AssetService:
    def __init__(self):
        # Initialize ADLS Gen2 client
        self.CONSTANT = 1
        

    def get_asset_by_id(self, db: Session, asset_id: int):
        return db.query(AssetDS).filter(AssetDS.assetid == asset_id).first()
    
    def get_asset_filter_unique_values(self,type : str ,  db: Session):
        query = db.query(AssetDS, Project).join(Project, AssetDS.projectid == Project.projectid)
        query = query.filter(AssetDS.assettype == type)
        assets =  query.all()
        seen = set()
        result = []
        for asset, project in assets:
            if asset is None:
                continue
            asset_dict = to_dict(asset)
            sim_details = asset_dict.pop("simulationdetails", None)
            if sim_details and isinstance(sim_details, str):
                try:
                    sim_details = json.loads(sim_details)
                except Exception:
                    sim_details = {}
            if not isinstance(sim_details, dict):
                sim_details = {}

            filtered_project = {
                    "projectname": project.projectname,
                    "country_code": project.country_code,
                    "location": project.location
                }
            
            if type == "Wind":
            # Only select specific fields
                filtered_asset = {
                    "projectid":asset_dict.get("projectid"),
                    "unique_desc": asset_dict.get("assetdesc"),
                    "farmname": asset_dict.get("farmname"),
                    "turbine_type":sim_details.get("WTG model"),
                    "installed_capcity":sim_details.get("Installed capacity"),
                    "meas_period":asset_dict.get("meas_campaign_period")
                }
                combined = {**filtered_asset, **filtered_project}
                # Ensure uniqueness (e.g., by assetid + projectid)
                unique_key = (combined["unique_desc"], combined["projectid"],combined["country_code"],combined["location"], combined["farmname"], combined["turbine_type"], combined["installed_capcity"], combined["meas_period"])
            elif type == "Solar":
                filtered_asset = {
                    "projectid":asset_dict.get("projectid"),
                    "unique_desc": asset_dict.get("assetdesc"),
                    "farmname": asset_dict.get("farmname"),
                    "pv_make":sim_details.get("PV Module Make & Model"),
                    "pv_model":sim_details.get("PV Module Model"),
                    "installed_capacity_ac":sim_details.get("AC Capacity (MW)"),
                    "dc_ac_ratio":sim_details.get("DC:AC Ratio"),
                    "meas_period":asset_dict.get("meas_campaign_period")
                }

                combined = {**filtered_asset, **filtered_project}
                # Ensure uniqueness (e.g., by assetid + projectid)
                unique_key = (combined["unique_desc"], combined["projectid"],combined["country_code"],combined["location"], combined["farmname"], combined["pv_make"], combined["pv_model"], combined["installed_capacity_ac"], combined["dc_ac_ratio"], combined["meas_period"])
            if unique_key not in seen:
                seen.add(unique_key)
                result.append(combined)

        if not result:
            raise HTTPException(status_code=404, detail="Asset not found")
        return result

    def get_asset_filter_unique_solar(self, db: Session):
        query = db.query(AssetDS, Project).join(Project, AssetDS.projectid == Project.projectid)
        query = query.filter(AssetDS.assettype == 'Solar')
        return query.all()

    def get_assets_by_filter_wind(self, db, project_id, asset_type=None, unique_desc=None, farmname=None, turbine_type=None, installed_capcity=None, meas_period=None):
        query = db.query(AssetDS, Project).join(Project, AssetDS.projectid == Project.projectid)
        if project_id is not None:
            query = query.filter(AssetDS.projectid == project_id)
        if asset_type is not None:
            query = query.filter(AssetDS.assettype == asset_type)
        if farmname is not None:
            query = query.filter(AssetDS.farmname == farmname)
        if unique_desc is not None:
            query = query.filter(AssetDS.assetdesc == unique_desc)
        if meas_period is not None:
            query = query.filter(text("TRY_CAST(meas_campaign_period AS FLOAT) = :meas_period")).params(meas_period=meas_period)
        if turbine_type is not None:
            query = query.filter(text("JSON_VALUE(simulationdetails, '$.\"WTG model\"') = :turbine_type")).params(turbine_type=turbine_type)
        if installed_capcity is not None:
            query = query.filter(text("TRY_CAST(JSON_VALUE(simulationdetails, '$.\"Installed capacity\"') AS FLOAT) = :installed_capcity")).params(installed_capcity=installed_capcity)
        return query.all()
    
    
    def get_assets_by_filter_solar(self, db, project_id, asset_type=None, unique_desc=None, farmname=None, pv_make=None, pv_model=None, installed_capacity_ac=None, dc_ac_ratio=None , meas_period=None):
        query = db.query(AssetDS, Project).join(Project, AssetDS.projectid == Project.projectid)
        if project_id is not None:
            query = query.filter(AssetDS.projectid == project_id)
        if farmname is not None:
            query = query.filter(AssetDS.farmname == farmname)
        if unique_desc is not None:
            query = query.filter(AssetDS.assetdesc == unique_desc)
        if meas_period is not None:
            query = query.filter(text("TRY_CAST(meas_campaign_period AS FLOAT) = :meas_period")).params(meas_period=meas_period)
        if pv_make is not None:
            query = query.filter(text("JSON_VALUE(simulationdetails, '$.\"PV Module Make & Model\"') = :turbine_type")).params(pv_make=pv_make)
        if pv_model is not None:
            query = query.filter(text("JSON_VALUE(simulationdetails, '$.\"PV Module Make & Model\"') AS FLOAT) = :pv_model")).params(pv_model=pv_model)
        if installed_capacity_ac is not None:
            query = query.filter(text("TRY_CAST(JSON_VALUE(simulationdetails, '$.\"AC Capacity (MW)\"') AS FLOAT) = :installed_capacity_ac")).params(installed_capacity_ac=installed_capacity_ac)
        if dc_ac_ratio is not None:
            query = query.filter(text("TRY_CAST(JSON_VALUE(simulationdetails, '$.\"DC:AC Ratio\"') AS FLOAT) = :dc_ac_ratio")).params(dc_ac_ratio=dc_ac_ratio)
        return query.all()
    
    def get_asset_with_data(self, db: Session, asset_id: int):
        try:
            # Get asset metadata from MS SQL
            
            logger.info(f"Fetching asset metadata for asset_id: {asset_id}")
            asset = self.get_asset_by_id(db, asset_id)
            if not asset:
                logger.warning(f"Asset not found: {asset_id}")
                return None

            # Get time series data from ADLS Gen2
            logger.info("Fetching time series data...")
            
            asset_df = dl_service.read_delta_table_from_adls(asset.deltapath, asset_id=asset.assetid )
            time_series_data = asset_df.reset_index(drop=True).to_dict(orient='records')
            logger.info(f"Successfully retrieved {len(time_series_data)} data points")
            
            return asset, {
                "asset": asset,
                "data": time_series_data
            }
        except Exception as e:
            logger.error(f"Error in get_asset_with_data: {str(e)}")
            # If ADLS Gen2 data retrieval fails, return just the metadata
            return {
                "asset": asset if 'asset' in locals() else None,
                "data": None,
                "error": str(e)
            }