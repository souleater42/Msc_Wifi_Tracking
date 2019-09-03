# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 15:36:26 2019

@author: Mhowa
"""
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.pyplot import figure
import numpy as np
import hashlib 


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
        
        
    def device_rssi_over_time(self, mac, is_distance, threshold):
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
        @return - None
        """
        if(self.db.is_tables()): # check if required tables exist
            # convert mac to md5 hash
            hashed_mac = hashlib.md5(mac.encode()).hexdigest()
            # create command
            cmd = "SELECT recordingDateTime, recordings.rssi FROM devices, devicerecords, recordings WHERE "
            cmd += "devicerecords.deviceId = devices.id AND devicerecords.recordId = recordings.id "
            cmd += "AND devices.macAddress = '" + hashed_mac + "';"
            # send command
            output = self.db.db_execute(cmd, True)[0]
            # check if mac exists in db
            if(len(output) != 0):
                print("mac exists")
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
                        rssi[i] = self.convert_rssi_to_distance(r)
                # plot graph
                fig, ax = plt.subplots()
                dt_format = mdates.DateFormatter('%d-%m-%y\n%H:%M:%S')
                ax.xaxis.set_major_formatter(dt_format)
                plt.xlabel("Date Time (Year-Month-Day Hour:Miniute:Second)")
                title = ""
                save_file = ""
                if(is_distance): # if is_distance is true plot distance vs time graph
                    title = mac + " : Distance value over time"
                    plt.ylabel("Distance (m)")
                    save_file = "distance_over_time_for_" + mac.replace(":", "_") + ".png"
                else:
                    title = mac + " : RSSI value over time"
                    plt.ylabel("RSSI (dB)")
                    save_file = "rssi_over_time_for_" + mac.replace(":", "_") + ".png"
                plt.title(title)
                fig.set_size_inches(10,8)
                plt.plot(dates, rssi)
                plt.savefig(save_file)
                plt.show()
            else: 
                print("mac does not exist")
            
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
                distance.append(self.convert_rssi_to_distance(x))
            # plot and save graph
            fig, ax = plt.subplots()
            plt.plot(rssi_value, distance)
            plt.title("RSSI vs Distance For ESP8266")
            plt.ylabel("Distance (m)")
            plt.xlabel("RSSI (dB)")
            fig.set_size_inches(10,8)
            save_file = "RSSI_vs_Distance_for_ESP8266.png"
            plt.savefig(save_file)
            plt.show()
        
    def convert_rssi_to_distance(self, rssi_value):
        """
        @summary - converts rssi to distance.
        @description - converts rssi to distance. The formula was found on; 
                https://iotandelectronics.wordpress.com/2016/10/07/how-to-calculate-distance-from-the-rssi-value-of-the-ble-beacon/
                Measured power for ESP8266 was found to be -70 through testing.
        @author - mah60
        @param - rssi_value - int - rssi value to be converted.
        @return - distance (meters) - int - distance that was calculated.
        """
        return 10**((-70-rssi_value)/(10*2))
            
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
        
        
        
    def total_count_over_time(self):
        """
        @summary - creates graph for total device count over time.
        @description - creates a graph that will show the total device
                        count over the time period of data in the database.
        @author - mah60
        @param - None
        @return - None
        """
        # get hour intervals count
        hour_interval = 1
        hour_count, dates = self.get_hour_count(hour_interval)
        # edit table to only show total over time
        max_count = 0
        for i, c in enumerate(hour_count):
            if(c >= max_count):
                max_count = c
            hour_count[i] = max_count
        # plot graph
        self.plt_count_over_time(hour_count, dates, "Total Visits Count Over Time", "total_count_over_time.png")
        
    def count_over_time(self):
        """
        @summary - creates a graph that shows the device count over time.
        @description - creates a graph that shows the device count over time
                        with a 1 hour interval.
        @author - mah60
        @param - None
        @return - None
        """
        # get hour intervals count
        hour_interval = 1
        hour_count, dates = self.get_hour_count(hour_interval)
        # plot graph
        self.plt_count_over_time(hour_count, dates, "Visits Count Over Time", "count_over_time.png")

        
    def plt_count_over_time(self, hour_count, dates, title, save_file):
        """
        @summary - Plots a graph of counts vs dates.
        @description - Plots a graph of counts vs dates.
        @author - mah60
        @param - hour_count - int list - the values for counts over time.
        @param - dates - list datetime object - values for dates, 
                            need to be same size as hour_count.
        @param - title - string - titile of the graph.
        @param - save_file - string - save location/path for the graph.
        @return - None
        """
        # plot graph
        fig, ax = plt.subplots()
        dt_format = mdates.DateFormatter('%d-%m-%y\n%H:%M:%S')
        ax.xaxis.set_major_formatter(dt_format)
        plt.step(dates, hour_count)
        plt.title(title)
        plt.xlabel("Date Time (Year-Month-Day Hour:Miniute:Second)")
        plt.ylabel("No. of visits")
        fig.set_size_inches(10,8)
        plt.savefig(save_file)
        plt.show()
        
        
        
    def get_hour_count(self, hour_iterate):
        """
        @summary - gets the count over time from the database.
        @description -  gets the count over time and returns the count
                        and date values.
        @author - mah60
        @param - hour_iterate - int - how much to increase the date from.
        @return - hour_count - int list - the values for counts over time.
        @return - dates - list datetime object - values for dates, 
                            need to be same size as hour_count.
        """
        hour_count = []
        dates = []
        if(self.db.is_tables()): # check if required tables exist
            # get max and min date
            dt = self.db.db_execute("SELECT MIN(recordingDateTime) FROM  recordings;", True)[0][0][0]
            max_date = self.db.db_execute("SELECT MAX(recordingDateTime) FROM  recordings;", True)[0][0][0]
            while(dt <= max_date): # continue till above max date
                dates.append(dt) # add date to list
                cmd =  "SELECT  COUNT(DISTINCT devices.macAddress) as deviceCount FROM devices, devicerecords, recordings "
                cmd += "WHERE devicerecords.deviceId = devices.id AND devicerecords.recordId = recordings.id "
                cmd += "AND recordingDateTime BETWEEN '" + dt.strftime('%Y-%m-%d %H:%M:%S')
                cmd += "' AND DATE_ADD('" + dt.strftime('%Y-%m-%d %H:%M:%S') + "', INTERVAL 1 HOUR);"
                hour_count.append(self.db.db_execute(cmd, True)[0][0][0]) # get hour count for that date
                dt = dt + timedelta(hours=hour_iterate)
        return hour_count, dates
    
    def get_dwelling_time_frequency(self, timeout):
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
        @return - None
        """
        if(self.db.is_tables()): # check if required tables exist
            cmd = "SELECT devices.macAddress, recordings.recordingDateTime FROM devices, devicerecords, recordings WHERE "
            cmd += "devicerecords.deviceId = devices.id AND devicerecords.recordId = recordings.id "
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
            # plot graph
            fig, ax = plt.subplots()
            b = len(dwelling_time)
            if(b == 0):
                b = 1
            plt.hist(dwelling_time, bins=b)
            plt.ylabel("Frequency")
            plt.xlabel("Dwelling Time (Hours)")
            plt.title("Hist Of Dwelling Time\nWith " + str(timeout) + " Minute Timeout" )
            fig.set_size_inches(10,8)
            save_file = "Hist_Dwelling_Time_" + str(timeout) + "M_TO.png"
            plt.savefig(save_file)
            plt.show()
                
                