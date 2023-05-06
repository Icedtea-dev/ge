import psycopg2
import re
import configparser
import json
from collections import defaultdict
from eprocurement_tables import replace_list

config = configparser.ConfigParser()
config.read('./config.cfg')

def build_expectations_for_data_assets(tbl_name,validator,schema_info, runtime=False):
    #Working on the product table
    if tbl_name == "tbl_product" and runtime == True:
        validator.expect_column_values_to_be_unique(column='parsed_name',mostly=1.0)
        validator.expect_column_values_to_not_be_null("parsed_name")
        return 
    
    # 1. Unique columns
    if 'id' in validator.columns():
        validator.expect_column_values_to_be_unique(column='id', mostly=1.0)

    #2. Matching data types
    if len(schema_info)> 0:
        # print(f"Table name: {tbl_name} \n schema_info: {schema_info}")
        if tbl_name in replace_list:
            temp_schema = replace_list.get(tbl_name)
            schema_info = {temp_schema.get(k,k):v for k,v in schema_info.items()}
        else:
            print(f"Not in schema: table {tbl_name}")

        for col_name,col_type in schema_info.items():
            try:
                validator.expect_column_values_to_be_of_type(column=col_name,type_=col_type)
            except Exception as e:
                print(e)

        # 3.Tables in the data warehouse should have the same number of columns as their 
        # corresponding tables in the database to ensure consistency.
        validator.expect_table_columns_to_match_set(list(schema_info.keys()),exact_match =True)


def create_conn(conn_name):
    try:
        connection_to_use = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config[conn_name].values(),connect_timeout=10))
        cursor_to_use = connection_to_use.cursor()
    except Exception as e:
        print("Cannot connect to the DB")
        print(e)
        raise Exception
    else:
        print("Connected to the DB Succesfully!!")
        return connection_to_use,cursor_to_use
    

# Dtype compilations
int_m = re.compile("int")
str_m = re.compile("character|text|uuid|jsonb")
bool_m = re.compile("boolean")
float_m = re.compile("numeric")
date_m = re.compile("timestamp")


def regex_m(input_str):
    if int_m.search(input_str):
        return "INTEGER"
    elif str_m.search(input_str):
        return("STRING")
    elif bool_m.search(input_str):
        return("BOOLEAN")
    elif float_m.search(input_str):
        return("FLOAT")
    elif date_m.search(input_str):
        return("DATETIME")
    else:
        return("STRING")


def dump_json(path,file):
    with open(path,"w") as f:
        json.dump(file,f)
    print("Done !!!")

def load_json(path):
    with open(path,"r") as f:  
        return json.load(f)


# dump_json("./src_dtypes.json",get_src_dtypes_from_postgres("public",None,"DB",True))

def get_src_dtypes_from_postgres(schema_name,tbl_name,db_conn_name):
    if type(tbl_name) ==str:
        tbl_name = (tbl_name,)
    elif type(tbl_name) ==list:
        tbl_name = tuple(tbl_name)

    connection_to_use,cursor_to_use = create_conn(db_conn_name)
    sql = f"""SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = '{schema_name}'
    AND table_name  in  %s
    """
    cursor_to_use.execute(sql,(tbl_name,))
    result = cursor_to_use.fetchall()

    schema_dict = defaultdict(dict)
    tmp = [schema_dict[x[0]].update({x[1]:regex_m(x[2])}) for x in result] 
    
    connection_to_use.close()
    return schema_dict


                