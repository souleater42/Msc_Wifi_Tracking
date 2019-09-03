# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 17:33:06 2019

@author: Mhowa
"""
import db_manager as dbm
import file_reader as fr
import record_handler
import visualisation_manager
import time
    

def main():
    """
    @summary - the application controller.
    @description - will controll what is happening at what time. e.g. install 
            data from recordings text files or creating visualisations.
    @author - mah60
    @param - None
    @return - None
    """
    db = dbm.DBManager()
    rh = record_handler.RecordHandler(db)
    vm = visualisation_manager.VisualisationManager(db)
    #-----------------------------------
    #db.reset_tables()
    #file = "recordings_4.txt"
    #rh.import_txt_to_db(file)
    
    # create visualisations 
    #mac = "0C:CB:85:25:D1:F1"
    #vm.device_rssi_over_time(mac, False, 4)
    #vm.device_rssi_over_time(mac, True, 4)
    #vm.total_count_over_time()
    #vm.count_over_time()
    #vm.rssi_to_distance_graph()
    #vm.get_dwelling_time_frequency(60)    
    """
    # test turnover bytes - for fasts speed
    #-------------------------------------------------
    turn_bytes = [10000, 100000, 250000, 500000, 750000, 1000000, 2000000, 4000000]
    for b in turn_bytes:
        for i in range (0, 3):
            db.reset_tables()
            print("-------------------------------")
            print("test " + str(i+1)+ ":")
            print("bytes limit: " + str(b))
            before = int(round(time.time()))
            file = "recordings_3.txt"
            rh.import_txt_to_db(file, db, b)
            after = int(round(time.time()))
            stopwatch_time = after-before
            print("time (sec): " + str(stopwatch_time))
    """
        # get average rssi over time -> testing
    #-----------------------------------
    """"
    for i in range(1,11):
        file = "meter_test_" + str(i) + ".txt"
        db.reset_tables()
        rh.import_txt_to_db(file)
        mac = "0C:CB:85:25:D1:F1"
        average, item_amount = vm.get_average_rssi_over_time(mac)
        print("test " + str(i) + ": average value: " + str(average) + "at 1 meter for 5 mins\nWith " + str(item_amount) + " records")
    # results 
    """
    """
    test 1: average value: -78.0at 1 meter for 5 mins
    With 1 records
    test 2: average value: -77.33333333333333at 1 meter for 5 mins
    With 3 records
    test 3: average value: -69.30674846625767at 1 meter for 5 mins
    With 163 records
    test 4: average value: -71.06629834254143at 1 meter for 5 mins
    With 362 records
    test 5: average value: -67.04672897196262at 1 meter for 5 mins
    With 214 records
    test 6: average value: -70.0863309352518at 1 meter for 5 mins
    With 278 records
    test 7: average value: -72.04761904761905at 1 meter for 5 mins
    With 462 records
    test 8: average value: -68.49095607235142at 1 meter for 5 mins
    With 387 records
    test 9: average value: -71.70263788968825at 1 meter for 5 mins
    With 417 records
    test 10: average value: -72.53793103448275at 1 meter for 5 mins
    With 290 records
    
    Average results determines rssi value to be 71.5 or 70 
    when there are more than 10 records
    """
    db.db_close()

if __name__ == "__main__":
    main()
