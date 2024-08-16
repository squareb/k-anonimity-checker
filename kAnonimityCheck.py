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

# determine input file
data_file_loc = sanitizeInput(input("Please provide the full path, including file name, of the data file that you want to assess the level of k-anonimity on (you can also drag and drop the file into this screen): "))
if(data_file_loc[-3:] == 'sav'):
    eval_data = pd.read_spss(data_file_loc)
else: 
    seperator = sanitizeInput(input("Please provide the seperator used within the file (e.g.: ; / , / \\t): "))
    eval_data = pd.read_csv(data_file_loc, sep=seperator)

# optional: exclude certain columns, f.e. the index column.
exclude_index = sanitizeInput(input("Do you want to exclude the first column (f.e. in case the first column is a simple, non-identifiable, index counter)? (y/n): "))
if exclude_index == "y":
    eval_data = eval_data[eval_data.columns[1:]]

# optional: provide sensitive columns, f.e.: ['age', 'gender'] 
sensitive_columns = []
if len(sensitive_columns) == 0:
    sensitive_columns = list(eval_data.columns.values)
    
# group the data by the sensitive columns and count the number of rows in each group
group_counts = eval_data.groupby(sensitive_columns, observed=True).size().reset_index(name='count')

# determine the minimum group size (k) for each sensitive attribute combination
min_counts = group_counts.groupby(sensitive_columns, observed=True)['count'].min().reset_index(name='min_count')

# compute the overall minimum group size (k-anonymity level) as the minimum of all the individual k values
k_anonymity_level = min_counts['min_count'].min()

# print the k-anonymity level
print('\n### Results ###')
print('> The dataset has a k-anonymity level of', k_anonymity_level)
if k_anonymity_level > 2:
    print('> Your file is eligble for export\n')
else:
    print('> Your file is not eligble for export, please apply further anonymization to ensure a k-anonimity of at least 3. You can check the generated results to see which records are below 3\n')
print(group_counts)

# print results to .csv 
filePath = re.search(r"^.*[\\\/]", data_file_loc)
filePath = filePath.group()
fileName = "%s%s" % (filePath,"k-anonimity-results.csv")

group_counts.to_csv(fileName, index=False, sep=seperator) 
print('\nResults have been exported to: ', fileName)