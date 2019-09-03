# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 14:59:53 2019

@author: Mhowa
"""

def read_txt_file(file, is_list):
    """
    @summary - read from a test file.
    @description - method will read from a text file and either return it
                    as a string or a list. 
                    If is_list is True the delimiter that will split the 
                    text file apart is ';' and '\n' will be removed.
    @author - mah60
    @param - file - string - file path location for the text file wanting
                            to be read.
    @param - is_list - boolean - if True return string will be split into
                               list with delimiter as ';' and no '\n' characters.
    @return - None
    """    
    # opens text file
    file_read = open(file, "r")
    contents = ""
    # read file
    if file_read.mode == "r":
        # convert return string to list if is_list is true
        if(is_list):
            contents = file_read.read().rstrip('\n').split(';')
        else:
            contents = file_read.read()
    
    return contents