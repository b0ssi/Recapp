# -*- coding: utf-8 -*-
import binascii
import hashlib
import itertools
import math
import os
import random
import sqlite3
import time

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


#time_start = time.time()
#conn = sqlite3.connect("Z:\\test.sqlite")
#conn.execute("DROP TABLE test")
#conn.execute("CREATE TABLE test ('inode' INTEGER)")
#conn.commit()
#for folder_path, folders, files in os.walk("Z:\\files"):
#    for file in files:
#        inode = os.stat(os.path.join(folder_path, file)).st_ino
#        conn.execute("INSERT INTO test VALUES (?)", (inode, ))
#        print(os.path.join(folder_path, file))
#print(time.time() - time_start)
#conn.commit()
#print(time.time() - time_start)

#i = 0
#for inode in (x[0] for x in conn.execute("SELECT * FROM test").fetchall()):
#    if len(conn.execute("SELECT * FROM test WHERE inode = ?", (inode, )).fetchall()) > 1:
#        print("NOT GOOD: %s" % (inode, ))
#    print(i)
#    i += 1


#print("Finding duplicates...")
#time_start = time.time()
#print(any(x == y for x, y in itertools.combinations(INODES, 2)))
#print(time.time() - time_start)

#for INODE in INODES:
#    if INODE not in INODES_2:
#        INODES_2.append(INODE)
#    else:
#        print(INODE)
#    print(len(INODES_2))



#print("DONE")

###############################################################################

def write_file_random_content(target_directory_path, file_size_min, file_size_max):
    target_file_path = os.path.join(target_directory_path, "")
    file_size_rand = random.randint(file_size_min, file_size_max)
    if not os.path.isdir(target_directory_path):
        os.makedirs(target_directory_path)

    while os.path.isfile(target_file_path) or\
        os.path.isdir(target_file_path):
        name = str(random.randint(1000000000000, 9999999999999))
        target_file_path = os.path.join(os.path.split(target_directory_path)[0], name)

    contents = random.randint(1000000000000000, 9999999999999999)
    contents = str(contents) * 64 * file_size_rand

    contents = bytes(contents, "utf-8")

    with open(target_file_path, "wb") as out:
        out.write(contents)

for i in range(1):
    for j in range(1):
        write_file_random_content("Y:\\_TMP\\bsTest\\s5\\%s\\" % i, 100 * pow(2, 10), 100 * pow(2, 10))



###############################################################################
