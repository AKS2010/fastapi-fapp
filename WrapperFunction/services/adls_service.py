from deltalake import DeltaTable
import duckdb
from WrapperFunction.core.config import settings

class DeltaLakeService:
    def __init__(self):
        # Initialize ADLS Gen2 client
        self.ADLS_STORAGE_ACCOUNT = settings.ADLS_STORAGE_ACCOUNT
        self.ADLS_STORAGE_KEY = settings.ADLS_STORAGE_KEY
        self.ADLS_CONTAINER = settings.ADLS_CONTAINER

    def read_delta_table_from_adls(self, delta_table_path, asset_id):
            # Construct the abfss path
            
            abfss_path = f"abfss://{self.ADLS_CONTAINER}@{self.ADLS_STORAGE_ACCOUNT}.dfs.core.windows.net/{delta_table_path}"

            # Set up Azure credentials for delta-rs
            storage_options = {
                "account_name": self.ADLS_STORAGE_ACCOUNT,
                "account_key": self.ADLS_STORAGE_KEY,
            }

            # Read the Delta table
            dt = DeltaTable(abfss_path, storage_options=storage_options)
            conn = duckdb.connect()
            dt = dt.to_pyarrow_dataset()
            conn.register("duck_data", dt)
            df = conn.query(f"SELECT * FROM duck_data where assetid = {asset_id} order by datetimekey").to_df()
            conn.close()        
            return df