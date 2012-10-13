'''
Tests for the users module.

Created on Sep 22, 2012

@author: fryckbos
'''
import unittest
import os

from users import UserController

class UserControllerTest(unittest.TestCase):
    """ Tests for UserController. """

    FILE = "test.db"
    
    def setUp(self): #pylint: disable-msg=C0103
        """ Run before each test. """
        if os.path.exists(UserControllerTest.FILE):
            os.remove(UserControllerTest.FILE)
    
    def tearDown(self): #pylint: disable-msg=C0103
        """ Run after each test. """
        if os.path.exists(UserControllerTest.FILE):
            os.remove(UserControllerTest.FILE)

    def __get_controller(self):
        """ Get a UserController using FILE. """
        return UserController(UserControllerTest.FILE,
                              { 'username' : 'om', 'password' : 'pass' }, 10)

    def test_empty(self):
        """ Test an empty database. """
        user_controller = self.__get_controller()
        self.assertEquals(None, user_controller.login("fred", "test"))
        self.assertEquals(False, user_controller.check_token("some token 123"))
        self.assertEquals(None, user_controller.get_role("fred"))
    
        token = user_controller.login("om", "pass")
        self.assertNotEquals(None, token)
        
        self.assertTrue(user_controller.check_token(token))
    
    def test_all(self):
        """ Test all methods of UserController. """
        user_controller = self.__get_controller()
        user_controller.create_user("fred", "test", "admin", True)
        
        self.assertEquals(None, user_controller.login("fred", "123"))
        self.assertFalse(user_controller.check_token("blah"))
        
        token = user_controller.login("fred", "test")
        self.assertNotEquals(None, token)
        
        self.assertTrue(user_controller.check_token(token))
        self.assertFalse(user_controller.check_token("blah"))
        
        self.assertEquals("admin", user_controller.get_role("fred"))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()