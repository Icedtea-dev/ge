
import great_expectations as gx
from great_expectations.core.expectation_configuration import ExpectationConfiguration
# from great_expectations.core.batch import BatchRequest, RuntimeBatchRequest
from build_expectations import get_src_dtypes_from_postgres,build_expectations_suite
from build_expectations  import load_json,dump_json,load_yaml,dump_yaml
from eprocurement_tables import eproc_tables,process
from great_expectations.exceptions import DataContextError



context = gx.get_context()

dataset_id = 'deep-contact-361614'
datasource_name = "BigQuery_datasource"

available_data_asset_names = context.datasources[datasource_name].get_available_data_asset_names(
    data_connector_names="default_inferred_data_connector_name")["default_inferred_data_connector_name"]

print(len(available_data_asset_names))


#Checkpoint
checkpoint_dir_path = './checkpoints/Eproc_checkpoint.yml'
checkpoint_data =  load_yaml(checkpoint_dir_path)

run_time_schema = get_src_dtypes_from_postgres("public",eproc_tables,"Staging")
path  ="./DB_schema.json"
rebuild_expectations = False

try:
    load_json(path) == run_time_schema
    # assert existing_schema == "hey"
except Exception as e:
    dump_json(path,run_time_schema)
    rebuild_expectations = True
    print(f"There is a Schema Evolution")


def rebuild_or_create_expectations(rebuild,expection_name,param):
    tbl_name,tbl_schema,ExpectationConfiguration,runtime = param
    create_expec = False
    try:
        suite = context.get_expectation_suite(expectation_suite_name=expection_name)
        print(f'Loaded ExpectationSuite "{suite.expectation_suite_name}" containing {len(suite.expectations)} expectations.')
    except DataContextError:
        create_expec = True

    if  rebuild or create_expec:
        suite = context.add_or_update_expectation_suite(expectation_suite_name=expection_name)
        print(f'Created ExpectationSuite "{suite.expectation_suite_name}".')
        build_expectations_suite(tbl_name,suite,tbl_schema,ExpectationConfiguration,runtime)
        context.add_or_update_expectation_suite(expectation_suite=suite)

def check_config(checkpoint_data,connector,dataset):
    exists_checkpoint = True
    try:
        tbl_check_point = list(filter(lambda x:  x["batch_request"]["data_asset_name"]  ==  f"{dataset}" and \
            x["batch_request"]["data_connector_name"]== connector , checkpoint_data.get("validations") ))
        if not tbl_check_point: exists_checkpoint =False
    except Exception as e:
        exists_checkpoint = False
    return exists_checkpoint


for dataset in available_data_asset_names:
    tbl_name = dataset.split(".")[-1]
    schema_name = dataset.split(".")[0]

    rebuild_specific_tbl_expectations = False
    if  tbl_name not in tuple(run_time_schema.keys()):continue  #e.g tbl_product_price_trends_deduplicated
    
    # if  not tbl_name  in ["tbl_product"]: continue

#     if rebuild_expectations:
#         if existing_schema.get(tbl_name) != run_time_schema.get(tbl_name):
#             rebuild_specific_tbl_expectations = True 
#             print(f"Rebuild expectations for table: {tbl_name}: {rebuild_specific_tbl_expectations}")

    if tbl_name == "tbl_product": 
        print(f"Running runtime batch configuration for table {tbl_name}")
        if not check_config(checkpoint_data,"default_runtime_data_connector_name",dataset):
            checkpoint_json_runtime_batch ={"batch_request":
                                             {"datasource_name": "BigQuery_datasource",
                                              "data_connector_name": "default_runtime_data_connector_name",
                                              "data_asset_name": dataset,
                                              "runtime_parameters": {"query": f"select *, trim(lower(name)) parsed_name from {dataset} where deleted_at is null"},
                                              "batch_identifiers": {
                                                  "default_identifier_name": f"runtime_request_for_{tbl_name}"
                                                  }},
                                              "expectation_suite_name": f"eproc_bq_expec_{tbl_name}_runtime"
                                                }
            if not checkpoint_data['validations']: checkpoint_data['validations'] = []
            checkpoint_data['validations'].append(checkpoint_json_runtime_batch)
            dump_yaml(checkpoint_dir_path,checkpoint_data)

        param= (tbl_name,run_time_schema.get(tbl_name),ExpectationConfiguration,True)
        rebuild_or_create_expectations(rebuild_specific_tbl_expectations,f"eproc_bq_expec_{tbl_name}_runtime",param)

    print(f"Running batch request for table {tbl_name}")
    if not check_config(checkpoint_data,"default_inferred_data_connector_name",dataset): 
        checkpoint_json_batch ={"batch_request":
                                            {"datasource_name": "BigQuery_datasource",
                                            "data_connector_name": "default_inferred_data_connector_name",
                                            "data_asset_name": dataset,
                                            "batch_spec_passthrough": {
                                                "name": f"batch_request_for_{tbl_name}"
                                                }},
                                            "expectation_suite_name": f"eproc_bq_expec_{tbl_name}"
                                            }
        
        if not checkpoint_data['validations']: checkpoint_data['validations'] = []
        checkpoint_data['validations'].append(checkpoint_json_batch)
        dump_yaml(checkpoint_dir_path,checkpoint_data)

    param= (tbl_name,run_time_schema.get(tbl_name),ExpectationConfiguration,False)
    rebuild_or_create_expectations(rebuild_specific_tbl_expectations,f"eproc_bq_expec_{tbl_name}",param)


# context.build_data_docs()