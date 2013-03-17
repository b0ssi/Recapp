# -*- coding: utf-8 -*-
import random

###############################################################################
##    [NAME]                                                                 ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2012 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Nov 25, 2012                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################

#import os
#
#
#class Event(object):
#    def __init__(self):
#        self.handlers = set()
#
#    def handle(self, handler):
#        self.handlers.add(handler)
#        return self
#
#    def unhandle(self, handler):
#        try:
#            self.handlers.remove(handler)
#        except:
#            raise ValueError("Handler is not handling this event, so can not "\
#                             "unhandle it.")
#        return self
#
#    def fire(self, *args, **kargs):
#        for handler in self.handlers:
#            handler(*args, **kargs)
#
#    def get_handler_count(self):
#        return len(self.handlers)
#
#    __iadd__ = handle
#    __isub__ = unhandle
#    __call__ = fire
#    __len__ = get_handler_count
#
#
#class FileWatcher(object):
#    def __init__(self):
#        self.file_changed = Event()
#
#    def watch_files(self):
#        source_path = os.path.realpath("Z:/test")
#        self.file_changed(source_path)
#
#
#def log_file_change(source_path):
#    print("%r changed." % (source_path,))
#
#
#def log_file_change_2(x):
#    print(x)
#
#watcher = FileWatcher()
#watcher.file_changed += log_file_change
#watcher.file_changed += log_file_change_2
#watcher.watch_files()

#file_in = os.path.realpath("Z:\\test.FVA")
#file_out = os.path.realpath("Z:\\out.txt")

#    import os
#    import re
#
#    #file_in = os.path.realpath("Z:/in.txt")
#    #file_out = os.path.realpath("Z:/out.txt")
#
#
#    file_in = os.path.realpath("path/to/log_file.txt")
#    file_out = os.path.realpath("path/to/output_file.txt")
#
#    def extract_lines():
#        with open(file_in, "r") as f_in:
#            for line in f_in.readlines():
#                res = re.search("(PUT_LOG\()(.*)(\)\;)", line)
#                for segment in res.group(2).split(", "):
#                    print(segment)
#
#    extract_lines()

###############################################################################
#
#import os
#import re
#
#
#def extract_lines(file_in, file_out, strings_to_filter):
#    with open(file_in) as f_in, open(file_out, "a+") as f_out:
#        for line in f_in:
#            res = re.search("(PUT_LOG\()(.*)(\)\;)", line)
#            if res is not None:
#                i = 0
#                for segment in res.group(2).split(","):
#                    segment = segment.strip()
#                    if segment in strings_to_filter and i < 2:
#                        print(segment, file=f_out)
#                        i += 1
#
#extract_lines(
#              os.path.realpath("Z:/in.txt"),
#              os.path.realpath("Z:/out.txt"),
#              [
#               "CAPTIVE_EXECUTE_CMD",
#               "CAPTIVE_EXECUTE_CMD_FAILED",
#               "CAPTIVE_RECVD_SIGCHLD",
#               "LOG_LEVEL_DEBUG",
#               "LOG_LEVEL_DEBUG_ERR"
#               ]
#              )
#
###############################################################################
