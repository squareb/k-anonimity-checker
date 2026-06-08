import pandas as pd
import os, sys, glob, datetime, csv, pathlib, re

"""
method to do various input sanitizations on user input.
"""
def sanitizeInput(string):
	# remove additional quotes
	string = string.replace("\"", "")
	# trim whitespaces around string
	string = string.strip()
	return string

seperator = ";"

print("### Lifelines k-anonymity data checker ###\nWith this tool you can verify if your files are eligble for export outside of the Lifelines Workspace. If your data file has at least a k-anonymity of 3, you are allowed to request an export. Levels below 3 are too low and require further anonymization. Follow the steps in this scripts to verify your file.\n")

# determine input file
data_file_loc = sanitizeInput(input("Please provide the full path, including file name, of the data file that you want to assess the level of k-anonymity on (you can also drag and drop the file into this screen): "))
if(data_file_loc[-3:] == 'sav'):
    eval_data = pd.read_spss(data_file_loc)
else: 
    seperator = sanitizeInput(input("Please provide the seperator used within the file (e.g.: ; / , / \\t): "))
    eval_data = pd.read_csv(data_file_loc, sep=seperator)

# optional: exclude certain columns, f.e. the index column.
exclude_index = sanitizeInput(input("Do you want to exclude the first column (f.e. in case the first column is a simple, non-identifiable, index counter)? (y/n): "))
if exclude_index.lower() == "y":
    eval_data = eval_data[eval_data.columns[1:]]

# optional: provide sensitive columns, f.e.: ['age', 'gender'] 
sensitive_columns_input = sanitizeInput(input("Please provide one or more variables that should be considered for the k-anonymity check (leave empty if you want to check all variables). For multiple variables, seperate by ,: "))
sensitive_columns = [c.strip() for c in sensitive_columns_input.split(",")]
# if no input was given, the list will contain 1 value containing an '' value. If this is the case, consider all variables.
if len(sensitive_columns) == 1 and sensitive_columns[0] == '':
	sensitive_columns = list(eval_data.columns.values)

# display the columns and their unique values to give indicator of highly unique/variable variables	
print(eval_data.nunique())

# convert all columns to strings so that the groupby function treats each column equal and considers missings (NA)
eval_data = eval_data.astype(str)

# group the data by the sensitive columns and count the number of rows in each group
group_counts = eval_data.groupby(sensitive_columns, observed=True).size().reset_index(name='count')

# compute the overall minimum group size (k-anonymity level) as the minimum of all the individual k values
k_anonymity_level = group_counts['count'].min()

# print the k-anonymity level
print('\n### Results ###')
print('> The dataset has a k-anonymity level of', k_anonymity_level)
if k_anonymity_level > 2:
    print('> Your file is eligble for export\n')
else:
    print('> Your file is not eligble for export, please apply further anonymization to ensure a k-anonymity of at least 3. You can check the generated results to see which records are below 3\n')
print(group_counts)

# print results to .csv 
filePath = re.search(r"^.*[\\\/]", data_file_loc)
filePath = filePath.group()
fileName = "%s%s" % (filePath,"k-anonymity-results.csv")

group_counts.to_csv(fileName, index=False, sep=seperator) 
print('\nResults have been exported to: ', fileName)