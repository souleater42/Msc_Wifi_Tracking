# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 18:22:42 2019

@author: Mhowa
"""

import mysql.connector

class DBManager:
    
    def __init__(self): 
        print("database made")
        db = mysql.connector.connect(
                host="Database/trackerDB",
                user="mah60",
                passwd="uisdv857"
                )
        
        cursor = db.cursor()
        
        cursor.execute("SHOW DATABASES;")
        
        
    def create_db(self):
        print("")
        