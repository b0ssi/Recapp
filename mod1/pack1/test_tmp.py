# -*- coding: utf-8 -*-
from unittest.mock import MagicMock
import unittest
from mod1.pack1 import tmp

################################################################################
##    mod1.pack1.test_tmp                                                               ##
################################################################################
################################################################################
##    Author:         Bossi                                                 ##
##                    © 2013 All rights reserved                              ##
##                    www.isotoxin.de                                         ##
##                    frieder.czeschla@isotoxin.de                            ##
##    Creation Date:  Mar 10, 2013                                                 ##
##    Version:        0.0.000000                                              ##
##                                                                            ##
##    Usage:                                                                  ##
##                                                                            ##
################################################################################



#class ProductionClass(object):
#    pass
#
#class TestProductionClass(unittest.TestCase):
#    def test_do_something(self):
#        thing = ProductionClass()
#        thing.method = MagicMock(return_value=3)
#        thing.method(3, 4, 5, key='value')
#        thing.method.assert_called_with(3, 4, 5, key='value')

class TestFoo(unittest.TestCase):
    def test_foo(self):
        foo = tmp.Foo()
        with self.assertRaises(SystemExit):
            foo.foo()