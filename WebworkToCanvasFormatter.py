#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The following is procedural code to import a webhomework formatted grade 
spreadsheet and export a canvas formatted grade spreadsheet

@author: robertdenomme
"""

import pandas as pd
import csv






#read the canvas data csv with your student info in it. Also clear out all but
#the student id columns 
df_canvas = pd.read_csv('canvas_data.csv')

df_canvas = df_canvas[df_canvas.columns[0:5]]

#remove the test student and total score row

df_canvas = df_canvas[df_canvas["Student"] != "Student, Test"]

df_canvas.drop(0, inplace = True)

"""
read the webwork data csv
so much formatting...
remove all cols but the linkblue field and the hw cols
"""

webwork_with_correct_header =[]
dumb_header_rows = []

with open('webwork_data.csv') as raw_webwork_csv:
    reader = csv.reader(raw_webwork_csv)
    for i in range(7):
        row = next(reader)
        dumb_header_rows.append(row)
    
    hw_name_row_index = 1
    student_id_row_index = 6
    student_id_col_stop = 6

    
    correct_header = dumb_header_rows[hw_name_row_index]
    
    correct_header[:student_id_col_stop] = \
        dumb_header_rows[student_id_row_index][:student_id_col_stop]
        
    webwork_with_correct_header.append(correct_header)
    for row in reader:
        webwork_with_correct_header.append(row)
        
# at this point, webwork_with_correct_header has its first row labelled
# with somewhat correct headers, and the rest of the rows are student data

# Next, expunge rows of instructors that are enrolled in more than one 
# section, since their row contains extra columns, which screws up importing 
# the data into 
# pandas
correct_col_number = len(webwork_with_correct_header[0]) 
temp_webwork = []
for row in webwork_with_correct_header:
    if len(row)==correct_col_number:
        temp_webwork.append(row)
webwork_with_correct_header = temp_webwork

linkblue_key = "SIS Login ID"
#Now, strip the header of extra whitespace
webwork_with_correct_header[0] = [header.strip() for header in \
                                  webwork_with_correct_header[0]]
#rename the login ID field (which has unknown extra whitespace in it) with 
#the same key as in the canvas df

webwork_with_correct_header[0][1]=linkblue_key
hw_column_start_index = 6
hw_column_stop_index = webwork_with_correct_header[0].index('summary')
hw_column_headers = \
    webwork_with_correct_header[0][hw_column_start_index:hw_column_stop_index]

all_webwork_headers = webwork_with_correct_header[0]
#turn the worksheet into a panda with correctly named headers!
df_webwork = pd.DataFrame(webwork_with_correct_header, 
                          columns=all_webwork_headers)

#strip the linkblue field values of extra whitespace 
df_webwork[linkblue_key] = df_webwork[linkblue_key].str.strip()

#delete all the irrelevant columns
irrelevant_columns = set(df_webwork.columns) - set(hw_column_headers+[linkblue_key])
df_webwork.drop(irrelevant_columns, axis=1, inplace=True)

"""
Done reading in/wrangling the webwork notebook (60 lines of code???)
"""



"""
Merge the hw grades over to the canvas df, then transfer into format 
for csv export, ading in the "Points Possible" row
"""

Left_join = pd.merge(df_canvas,df_webwork,
                     on=linkblue_key,
                     how='left')


hw_out_of = ["Points Possible",'','','','']+dumb_header_rows[5][hw_column_start_index:hw_column_stop_index]

export_list = [Left_join.columns.values.tolist()]+[hw_out_of]+Left_join.values.tolist()

with open('out.csv',mode = 'w') as f:
    wr = csv.writer(f, delimiter=',')
    for row in export_list:
        wr.writerow(row)
    