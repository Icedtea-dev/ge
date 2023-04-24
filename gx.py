# import great_expectations as gx

# expect_column_values_to_be_of_type

# expect_column_values_to_not_be_null 

# expect_column_values_to_be_in_type_list


# importing pandas as pd
import pandas as pd

# Creating the DataFrame
df = pd.DataFrame({'Weight': [45, 88, 56, 15, 71],
				'Name': ['Sam', 'Andrea', 'Alex', 'Robin', 'Kia'],
				'Age': [14, 25, 55, 8, 21],
                'time':["2022-03-16","2022-02-16","2022-05-16","2022-03-19","2022-03-21"]
                })

# Create the index
index_ = ['Row_1', 'Row_2', 'Row_3', 'Row_4', 'Row_5']

# Set the index
df.index = index_

# Print the DataFrame
# print(df)

# return the dtype of each column
result = df.dtypes.to_frame()

# Print the result
print(result)
