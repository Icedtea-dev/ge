
import great_expectations as gx
from great_expectations.core.batch import BatchRequest, RuntimeBatchRequest
from build_expectations import build_expectations_for_data_assets,get_src_dtypes_from_postgres,load_json,dump_json
from eprocurement_tables import eproc_tables,process

context = gx.get_context()

dataset_id = 'deep-contact-361614'
datasource_name = "BigQuery_datasource"

available_data_asset_names = context.datasources[datasource_name].get_available_data_asset_names(
    data_connector_names="default_inferred_data_connector_name")["default_inferred_data_connector_name"]

# print(len(available_data_asset_names))

path = "./test_schema.json"
existing_schema = load_json(path=path)
run_time_schema = get_src_dtypes_from_postgres("public",eproc_tables,"DB")
rebuild_expectations = False

try:
    # assert existing_schema == run_time_schema
    assert existing_schema == "hey"
except Exception as e:
    dump_json(path,run_time_schema)
    rebuild_expectations = True
    print(f"Schema Evolution")


def checkpoint_run(validator):
    checkpoint = gx.checkpoint.SimpleCheckpoint(
    name="big_query_checkpoint",
    data_context=context,
    validator=validator,
    )
    checkpoint.run()

def checkpoint_run_using_expectations(batch_request,validation):
    checkpoint = gx.checkpoint.SimpleCheckpoint(
    name="big_query_checkpoint",
    data_context=context,
    validations=[
    {
        "batch_request": batch_request,
        "expectation_suite_name": validation,
    },
    ],)
    checkpoint.run()  
    

for dataset in available_data_asset_names:
    tbl_name = dataset.split(".")[-1]
    schema_name = dataset.split(".")[0]
    rebuild_specific_tbl_expectations = True
    if  tbl_name not in tuple(run_time_schema.keys()):continue #e.g tbl_product_price_trends_deduplicated
    # if  not tbl_name  in ["tbl_product"]: continue

    if rebuild_expectations:
        if existing_schema.get(tbl_name) != run_time_schema.get(tbl_name):
            rebuild_specific_tbl_expectations = True 
            print(f"Rebuild expectations for table: {tbl_name}: {rebuild_specific_tbl_expectations}")

    if tbl_name == "tbl_product": 
        print(f"Running runtime batch request for table {tbl_name}")
        runtime_parameters={"query": f"select *, trim(lower(name)) parsed_name from {dataset} where deleted_at is null"}
        run_time_batch_request = RuntimeBatchRequest(
            datasource_name=datasource_name,
            data_connector_name="default_runtime_data_connector_name",
            data_asset_name=dataset,
            runtime_parameters=runtime_parameters,
            batch_identifiers={"default_identifier_name": "runtime_product_data"},
            batch_spec_passthrough={}
        )

        if  rebuild_specific_tbl_expectations:
            context.add_or_update_expectation_suite(expectation_suite_name=f"eproc_bq_expec_{tbl_name}_runtime")
            validator_runtime = context.get_validator(
                batch_request=run_time_batch_request, expectation_suite_name=f"eproc_bq_expec_{tbl_name}_runtime"
                )
            build_expectations_for_data_assets(tbl_name, validator_runtime,run_time_schema.get(tbl_name),runtime=True)
            validator_runtime.save_expectation_suite(discard_failed_expectations=False)
            checkpoint_run(validator_runtime)
        else:
            checkpoint_run_using_expectations(batch_request,f"eproc_bq_expec_{tbl_name}_runtime")

    print(f"Running batch request for table {tbl_name}")
    batch_request = BatchRequest(
        datasource_name=datasource_name,
        data_connector_name="default_inferred_data_connector_name",
        data_asset_name=dataset, 
        batch_spec_passthrough={
            "name": "batch_request_for_tbl"
        }
    )

    if  rebuild_specific_tbl_expectations:
        context.add_or_update_expectation_suite(expectation_suite_name=f"eproc_bq_expec_{tbl_name}")
        validator = context.get_validator(
            batch_request=batch_request, expectation_suite_name=f"eproc_bq_expec_{tbl_name}"
            )
        build_expectations_for_data_assets(tbl_name, validator,run_time_schema.get(tbl_name))
        validator.save_expectation_suite(discard_failed_expectations=False)
        checkpoint_run(validator)

    else:
        checkpoint_run_using_expectations(batch_request,f"eproc_bq_expec_{tbl_name}")


# if rebuild_expectations:
#     checkpoint_run(validator)

context.build_data_docs()