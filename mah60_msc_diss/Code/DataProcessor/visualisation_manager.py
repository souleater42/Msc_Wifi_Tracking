# -*- coding: utf-8 -*-
"""
@author mah60
@version - 0.1 - created the visulisation manager, this object will produce 
                    graphs from the database. That will demonstrate what 
                    statistics can be made from the collected data.
                    The graphs that are produced are; distance/rssi of a 
                    device over time, rssi vs distance graph, total counter
                    over time, count over time and a histogram of dwelling 
                    times.
                    - 01/09/2019;
            0.2 - added config file variables on where to save the files. 
                    modified get_hour_count() to get_iterate_count() and 
                    made the commad a multi-select statement using union.
                    Created function called take_date() and 
                    send_cmd_count() to reduce run time on 
                    the sql statement. From 40 seconds to 20 seconds
                    - 03/09/2019;
            0.3 - modified graph methods to also separate the data by
                    counter. As well, created a method to produce a 
                    final report from the data that was found. - 05/09/2019;
            
"""
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.pyplot import figure
import numpy as np
import hashlib 
import config as cf
from pylab import title, figure, xlabel, ylabel, xticks, bar, legend, axis, savefig
from fpdf import FPDF


class VisualisationManager:
    """
    @summary - manages all visulisations.
    @description - manages all visulisations made in the application. 
                    Produces graphs and stats about the data that
                    is currently in the given database.
                    
                    The methods that will produce these results are:
                        __init__(db)
                        device_rssi_over_time(mac, is_distance, threshold)
                        rssi_to_distance_graph()
                        get_average_rssi_over_time()
                        total_count_over_time()
                        count_over_time()
                        get_dwelling_time_frequency(timeout)
                        
    @author - mah60
    @param - None
    @return - None
    """
    
    def __init__(self, db):
        """
        @summary - will create the VisulisationManager.
        @description - will create the VisulisationManager. This object
                        will produce visualisations from the database given
                        and other statistics.
        @author - mah60
        @param - db - DBManager object - the database connector to the
                                        databases location.
        @return - None
        """
        # set db
        self.db = db
        self.made_graphs_loc = []
        
    def send_graphs_to_pdf(self):
        """
        @summary - produces a pdf of graphs made from the database.
        @description -  produces a pdf of graphs and stats from the database
                        and saves the pdf in the apprioate folder. 
        @author - mah60
        @param - None
        @return - None
        """
        # get stats
        dt_now = date.today()
        cmd = "SELECT '', MIN(recordings.recordingDateTime) AS startDate, MAX(recordings.recordingDateTime) AS endDate, "
        cmd += "COUNT(DISTINCT devices.macAddress) AS NoDevices, COUNT(DISTINCT counters.macAddress) AS NoCounters, "
        cmd += "COUNT(DISTINCT counters.id) AS NoSessions, COUNT(*) AS NoRecords "
        cmd += "FROM devices, devicerecords, recordings, counters WHERE devices.id=devicerecords.deviceId AND "
        cmd += "recordings.id=devicerecords.recordId AND recordings.counterId=counters.id;"
        output = list(self.db.db_execute(cmd, True)[0][0])
        lines = ["", "Start Timestamp : ", "End Timestamp : ", "Number Of Devices : ",
                 "Number Of Counters : ", "Number Of Counter Sessions : ", "Number Of Records : "]
        output[1] = output[1].strftime("%d/%m/%Y %H:%M:%S")
        output[2] = output[2].strftime("%d/%m/%Y %H:%M:%S")
        # write pdf, using php
        pdf = FPDF() 
        pdf.add_page()
        pdf.set_xy(0, 0)
        pdf.set_font('arial', 'B', 12)
        pdf.cell(90, 10, " ", 0, 2, 'C')
        pdf.cell(10)
        pdf.cell(60, 10, ('WiFi Counter Report - ' + dt_now.strftime("%d/%m/%Y")))
        pdf.set_font('arial', '', 10)
        pdf.cell(90, 10, " ", 0, 2, 'C')
        pdf.cell(60)
        for i, item in enumerate(output):
            pdf.cell(90, 5, " ", 0, 2, 'C')
            pdf.cell(-160)
            pdf.cell(0, 0, (lines[i] + str(item)))
        pdf.cell(90, 10, " ", 0, 2, 'C')
        pdf.cell(-190)
        for f in self.made_graphs_loc:
            pdf.image(f, x = None, y = None, w = 180, h = 130, type = '', link = '')
        # save pdf
        save_file = cf.report_save_path + cf.report_save_file + dt_now.strftime("%d_%m_%Y") + ".pdf"
        pdf.output(save_file, 'F')          
        print("Report has been saved to : " + save_file)
        
        
    def device_rssi_over_time(self, mac, is_distance, threshold, separate):
        """
        @summary - create graph of rssi/distance over time.
        @description - create graph of rssi/distance over time. This will
                        be recordings from the database and the data inserted.
                        
                        The graph will be about a specified mac address.
        @author - mah60
        @param - mac - string - mac address that will be filtered to
                                see rssi or distance over the time of
                                data collected.
        @param - is_distance - if True - will produce distance vs time graph.
                             - if False - will produce rssi vs time graph.
        @param - threshold - int - will be the + or - value to reduce noise
                                    in the rssi value.
        @param - separate - boolean - True - graph will be separated by counter.id.
                                    - False - data will not be separated by counter.id.
        @return - None
        """
        if(self.db.is_tables()): # check if required tables exist
            # convert mac to md5 hash
            hashed_mac = hashlib.md5(mac.encode()).hexdigest()
            # get counters if separate
            counters = [[]]
            label = ["All Counters"]
            if(separate):
                counters = self.db.db_execute("SELECT * FROM counters;", True)[0]
                label  = self.get_counter_labels(counters) # make labels
            dates_values = []  # dates values to plot
            rssi_values = []  # rssi values to plot
            for c in counters:
                # create command
                cmd = "SELECT recordingDateTime, recordings.rssi FROM devices, devicerecords, recordings WHERE "
                cmd += "devicerecords.deviceId = devices.id AND devicerecords.recordId = recordings.id "
                if(separate): # only add if separate is True
                    cmd += "AND recordings.counterId = " + str(c[0]) + " "
                cmd += "AND devices.macAddress = '" + hashed_mac + "' ORDER BY recordings.recordingDateTime;"
                # send command
                output = self.db.db_execute(cmd, True)[0]
                # check if mac exists in db
                if(len(output) != 0):
                    # print("mac exists : " + mac)
                    # sort dates and rssi values into list
                    dates = []
                    rssi = []
                    pre_rssi = 0
                    for r in output:
                        dates.append(r[0])
                        # make rssi threshhold of +-threshold
                        if(r[1] >= (pre_rssi-threshold) and r[1] <= (pre_rssi+threshold)):
                            rssi.append(pre_rssi)
                        else:
                            rssi.append(r[1])
                            pre_rssi = r[1]
                    # if is_distance =  convert rssi to meters
                    if(is_distance):
                        for i, r in enumerate(rssi):
                            rssi[i] = self.convert_rssi_to_distance(r, 2)
                    dates_values.append(dates)
                    rssi_values.append(rssi)
            # plot graph
            fig, ax = plt.subplots()
            dt_format = mdates.DateFormatter('%d-%m-%y\n%H:%M:%S')
            ax.xaxis.set_major_formatter(dt_format)
            plt.xlabel("Date Time (Year-Month-Day Hour:Miniute:Second)")
            title_graph = ""
            save_file = ""
            if(is_distance): # if is_distance is true plot distance vs time graph
                title_graph = mac + " : Distance value over time"
                plt.ylabel("Distance (m)")
                if(separate): # different save if True
                    save_file = cf.graph_save_path +"distance_over_time_for_" + mac.replace(":", "_") + "_sep_counter.png"
                else: 
                    save_file = cf.graph_save_path +"distance_over_time_for_" + mac.replace(":", "_") + ".png"
            else:
                title_graph = mac + " : RSSI value over time"
                plt.ylabel("RSSI (dB)")
                if(separate):  # different save if True
                    save_file = cf.graph_save_path + "rssi_over_time_for_" + mac.replace(":", "_") + "_sep_counter.png"
                else:
                    save_file = cf.graph_save_path + "rssi_over_time_for_" + mac.replace(":", "_") + ".png"
            plt.title(title_graph)
            fig.set_size_inches(10,8)
            alpha = 1
            if(separate): # set alpha to 0.75 if True, means can see all results
                alpha = 0.75
            for i in range(len(dates_values)):    
                plt.plot(dates_values[i], rssi_values[i], alpha=alpha)
            ax.legend(label, loc='best')
            self.made_graphs_loc.append(save_file)
            plt.savefig(save_file)
            if(cf.show_graphs): # only show graph in terminal if True
                plt.show()
        else: 
            print("mac does not exist : " + mac)
            
    def rssi_to_distance_graph(self):
        """
        @summary - plots the rssi vs distance graph for the ESP8266.
        @description - plots the rssi vs distance graph for the ESP8266. The
                        function conver_rssi_to_distance(rssi_value) is used
                        to make the conversions.
        @author - mah60
        @param - None
        @return -None
        """
        if(self.db.is_tables()): # check if required tables exist
            # variables for graph
            rssi_value = []
            distance = []
            # set values
            for x in range(-100, 0): # rssi values, 0 to -100
                rssi_value.append(x)
                # convert rssi to distance
                distance.append(self.convert_rssi_to_distance(x, 2))
            # plot and save graph
            fig, ax = plt.subplots()
            plt.plot(rssi_value, distance)
            plt.title("RSSI vs Distance For ESP8266")
            plt.ylabel("Distance (m)")
            plt.xlabel("RSSI (dB)")
            fig.set_size_inches(10,8)
            save_file = cf.graph_save_path + "RSSI_vs_Distance_for_ESP8266.png"
            self.made_graphs_loc.append(save_file)
            plt.savefig(save_file)
            if(cf.show_graphs): # only plot graph if True
                plt.show()
        
    def convert_rssi_to_distance(self, rssi_value, env_power):
        """
        @summary - converts rssi to distance.
        @description - converts rssi to distance. The formula was found on; 
                https://iotandelectronics.wordpress.com/2016/10/07/how-to-calculate-distance
                -from-the-rssi-value-of-the-ble-beacon/
                Measured power for ESP8266 was found to be -70 through testing.
        @author - mah60
        @param - rssi_value - int - rssi value to be converted.
        @return - distance (meters) - int - distance that was calculated.
        """
        return 10**((-70-rssi_value)/(10*env_power))
            
    def get_average_rssi_over_time(self, mac):
        """
        @summary - will calculate average rssi over time for specified mac address.
        @description - will get all records for mac address given and find the
                        average rssi. Was used for the testing to find 
                        the measured power - rssi at 1 meter in 
                        convert_rssi_to_distance() method.
        @author - mah60
        @param - mac - string - mac address to search for.
        @return - average - int - average rssi over time period in the database.
        @return - item_amount - int -  amount of items in the database for
                                        reference.
        """
        if(self.db.is_tables()): # check if required tables exist
            # convert mac to md5 hash
            hashed_mac = hashlib.md5(mac.encode()).hexdigest()
            # create command
            cmd = "SELECT recordings.rssi FROM devices, devicerecords, recordings WHERE "
            cmd += "devicerecords.deviceId = devices.id AND devicerecords.recordId = recordings.id "
            cmd += "AND devices.macAddress = '" + hashed_mac + "';"
            # send command
            output = self.db.db_execute(cmd, True)[0]
            item_amount = len(output)
            total = 0
            for r in output:
                total += float(r[0])
            # get average
            average = total/item_amount
            return average, item_amount
        
        
        
    def total_count_over_time(self, separate):
        """
        @summary - creates graph for total device count over time.
        @description - creates a graph that will show the total device
                        count over the time period of data in the database.
        @author - mah60
        @param - separate - boolean - True - graph will be separated by counter.id.
                                    - False - data will not be separated by counter.id.
        @return - None
        """
        # get hour intervals count
        hour_interval = 1
        dates = []
        counts = []
        label = ["All Counters"]
        save_path = cf.graph_save_path + "total_count_over_time.png"
        if(separate):
            # get counters
            save_path = cf.graph_save_path + "total_count_over_time_sep_count.png"
            counters = self.db.db_execute("SELECT * FROM counters;", True)[0]
            date_count_counters =  []
            label  = self.get_counter_labels(counters)
            # create list for each counter found
            for c in counters:
                date_count_counters.append(self.get_iterate_count(hour_interval, c[0]))
            # sort dates and times
            for dt_count in date_count_counters: # split into dates and times
                dates.append(dt_count[0])
                counts.append(dt_count[1])
        else:
            dt_count = self.get_iterate_count(hour_interval)
            dates.append(dt_count[0])
            counts.append(dt_count[1])
        
        for count in counts: #  find max for each counter
            # edit table to only show total over time
            max_count = 0
            for i, c in enumerate(count):
                if(c >= max_count):
                    max_count = c
                count[i] = max_count
        # plot graph
        self.plt_count_over_time(counts, 
                                 dates,
                                 "Total Visits Count Over Time",
                                 save_path,
                                 label)
        
    def count_over_time(self, separate):
        """
        @summary - creates a graph that shows the device count over time.
        @description - creates a graph that shows the device count over time
                        with a 1 hour interval.
        @author - mah60
        @param - separate - boolean - True - graph will be separated by counter.id.
                                    - False - data will not be separated by counter.id.
        @return - None
        """
        hour_interval = 1  # get hour intervals count
        if(separate):
            # get counters and labels
            counters = self.db.db_execute("SELECT * FROM counters;", True)[0]
            label  = self.get_counter_labels(counters)
            date_count_counters =  []
            for c in counters: #  find data on each counter
                date_count_counters.append(self.get_iterate_count(hour_interval, c[0]))
            # sort dates and times
            dates = []
            counts = []
            for dt_count in date_count_counters:
                dates.append(dt_count[0])
                counts.append(dt_count[1])
            self.plt_count_over_time(counts, 
                                    dates, 
                                    "Visits Count Over Time", 
                                    (cf.graph_save_path + "count_over_time_sep_counters.png"),
                                    label
                                    )

        else:
            date_count = self.get_iterate_count(hour_interval)
            # plot graph
            self.plt_count_over_time([date_count[1]], 
                                     [date_count[0]], 
                                     "Visits Count Over Time", 
                                     (cf.graph_save_path + "count_over_time.png")
                                     )

        
    def plt_count_over_time(self, hour_count, dates, title_graph, save_file, label=["All Counters"]):
        """
        @summary - Plots a graph of counts vs dates.
        @description - Plots a graph of counts vs dates.
        @author - mah60
        @param - hour_count - list of list of integers - the values for counts over time.
                                    , len(hour_count) will represent number of counters.
        @param - dates - list of list of datetime object - values for date,
                            need to be same size as hour_count.
                            , len(dates) will represent number of counters.
        @param - title - string - titile of the graph.
        @param - save_file - string - save location/path for the graph.
        @param - label - list of strings - labels for each counter, defualt ["All Counters"]
        @return - None
        """
        # plot graph
        fig, ax = plt.subplots()
        dt_format = mdates.DateFormatter('%d-%m-%y\n%H:%M:%S')
        ax.xaxis.set_major_formatter(dt_format)
        for i in range(len(hour_count)): # plot each record in the list
            plt.step(dates[i], hour_count[i])
        ax.legend(label, loc='best')
        plt.title(title_graph)
        plt.xlabel("Date Time (Year-Month-Day Hour:Miniute:Second)")
        plt.ylabel("No. of visits")
        fig.set_size_inches(10,8)
        self.made_graphs_loc.append(save_file)
        plt.savefig(save_file)
        if(cf.show_graphs):
            plt.show()
        
        
        
    def get_iterate_count(self, hour_iterate, counter=None):
        """
        @summary - gets the count over time from the database.
        @description -  gets the count over time and returns the count
                        and date values.
        @author - mah60
        @param - hour_iterate - int - how much to increase the date from.
        @return - date_count - list - [[],[]] , [dates, iterate_count] - 2d
                                        list that holds a list of dates and 
                                        their corrisponding count values.
        """
        dates = []
        if(self.db.is_tables()): # check if required tables exist
            # get max and min date for counters
            cmd = "SELECT MIN(recordingDateTime), MAX(recordingDateTime) FROM  recordings GROUP BY counterId;"
            dt_groups = self.db.db_execute(cmd, True)[0]
            for dt in dt_groups: # 0 -> min, 1 -> max
                cmd = "" # create start of multi select command
                dt = list(dt)
                count_index = 1
                while(dt[0] <= dt[1]): # continue till above max date
                    cmd +=  "SELECT '" + dt[0].strftime('%Y-%m-%d %H:%M:%S') + "' AS countDate, "
                    cmd += "COUNT(DISTINCT devices.macAddress) AS deviceCount FROM devices, "
                    cmd += " devicerecords, recordings WHERE devicerecords.deviceId = devices.id AND "
                    cmd += "devicerecords.recordId = recordings.id " 
                    if(counter): # only do if counter is given
                        cmd += "AND recordings.counterId = " + str(counter) + " "
                    cmd += "AND recordingDateTime BETWEEN '" + dt[0].strftime('%Y-%m-%d %H:%M:%S')
                    cmd += "' AND DATE_ADD('" + dt[0].strftime('%Y-%m-%d %H:%M:%S') + "', INTERVAL 1 HOUR) "
                    cmd += "UNION "
                    #dates.append([dt[0], self.db.db_execute(cmd, True)[0][0][0]]) # add date with count to list
                    dt[0] = dt[0] + timedelta(hours=hour_iterate)
                    count_index = count_index + 1
                    if(len(cmd.encode('utf-8')) > 20000): # if string exceeds x bytes send command
                                                            # and reset cmd string
                        dates = self.send_cmd_count(cmd, dates)
                        cmd = ""
                # at end of loop send final command
                dates = self.send_cmd_count(cmd, dates)

        date_count = [[],[]] # [dates, iterate_count]
        dates.sort(key=self.take_date) # sort list by date
        # put list in dates and iterate_count
        
        for i, dc in enumerate(dates):
            date_count[0].append(dc[0])
            date_count[1].append(dc[1])
            if((i+1) < len(dates)): #  make sure doesnt go above array size
                if(dates[i+1][0] > (dc[0] + timedelta(hours=hour_iterate))):
                    # if greater than hour gap, make next value 0 till date seen again.
                    # value is 0, as no recodings in that time.
                    date_count[0].append((dc[0] + timedelta(hours=hour_iterate)))
                    date_count[1].append(0)
        #print(date_count)
        return date_count
        
    def take_date(self, element):
        """
        @summary - returns the date element.
        @description - returns the date element for the get_iterate_count()
                        method. This is used as a key for list.sort()
                        method.
        @author mah60
        @param - element - the 2d list wanting to get the 1st item in.
        @return - element[0]  - fist element in the list.
        """
        return element[0]
    
    def send_cmd_count(self, cmd, dates):
        """
        @summary - sends the count command and add values found are added dates list.
        @description - sends the count command and add values found to dates list.
                        only use with get_iterate_count().
        @author - mah60
        @param - cmd - string - command string to send to db
        @param - dates - [[DateTime object, count]] - list of list that represent
                            the time and the device count at that time.
        @return - dates - [[DateTime object, count]] - list of list that represent
                            the time and the device count at that time.
        """
        if(self.db.is_tables()):
            cmd = cmd[:len(cmd)-7]
            cmd += ";"
            output = self.db.db_execute(cmd, True)[0]
            # convert output to dates
            for o in output:
                dates.append([datetime.strptime(o[0], '%Y-%m-%d %H:%M:%S'),o[1]])
        return dates
    
    def get_dwelling_time_frequency(self, timeout, separate):
        """
        @summary - create graph of dwelling time frequency.
        @description - will create graph of the dwelling time frequency. The
                        timeout variable determines how much time untill the
                        device is considered to leave the range of the device, 
                        without hearing anything from the device.
        @author - mah60
        @param - timeout- int - amounts of miniutes of not hearing the device
                                    and condisidering the device has left 
                                    the zone.
        @param - separate - boolean - True - graph will be separated by counter.id.
                                    - False - data will not be separated by counter.id.
        @return - None
        """
        if(self.db.is_tables()): # check if required tables exist
            counters = [[None]]
            dwelling_times_c = []
            label = ["All Counters"]
            if(separate): # get counters
                counters = self.db.db_execute("SELECT * FROM counters;", True)[0]
                label  = self.get_counter_labels(counters)
            for c in counters: # create dwelling time for each counter. If [[None]], will complete for all.
                cmd = "SELECT devices.macAddress, recordings.recordingDateTime FROM devices, devicerecords, recordings WHERE "
                cmd += "devicerecords.deviceId = devices.id AND devicerecords.recordId = recordings.id "   
                if(separate):
                    cmd += "AND recordings.counterId = " + str(c[0]) + " "
                cmd += "ORDER BY recordings.recordingDateTime;"
                output = self.db.db_execute(cmd, True)[0]
                mac_addresses = [] # [mac addresses, start_time, last seen]
                dwelling_time = []
                for o in output:
                    if(any(o[0] in mac_add for mac_add in mac_addresses)):
                        # find which index it is
                        for m in mac_addresses:
                            if(o[0] in m[0]):
                                # add threshold to last seen
                                timeout_time = m[2] + timedelta(minutes=timeout)
                                if(o[1] <= timeout_time): # still within time zone
                                    # change last seen
                                    m[2] = o[1]
                                else: # timed out # dwelling_time = current time - start time
                                    dwelling_time.append((o[1]-m[1]).total_seconds()/(60*60))
                                    m[1] = o[1]
                                    m[2] = o[1]
                    else: 
                        mac_addresses.append([o[0], o[1], o[1]])
                # calculate last dwelling times, as final values won't exceed max datetime
                for m in mac_addresses:
                    # check if start and last seen is the same.
                    #  if so device has not been seen again so dont
                    #  work out final dwelling time.
                    if(m[1] != m[2]):
                        # if not same calculate final dwelling time
                        dwelling_time.append((m[2]-m[1]).total_seconds()/(60*60))
                dwelling_times_c.append(dwelling_time) # add list of dwelling time to list
            # plot graph
            fig, ax = plt.subplots()
            for h in dwelling_times_c: # plot list of dwelling time
                b = len(dwelling_time)
                if(b == 0): # check there are value, if not bins = 1
                    b = 1
                alpha = 1
                if(separate): # set alpha to 0.75 if separate is True
                    alpha = 0.75
                plt.hist(h, alpha=alpha, bins=b, edgecolor='black', linewidth=1.2)
            ax.legend(label, loc='best')
            plt.ylabel("Frequency")
            plt.xlabel("Dwelling Time (Hours)")
            plt.title("Hist Of Dwelling Time\nWith " + str(timeout) + " Minute Timeout" )
            fig.set_size_inches(10,8)
            save_file = ""
            if(separate):  # change file save if separate is True
                save_file = cf.graph_save_path + "Hist_Dwelling_Time_" + str(timeout) + "M_TO_Sep_Counter.png"
            else:
                save_file = cf.graph_save_path + "Hist_Dwelling_Time_" + str(timeout) + "M_TO.png"
            self.made_graphs_loc.append(save_file)
            plt.savefig(save_file)
            if(cf.show_graphs):
                plt.show()
                
    def get_counter_labels(self, counters):
        """
        @summary - create list of counter labels.
        @description - creates list of counter labels. If same counter appears
                        more than once the session count will increase.
        @author - mah60
        @param - counters - list of tuple - [(id, macAddress, rssi_limit)]
                                        - get from SELECT * FROM counters; command.
        @return - label - list of strings - labels for each counter.
        """
        counter = []
        label = []
        for c in counters: # create label for each counter
                            # If counter already seen, increase session number.
            label.append("Session " + str(counter.count(c[1]) + 1) + " : " + c[1])
            counter.append(c[1])
        return label
                
                