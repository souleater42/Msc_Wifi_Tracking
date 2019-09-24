# -*- coding: utf-8 -*-
"""
@summary - will store the key variables used in the application.
@description - will store the key variables in the application, the
                values will be preset here and will controll how the 
                application runs. Meaning you can avoid input quries.
@author: mah60
@version - 0.1 - created config and added variables for database, and entering
                    records locations and where to save the graphs produced.
                    As well, as key variables.
         - 0.1.1 - add values to turn off showing graph in terminal and
                     and a report file and path. Used for saving, graphs. 
                     Also added comments.
                     - 05/09/2019;
"""
import os

# server details
db_username = "mah60"
db_password = "xyz925krs"
db_name = "wificounter"
db_host = "localhost"
# path for where the application is being run.
directory_path = os.path.abspath("application.py").replace("application.py","")

# ------------------------------------------------------------------------------------
# Test inport byte size
# This is done to work out a optimal value byte cut off size 
# for the insert many command. Will print out results.
# WARNING :  this may take awhile if set to True.
test_time_import_different_byte_size = False
# Do you want to import files - True = yes - False = No
is_import = True
# set parameters
import_byte_limit = 250000 # cut off byte size for insert many path
record_path = directory_path + "records\\" # folder of where records are stored
counter_records = ["recordings_7_d1.txt", "recordings_7_d2.txt"] # records file name, need to be txt files.
# start timestamp for each record. WARNING :  Must be same size as counter_records.
# WARNING : times must be formatted like "YEAR-MONTH-DAY-HOUR-MINUITE-SECOND"/"YYYY-MM-DD-HH-MM-SS"
start_date_time =  ["2019-09-09-16-54", "2019-09-09-16-55"] 
# filter for each record. WARNING :  Must be same size as counter_records.
# [ filter mac address, start filter time, end filter time] or ["None"] if no filter
# WARNING : times must be formatted like "YEAR-MONTH-DAY-HOUR-MINUITE-SECOND"/"YYYY-MM-DD-HH-MM-SS"
filters = [["None"], ["None"]] # ["0C:CB:85:25:D1:F1", "2019-09-02-19-13-00", "2019-09-02-19-18-00"]
filter_noise = 4 #  this is to plus x noise to the filter range to ensure no vital data is missed.

# ------------------------------------------------------------------------------------
# Do you want to import files - True = yes - False = No
is_graphs = True 
# Do you want each graph to be displayed in terminal
show_graphs = False
graph_save_path = directory_path + "graphs\\" # folder of where graphs are stored
rssi_distance_graph_threshold = 4 # +- rssi error rate. Will create threshold of values. 
# mac address to create distance and rssi graphs
rssi_distance_mac_address = ["0C:CB:85:25:D1:F1", "34:12:F9:20:CF:FF"]
# create graph for each dwelling time value
dwellingtime_timeout = [30, 60]

# ------------------------------------------------------------------------------------
report_save_path = directory_path + "reports\\" # folder of where reports are stored
report_save_file = "report_" # file name of report, date will be added to end of file name
                                # day_month_year.png