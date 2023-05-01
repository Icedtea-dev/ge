# Connect to data
# validator = context.sources.pandas_default.read_csv(
#     "test_data/tbl_product.csv"
# )
# # Create Expectations
# validator.expect_column_values_to_not_be_null("name")

# # Validate data
# checkpoint = gx.checkpoint.SimpleCheckpoint(
#     name="my_quickstart_checkpoint",
#     data_context=context,
#     validator=validator,
# )

# checkpoint_result = checkpoint.run()

# View results
# validation_result_identifier = checkpoint_result.list_validation_result_identifiers()[0]
# context.open_data_docs(resource_identifier=validation_result_identifier)


# my_connection_string = "postgresql+psycopg2://postgres:MesutOzil4$@datateam-dev-server.cdvgme4p63fk.us-east-1.rds.amazonaws.com:5432/postgres"

# datasource = context.get_datasource("postgres_datasource")
# datasource = context.get_datasource("test_postgres")
# datasource = context.sources.add_sql(name="test_postgres", connection_string=my_connection_string)
# table_asset = datasource.add_table_asset(name="tblProduct_asset", table_name="tbl_product")

