from eprocurement_tables import replace_list
from build_expectations import build_expectations_for_data_assets
import yaml

temp_schema = {"id":"INTEGER","tag":"STRING","create":"STRING"}

# build_expectations_for_data_assets("eproc.tbl_purchase_order","xx",temp_schema)

print(list(replace_list.keys()))

