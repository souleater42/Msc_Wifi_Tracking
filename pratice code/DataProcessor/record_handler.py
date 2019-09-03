# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 16:24:47 2019

@author: Mhowa
"""
import db_manager as dbm
import file_reader as fr
from datetime import datetime, timedelta
import hashlib 

class RecordHandler:
    """
    @summary - handles all recordings comming in from wifi counters.
    @description - will handle all incoming text files comming from the
                    wifi counters. Sends the data that is inside the
                    textfiles to the wificounter database. 
                    
                    methods are:
                        __init__(db)
                        inport_txt_to_db()
                        
                    all other methods shouldn't be used outside this object.
    @author - mah60
    @param - None
    @return - None
    """
    def __init__(self, db): 
        """
        @summary - creates the RecordHandler object.
        @description - creates the RecordHandler object and
                        sets the db that will be used throughout the code.
        @author - mah60
        @param - db  - DBManager object - the database where the data
                        is being send to.
        @return - None
        """
        # set db
        self.db = db
        
    def import_txt_to_db(self, txt_file):
        """
        @summary - imports the text file data to the given database.
        @description - will import the data inside the text file to the 
                            database given in initilisation. 
                        You may be asked during the function to given start
                        datetime or the filter (mac address and start/end time)
                        if they have been recorded.
        @author - mah60
        @param - txt_file - string - file location/path to the recordings text
                    file.
        @return - None
        """
        if(self.db.is_tables()): # check if required tables exist
            #print("-------------------------------")
            # read data from txt file
            data = fr.read_txt_file(txt_file, True)
            secounds = [0.00, 0.00, 0.00] # total secounds , current value, reset value
            # string for cmds 
            cmd = ["INSERT INTO devices ( macAddress ) VALUES ", 
                   "INSERT INTO counters  ( macAddress)  VALUES ",
                   "INSERT INTO recordings ( recordingDateTime, rssi, counterId ) VALUES ",
                   "INSERT INTO devicerecords (deviceId, recordId) Values "
                   ]
            
            # list for stored values
            mac_list = []
            id_counts = [self.get_id_count("devices"),
                         self.get_id_count("counters"), 
                         self.get_id_count("recordings")]
            is_counter_added = False
            counter_mac = ""
            datetime_set = False
            datetime_value = "" # make the start date time value constant
            for record in data:
                if(record != ''):
                    r_parts = record.split(',')
                    if(not is_counter_added):
                        cmd[1] += "('" + r_parts[1] + "'), "
                        counter_mac = r_parts[1]
                        id_counts[1] = id_counts[1] + 1
                        is_counter_added = True
                    # check for nulls
                    is_nulls = False
                    for p in r_parts:
                        if(p == ''):
                            print("found null")
                            is_nulls = True
                    if(not is_nulls):
                       
                        if(not datetime_set): # check if start datetime value has been set
                            # done to ensure the device is constant
                            # check if connected to wifi
                            if('1970' in r_parts[2]):
                                # if not ask for start datetime
                                print("Device did not connect to Wifi - what was the start date - time?")
                                output = self.ask_datetime()
                                datetime_value = output
                                datetime_set = True
                            else:
                                datetime_value = r_parts[2]
                                datetime_set = True
                        cmd[0], id_counts[0], mac_list, device_reference = self.is_mac_exists("devices", cmd[0], id_counts[0], r_parts[0], mac_list)
                        # make datetime variable for recording time
                        # if counter crashes timer will restart, then millis given will reset to
                        secounds[1] = float(r_parts[3]) # set current seconds
                        if(secounds[2] > secounds[1]):
                            print(secounds)
                            secounds[0] += secounds[1]
                            secounds[2] = secounds[1]                        
                        else:
                            # if not add additional second time to total
                            t = secounds[1] - secounds[2]
                            secounds[0] += t
                            secounds[2] = secounds[1]
                        
                        recordDateTime = datetime.strptime(datetime_value, '%Y-%m-%d-%H-%M-%S')
                        recordDateTime = recordDateTime + timedelta(seconds=secounds[0])
                       # print(recordDateTime)
                        cmd[2] += "('" + recordDateTime.strftime('%Y-%m-%d-%H-%M-%S.%f') + "', " + r_parts[4] + ", " + str(id_counts[1]) + "), "
                        id_counts[2] = id_counts[2] + 1
                        cmd[3] += "( " + str(device_reference[0][0][0]) + ", " + str(id_counts[2]) + "), "
                        # send data in insert many once string exceeds x bytes
                        if(len(cmd[2].encode('utf-8')) > 500000): # max bytes that can be sent at a time is 4194304
                            # get times for different values, in seconds. test for 48401 records
                            # limit of 4000000 = 88, 92, 102
                            # limit of 2000000 = 91, 89, 88
                            # limit of 1000000 = 69, 56, 49
                            # limit of  750000 = 46, 46, 67
                            # limit of  500000 = 44, 45, 44
                            # limit of  250000 = 65, 45, 46
                            # limit of  100000 = 51, 65, 79
                            # limit of   10000 = 137, 133, 149
                            
                            self.send_records(cmd)
                            # reset variables 
                            mac_list = []
                            # string for cmds 
                            cmd = ["INSERT INTO devices ( macAddress ) VALUES ", 
                                   "INSERT INTO counters ( macAddress ) VALUES ",
                                   "INSERT INTO recordings ( recordingDateTime, rssi, counterId ) VALUES ",
                                   "INSERT INTO devicerecords (deviceId, recordId) Values "
                                   ]
            # send final set or records
            self.send_records(cmd)
            # ask if there is a filter
            rssi_limit = self.ask_filter()
            print("the rssi limit is : " + str(rssi_limit))
            if(rssi_limit != -100):
                datetime_value = datetime.strptime(datetime_value, '%Y-%m-%d-%H-%M-%S')
                print("Start time : " + datetime_value.strftime('%Y-%m-%d %H:%M:%S') )
                self.set_filter(rssi_limit, counter_mac, id_counts[1])
        
        
    def send_records(self, cmd):
        """
        @summary - send the records that have been given.
        @description - will execute all commands given through the
                        cmd params.
        @author - mah60
        @param - cmd - string list - a list of sql commands to be executed.
                    Should be insert many commands.
        @return - None
        """
        if(self.db.is_tables()): # check if required tables exist
            # convert commands to have ; on end instead of ', ' 
            for c in cmd: 
                if(')' in c[len(c)-5:]):
                    c = c[:len(c)-2] #  remove last comma
                    c += ";"
                    #print(c)
                    self.db.db_execute(c, False)
    
            
            
    def get_id_count(self, table):
        """
        @summary - get the current ID for the given table.
        @description - get the current ID for the given table. This will
                        be the idea of the last record insert into the 
                        table.
        @author - mah60
        @param - table - string - name of the table you want to check the
                        id for.
        @return - id_count - int - the last records id, max(id)
        """
        id_count = 0 # if not value is returned, defualt to zero
        # execute command to get max id
        if(self.db.is_tables()): # check if required tables exist
            output = self.db.db_execute("SELECT MAX(id) as 'maxId' FROM " + table + ";", True)
            if(output[0][0][0] != None): # check if value exsists
                id_count = output[0][0][0]
        return id_count #  return id_count
                      
    def is_mac_exists(self, table, cmd, id_count, mac, mac_list):
        """
        @summary - check if mac address exists in database or mac list.
        @description - check if the mac address exist in the database or
                        mac list. To ensure no duplicates are sent to the 
                        database. 
                        Mac list is to ensure no duplicates in the the 
                        insert many command. 
        @author - mah60
        @param - table - string - table name in the database.
        @param - cmd - string of the command for any non duplicate 
                        mac addresses to be added to.
        @param - id_count - int - the current id count for mac address, 
                                so reference can be set for later in 
                                the import_txt_to_db() method.
        @param - mac - string -  the mac address string that is being
                                 added to the database.
        @param - mac_list - list [id, mac] - id is the id_count for that
                                            mac address for reference and
                                            mac is the unique mac address
                                            in that list and in the database.
        @return - cmd - string - command string, with added mac address if
                                    unqiue mac address found. 
        @return - id_count - int - id_count, new id count if new unique
                                    mac address found.
        @return - mac_list - list [id, mac] - list of unique mac address.
        @return - reference - [output, cursor] - output is a reference
                                    to select command output, with mac
                                    address id if found and cursor used
                                    if required.
        """
        reference = ""
        if(self.db.is_tables()): # check if required tables exist
        # check if device mac address is in db 
            s_cmd = "SELECT * FROM " + table + " WHERE macAddress = '"+ mac +"';"
            reference = self.db.db_execute(s_cmd, True)
            # send mac address, if not found
            if(len(reference[0]) > 1):
                print("there are duplicates")
            elif(len(reference[0]) == 0): # check if in list array
                if(any(mac in mac_add for mac_add in mac_list)):
                    for m in mac_list:
                        if(m[1] == mac):
                            reference[0] = [m]
                else: 
                    # set ids
                    id_count = id_count + 1
                    # add devices to list, add for bulk insert
                    mac_list.append([id_count, mac])
                    # make reference of id and mac for insert
                    #print(deviceReference[0])
                    reference[0] = [[id_count, mac]]
                    # add to insert statements
                    cmd += "('" + mac +  "'), "
        return cmd, id_count, mac_list, reference
    
    def ask_datetime(self):
        """
        @summary - ask for input for datetime object.
        @description - ask input for the datetime object. Will stay in loop
                        suitable value is returned.
        @author - mah60
        @param - None
        @return - date - string - date time format of input given. Will be
                                    formatted as; 'YYYY-MM-DD-MM-HH-SS'
        """
        # set string list for printing, to ask questions
        datetime_parts = ["year (e.g.2019)", "month (e.g.8)", "day (e.g.30)", "hour (e.g.15)", "minuite (e.g.16)", "second (e.g.52 or 00 if unknown)"]
        datetime_values = []
        is_date = False # will only leave when is_date is True
        date = ""
        # ask for date
        while(not is_date):
            # ask for date time parts
            for p in datetime_parts:
                output = ""
                while(not output.isdigit()):
                    output = input("What was the " + p + " : ")
                datetime_values.append(output)
            # create YYYY-MM-DD-HH-MM-SS string from parts of input
            date = datetime_values[0] + "-" + datetime_values[1] + "-" + datetime_values[2] + "-" + datetime_values[3] + "-" + datetime_values[4] + "-" + datetime_values[5]
            try: # try to convert to date
                datetime.strptime(date, '%Y-%m-%d-%H-%M-%S')
                is_date = True
            except ValueError: # if failed re-ask question
                print(date + " : is not a date (YYYY-MM-DD-HH-MM-SS)")
                datetime_values = [] #  reset if doesnt work
            
        return date
    
    def ask_filter(self):
        """
        @summary - ask if there is a filter device.
        @description - ask if there is a filter device, if no the rssi_value
                        will be set to -100. If yes, will ask for a mac address
                        for the filter device and the start/end time for 
                        the filter reading timezone.
                        
                        Enforce that this method is only called once
                        all data is imported from the text file.
        @author - mah60
        @param - None
        @return - rssi_value - int -  the average rssi in the time zone given
                                        from the filter mac address.
        """
        rssi_value = -100 # rssi_value defualt value is 0
        print("New wifi counter found: ")
        filter_complete =  False #  only finish when task is complete or no mac
                                    # address given
        if(self.db.is_tables()): # check if required tables exist
            while(not filter_complete):
                output = ""
                answer = False
                while(not answer): # wait for answer to be yes or no
                    output = input("     Is there a filter range for this session (Yes or No): ").lower()
                    if(output == "yes" or output =="no"):
                        answer = True
                if(output == "no"): # if no exit while loop and use defualt value
                    return rssi_value
                else:
                    is_mac = False
                    filter_mac = ""
                    # ask for filter mac address
                    while(not is_mac):
                        mac = input("What was the devices mac address : ").upper()
                        mac = hashlib.md5(mac.encode()).hexdigest()
                        # check if mac address is inside the database
                        cmd = "SELECT * FROM devices WHERE macAddress = '" + mac + "';"
                        output = self.db.db_execute(cmd, True)[0]
                        if(len(output) >= 1):
                            filter_mac = mac
                            is_mac = True
                        else:
                            print("Mac address doesnt exist")
                    # ask for start date time and end datetime
                    print("Enter start filter time : ")
                    start_date_time = self.ask_datetime()
                    start_date_time = datetime.strptime(start_date_time, '%Y-%m-%d-%H-%M-%S')
                    print("Enter end filter time : ")
                    end_date_time = self.ask_datetime()
                    end_date_time = datetime.strptime(end_date_time, '%Y-%m-%d-%H-%M-%S')
                    cmd = "SELECT ROUND(AVG(recordings.rssi)) FROM devices, devicerecords, recordings WHERE "
                    cmd += "devicerecords.deviceId = devices.id AND devicerecords.recordId = recordings.id "
                    cmd += "AND devices.macAddress = '" + filter_mac + "' AND recordings.recordingDateTime "
                    cmd += "BETWEEN '" + start_date_time.strftime('%Y-%m-%d %H:%M:%S')  +"' AND '" + end_date_time.strftime('%Y-%m-%d %H:%M:%S')  +"';"
                    # send cmd
                    print(cmd)
                    output = self.db.db_execute(cmd, True)[0]
                    # set filter range
                    if(len(output) == 1): # if value is returned set new rssi_value
                        rssi_value = int(output[0][0])
                        return rssi_value
        return rssi_value
                
                
        
        
    def set_filter(self, rssi_limit, counter_mac, counter_id):
        """
        @summary - enforces the filter given to the counter id.
        @description - enforces the filter given to the counter id, 
                        make sure all rssi values that were recorded
                        are above the rssi limit. 
                        
                        Will remove any values below the rssi_limit in the
                        database that is connected the counter_id.
                        
                        Enforce that this method is only called once
                        all data is imported from the text file and rssi
                        limit is found. Don't bother if value is -100, as this
                        is the max rssi value.
        @author - mah60
        @param - rssi_limit - int - rssi limit - between 0 to -100.
        @param - counter_mac - string - mac address of the counter.
        @param - counter_id - int - the id for the given counter 
                                        in the counters table.
        @return - None
        """
        if(self.db.is_tables()): # check if required tables exist
            if(rssi_limit != -100): # dont do if rssi_limit is max rssi value
                tables = ["devices", "devicerecords", "recordings"]
                # get items above limit
                cmd = "SELECT devices.id, devicerecords.id, recordings.id FROM devices, devicerecords, recordings WHERE "
                cmd += "devices.id=devicerecords.deviceId AND recordings.id=devicerecords.recordId AND recordings.rssi < " + str(rssi_limit)
                cmd += " AND recordings.counterId = " + str(counter_id) + " ;"
                results = self.db.db_execute(cmd, True)[0]
                ids = [[],[],[]] # [device.Id, deviceRecords.Id, recordings.Id ]
                for r in results:
                    for i in range(0,3):
                        if(r[i] not in ids[i]):
                            ids[i].append(r[i])
                # turn off foreign key restraints # WARNING MAKE SURE TO TURN BACK ON
                self.db.db_execute("SET FOREIGN_KEY_CHECKS = 0;", False)
                # delete unwanted rows
                for i, table_ids in enumerate(ids):
                    cmd = "DELETE FROM " + tables[i] + " WHERE (id) IN ("
                    # create cmd 
                    for row_id in table_ids:
                        cmd += "(" + str(row_id) + "),"
                    # end command
                    cmd = cmd[:len(cmd)-1]
                    cmd += ");"
                    self.db.db_execute(cmd, False)
                        
                # turn on foreign keys
                self.db.db_execute("SET FOREIGN_KEY_CHECKS = 1;", False)
                
                # alter counter rssi limit value
                cmd = "UPDATE counters SET filterId = " + str(rssi_limit) + " WHERE id = " + str(counter_id) + ";"
                self.db.db_execute(cmd, False)
        
    