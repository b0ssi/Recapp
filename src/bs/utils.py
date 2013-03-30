# -*- coding: utf-8 -*-
import hashlib
import logging
import os
import sys
import threading
import time

###############################################################################
##    utils                                                                  ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Mar 12, 2013                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################


class Event(object):
    """
    *
    """
    def __init__(self):
        self.handlers = set()

    def __repr__(self):
        return "Event (%s) <%s>" % (self.num_handlers(),
                                    self.__class__.__name__, )

    def add_handler(self, handler):
        self.handlers.add(handler)
        print("'%s' successfully added to handlers." % (handler,))
        return self

    def remove_handler(self, handler):
        try:
            self.handlers.remove(handler)
            print("'%s' successfully removed from handlers." % (handler,))
        except:
            print("This handler is not currently registered with the event "\
                  "and can therefore not be detached.")
        return self

    def fire_handlers(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)

    def num_handlers(self):
        return len(self.handlers)

    __iadd__ = add_handler
    __isub__ = remove_handler
    __call__ = fire_handlers
    __len__ = num_handlers

#class MyTrigger(object):
#    def __init__(self):
#        self.event = Event()
#
#    def click(self, arg):
#        self.event(arg)
#
## install event listener on object
#my_trigger = MyTrigger()
## add event(s)
#my_trigger.event += print
#my_trigger.event += testionation
## fire the trigger
#my_trigger.click("boooo!!!")


class BSString(object):
    """
    Extends the built-in str() with additional methods.
    """
    def __init__(self, name=""):
        super(BSString, self).__init__()

        self.__unicode__ = name

    def __repr__(self):
        return self.__unicode__

    def endswith(self, *args, **kwargs):
        """
        Returns `True` if self.__unicode__ ends with passed string, `False`
        otherwise.
        """
        if self.__unicode__[0 - len(args[0]):] == args[0]:
            return True
        else:
            return False

    def pluralize(self):
        """
        Pluralizes self.__unicode__ and returns self.
        """
        endings = [
                   ("e", "es"),
                   ("t", "ts"),
                   ("us", "i"),
                   ("um", "a")
                   ]
        for ending in endings:
            if self.endswith(ending[0]):
                self.__unicode__ = self.__unicode__[:(0-len(ending[0]))] + ending[1]
        return self

    def singularize(self):
        """
        Singularizes self.__unicode__ and returns self.
        """
        endings = [
                   ("s", ""),
                   ("ts", "t"),
                   ("i", "us"),
                   ("a", "um")
                   ]
        for ending in endings:
            if self.endswith(ending[0]):
                self.__unicode__ = self.__unicode__[:(0-len(ending[0]))] + ending[1]
        return self

    def capitalize(self):
        """
        Capitalizes self.__unicode__ and returns self.
        """
        self.__unicode__ = self.__unicode__.capitalize()
        return self

    def lower(self):
        """
        Lowers self.__unicode__ and returns self.
        """
        self.__unicode__ = self.__unicode__.lower()
        return self


def formatDirSize(size, lock_to=None):
    """
    *
    size: int: bytes
    lock_to: string: name of unit (e.g. "MiB") and returns value not
    higher than chosen unit.
    """
    # format byte-size
    for x in ["bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]:
        if x == lock_to or \
            size < 1024.0:
            return "%3.2f %s" % (size, x, )
        size /= 1024.0
    return "%3.1f%s" % (size, 'YiB')


class HashFile(object):
    """
    *
    _sleeping_time: The smaller the value the higher the speed and the higher
    the number of files, the higher the effective gain. Using no sleep at all
    maximizes CPU usage for that thread (unthrottled while loops...)

    _buffer_size: Profiling tests have shown that the ideal buffer-size is a
    size smaller but as close to the size of the hashed file itself as
    possible. For memory-usage to not spike, the buffer should be limited to
    a maximum value though.
    """
    _file_path = ""
    _hash_obj = None
    _data = []
    _status = 0
    _sleeping_time = 0.005
    _buffer_size = 1024 * 1 * 1
    _hash = ""

    def __init__(self, file_path, hash_obj=None):
        """
        *
        """
        self._file_path = file_path
        # instantiate default _hash_obj
        if not hash_obj:
            self._hash_obj = hashlib.sha512()

    def _read_data(self):
        """
        *
        """
        f = open(self._file_path, "rb")
        logging.info("Reading of _data-stream started.")
        while True:
            if not len(self._data) > 2:
                logging.debug("_read_data(): Reading more _data... (%s)"
                              % (len(self._data), ))
                data = f.read(self._buffer_size)
                self._data.append(data)
                if not data:
                    break
            else:
                logging.debug("_read_data(): Sleeping... (%s)"
                              % (len(self._data), ))
                time.sleep(self._sleeping_time)
        self._status = 1

    def _calc_hash(self):
        """
        *
        """
        logging.info("Hash-calculation started.")
        file_hash = self._hash_obj
        time_start = time.time()

        while self._status == 0:
            if len(self._data) > 0:
                logging.debug("_calc_hash(): Updating _hash... (%s)" % (len(self._data), ))
                file_hash.update(self._data[0])
                self._data.pop(0)
            else:
                logging.debug("_calc_hash(): Sleeping... (%s)" % (len(self._data), ))
                time.sleep(self._sleeping_time)
        self._hash = file_hash.hexdigest()
#        print(time.time() - time_start)

    def start(self):
        """
        *
        """
        logging.info("Starting to _hash file: %s" % (self._file_path, ))
        # fire _data/_hash wrangler threads
        s = threading.Thread(target=self._read_data).start()
        t = threading.Thread(target=self._calc_hash).start()
        t.join()
        return(self._hash)
