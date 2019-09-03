# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 18:22:42 2019

@author: Mhowa
"""

import mysql.connector as db_con
import file_reader as fr

class DBManager:
    """
    @summary - database connector controller.
    @description - will have methods that will connect to the wificounter
                database. 
                
                The methods that are in this class are:
                    __init__()
                    db_close()
                    db_execute(string , boolean - is_output)
                    reset_tables()
                    create_tables()
                    delete_tables()
                    
    @author - mah60
    @param - None
    @return - None
    """
    
    def __init__(self): 
        """
        @summary - connects to the wificounter database.
        @description - connects to the wificounter database and makes
                sure a connection is established.
        @author - mah60
        @param - None
        @return - None
        """
        print("database made")
        # connect to database
        self.db = db_con.connect(
              host="localhost",
              user="mah60", 
              passwd="xyz925krs",
              database="wificounter")
        # check connection was made
        output, cursor = self.db_execute("SHOW DATABASES;", True)
        if(len(output) > 0):
            print("connected to database")
        else:
            print("connection failed")
      
    def db_close(self):
        """
        @summary - disconnect from the wificounter database
        @description - disconnects from the database.
        @author - mah60
        @param - None
        @return - None
        """
        print("closed db")
        self.db.close()
        

    def db_execute(self, string, is_output):
        """
        Summary - executes commands to wificounter database.
        @description - executes commands to wificounter database.
                Only set is_output is true, if expecting return values. 
                Returns the cursor, if information is required from the cursor.
        @author - mah60
        @params - string - the command to be sent to the database.
        @params - is_output - boolean - is it expected for there to be output.
        @returns - [output , cursor] - output - list- list of return values from
                                                executions.
                                     - cursor - cursor object
        """
        # create cursor
        cursor = self.db.cursor()
        # execute command
        cursor.execute(string)
        output = []
        if(is_output):
            output = cursor.fetchall()
        self.db.commit()
        return [output, cursor]
    
            
    def reset_tables(self):
        """
        @summary - reset the database. 
        @description - sets all tables in the wificounter database to have no
                        records and the ids to be reset to zero.
        @author - mah60
        @param - None
        @return - None
        """
        # reset tables
        # turn off foreign key restraints # MAKE SURE IS TURNED BACK ON
        self.db_execute("SET FOREIGN_KEY_CHECKS = 0;", False)
        # get and reset tables
        tables = self.db_execute("SELECT table_name FROM information_schema.tables WHERE table_schema ='wificounter';", True)
        for t in tables[0]:
            cmd = "TRUNCATE " + t[0] + ";"      
            #print(cmd)
            self.db_execute(cmd, False)
        # turn on foreign keys
        curr = self.db_execute("SET FOREIGN_KEY_CHECKS = 1;", False)
    
    def create_tables(self):  
        """
        @summary - creates tables for the wificounter database.
        @description - creates tables for the wificounter database, 
                        will get commands from the create_tables.txt files
                        that holds the SQL commands to create 
                        the desired database.
        @author - mah60
        @param - None
        @return - None
        """
        # get command
        cmd = fr.read_txt_file("create_tables.txt", False).split(':')
        for c in cmd: # exectute all commands to create tables
            self.db_execute(c, False)
        
        
    def delete_tables(self):
        """
        @summary - deletes tables in the wificounter database.
        @description - will delete all tables in the wificounter database.
                        make sure to recreate tables before executing any 
                        other methods in this application. As almost every
                        function requires the tables to work.
        @author - mah60
        @param - None
        @return - None
        """
        # delete tables
        # turn off foreign key restraints # WARNING MAKE SURE TO TURN BACK ON
        self.db_execute("SET FOREIGN_KEY_CHECKS = 0;", False)
        tables = self.db_execute("SELECT table_name FROM information_schema.tables WHERE table_schema ='wificounter';", True)
        for t in tables[0]:
            cmd = "DROP TABLE " + t[0] + ";"        
            self.db_execute(cmd, False)
        # turn on foreign keys
        self.db_execute("SET FOREIGN_KEY_CHECKS = 1;", False)
        
    def is_tables(self):
        """
        @summary - check if required tables exist.
        @description - check if required tables exist. If not return
                        False.
        @param - None
        @return - boolean - True -  all required tables exist.
                            -  False - Missing a required table.
        """
        # tables to check
        tables = ["counters", "devices", "recordings", "devicerecords"]
        # get tables in database
        output = self.db_execute("SHOW TABLES;", True)[0]
        exist = True
        for t in tables: # check if all tables required in the database
            if(any(t in o[0] for o in output)):
                exist = True
            else: 
                print("Table : " + t + " : doesnt exist")
                return False
        return exist
