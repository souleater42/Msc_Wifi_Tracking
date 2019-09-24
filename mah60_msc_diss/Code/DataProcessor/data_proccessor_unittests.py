# -*- coding: utf-8 -*-
"""
@author mah60
@version - 0.1 - created test suite and test case for visualisation manager. 18/09/2019; 

"""
     
import unittest as ut
import visualisation_manager
import db_manager as dbm


class TestVisualisationManager(ut.TestCase):
    
    def runTest(self):
        """
        @summary - runs tests for VisualisationManager.
        @description - will run the unit tests for VisualisationManager
        @author - mah60
        @param - None
        @return - None
        """
        self.db = dbm.DBManager()
        self.vm = visualisation_manager.VisualisationManager(self.db)
        self.test_convert_rssi_to_distance()
        self.test_get_counter_labels()
        self.db.db_close()
    
    def test_convert_rssi_to_distance(self):
        """
        @summary - test convert_rssi_to_distance.
        @description - tests if convert_rssi_to_distance works. Test if
                        -70 is equal to one.
        @author - mah60
        @param - None
        @return - None
        """
        dist = self.vm.convert_rssi_to_distance(-70, 2)
        self.assertEqual(dist, 1)
        
    def test_get_counter_labels(self):
        """
        @summary - test get_counter_labels().
        @description - tests if get_counter_labels() works. Test if
                        labels are made correctly.
        @author - mah60
        @param - None
        @return - None
        """
        counters = [(1, "AB", -70), (1, "CD", -80), (1, "AB", -70)]
        result = ['Session 1 : AB', 'Session 1 : CD', 'Session 2 : AB']
        output =  self.vm.get_counter_labels(counters)
        self.assertEqual(output, result)
            


def main():
    """
    @summary - run test suite for Data Processor.
    @description - will run test suite of all tests in the DataProccessor.
    @author - mah60
    @param - None
    @return - None
    """
    # initialize the test suite
    loader = ut.TestLoader()
    suite  = ut.TestSuite()
    # add tests to the test suit
    suite.addTest(TestVisualisationManager())
    # initialize a runner, pass it your suite and run it
    runner = ut.TextTestRunner(verbosity=3)
    result = runner.run(suite)
    
if __name__ == "__main__":
    main()
            