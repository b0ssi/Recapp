# -*- coding: utf-8 -*-

###############################################################################
##    bs.messages.general                                                    ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Mar 26, 2013                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################


def general_error(e):
    exception_msg = "A general error occurred: %s" % (e, )
    exit_msg = "EXIT: Operation could not be successfully completed; system "\
               "needs to exit."

    out = [exception_msg, exit_msg]
    return out
