
import great_expectations as gx
from great_expectations.core.batch import BatchRequest, RuntimeBatchRequest
from build_expectations import build_expectations_for_data_assets,get_src_dtypes_from_postgres,load_json,dump_json
from eprocurement_tables import eproc_tables,process

context = gx.get_context()

dataset_id = 'deep-contact-361614'

datasource_name = "BigQuery_datasource"

available_data_asset_names = context.datasources[datasource_name].get_available_data_asset_names(
    data_connector_names="default_inferred_data_connector_name")["default_inferred_data_connector_name"]

print(available_data_asset_names)
