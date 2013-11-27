# -*- coding: utf-8 -*-
import copy
import hashlib
import logging
import threading
import time
import win32file

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

""" * """


class Signal(object):
    """ ..

    """
    handlers = None

    def __init__(self):
        self.handlers = set()

    def __repr__(self):
        return "Event (%s) <%s>" % (self.num_handlers(),
                                    self.__class__.__name__, )

    def connect(self, handler):
        """ * """
        self.handlers.add(handler)
        logging.debug("%s: '%s' successfully added to handlers."
                      % (self.__class__.__name__,
                         handler, ))
        return self

    def disconnect(self, handler):
        """ * """
        try:
            self.handlers.remove(handler)
            logging.debug("%s: Handler '%s' successfully removed from event "\
                          "dispatcher."
                          % (self.__class__.__name__,
                             handler, ))
        except Exception as e:
            raise(e)
            logging.warning("%s: This handler is not currently registered "\
                            "with the event and can therefore not be detached."
                            % (self.__class__.__name__, ))
        return self

    def emit(self, *args, **kwargs):
        """ * """
        # if a handler does not exist anymore (because its bound object has
        # been deleted e.g., disconnect the handler.
        # Otherwise, call it.
        handlers_to_disconnect = []
        # create copy to protect if list changes (disconnect is called for
        # specific handler) while the loop runs
        handlers_copy = copy.copy(self.handlers)
        for handler in handlers_copy:
            try:
                handler(*args, **kwargs)
                logging.debug("%s: Handler %s successfully called."
                              % (self.__class__.__name__,
                                 handler, ))
            except RuntimeError as e:
                self.disconnect(handler)
                logging.debug("%s: Handler has thrown a RuntimeError and has "\
                              "been disconnected from event (%s): %s"
                              % (self.__class__.__name__,
                              handler,
                              e))
            except Exception as e:
                logging.warning("%s: Handler emission error: %s" %
                                (self.__class__.__name__,
                                 handler, ))
                raise e
        # disconnect
        for handler_to_disconnect in handlers_to_disconnect:
            self.disconnect(handler_to_disconnect)

    def num_handlers(self):
        """ * """
        return len(self.handlers)

    __iadd__ = connect
    __isub__ = disconnect
    __call__ = emit
    __len__ = num_handlers


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
                i1b = (0 - len(ending[0]))
                self.__unicode__ = self.__unicode__[:i1b] + ending[1]
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
                i1b = (0 - len(ending[0]))
                self.__unicode__ = self.__unicode__[:i1b] + ending[1]
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


class HashFile(object):
    """ ..

    :param str file_path: The absolute path to the file to be hashed.
    :param hashlib.HASH hash_obj: The hash object to be used for hashing. \
    This needs to be from Python's native ``hashlib`` module.
    """
    _file_path = None
    _hash_obj = None
    _data = None
    _data_lock = None
    _send_signal_handler = None
    _status = None
    # The smaller the value the higher the speed and the higher
    # the number of files, the higher the effective gain. Using no sleep at all
    # maximizes CPU usage for that thread (unthrottled while loops...)
    _sleeping_time = 0.005
    # Profiling tests have shown that the ideal buffer-size is a
    # size smaller but as close to the size of the hashed file itself as
    # possible. For memory-usage to not spike, the buffer should be limited to
    # a maximum value though.
    _buffer_size = 1024 * 1024 * 1
    _hash = None

    def __init__(self, file_path, **kwargs):
        """ ..

        """
        self._file_path = file_path
        # instantiate default _hash_obj
        self._hash_obj = kwargs.get("hash_obj", hashlib.sha512())
        self._send_signal_handler = kwargs.get("send_signal_handler", None)
        self._data = []
        self._data_lock = threading.Lock()
        self._status = 1

    def _read_data(self):
        """ ..

        """
        f = open(self._file_path, "rb")
        logging.debug("%s: Reading of data-stream started."
                     % (self.__class__.__name__, ))
        while True:
            if not len(self._data) > 2:
                logging.debug("%s: Reading more data... (%s)"
                              % (self.__class__.__name__, len(self._data), ))
                data = f.read(self._buffer_size)
                if len(data) == 0:
                    break
                with self._data_lock:
                    self._data.append(data)
            else:
                logging.debug("%s: Sleeping... (%s)"
                              % (self.__class__.__name__, len(self._data), ))
                time.sleep(self._sleeping_time)
        self._status = 0
        f.close()

    def _calc_hash(self):
        """ ..

        """
        logging.debug("%s: Hash-calculation started."
                     % (self.__class__.__name__, ))

        while self._status == 1 or len(self._data) > 0:
            if len(self._data) > 0:
                with self._data_lock:
                    data_block = self._data[0]
                self._hash_obj.update(data_block)
                with self._data_lock:
                    self._data.pop(0)
                # send signal
                if self._send_signal_handler:
                    self._send_signal_handler("updated",
                                              len(data_block),
                                              False,
                                              event_source="hash")
            else:
                time.sleep(self._sleeping_time)
        self._hash = self._hash_obj.hexdigest()

    def start(self):
        """ * """
        logging.debug("%s: Starting to hash file: %s"
                     % (self.__class__.__name__, self._file_path, ))
        # fire _data/_hash wrangler threads
        s = threading.Thread(target=self._read_data)
        t = threading.Thread(target=self._calc_hash)
        s.start()
        t.start()
        s.join()
        t.join()
        logging.debug("%s: Hash successfully calculated: %s"
                     % (self.__class__.__name__,
                        self._hash), )
        return self._hash


def format_data_size(size, lock_to=None):
    """ ..

    :param int size: The capacity in bytes to format.
    :param str lock_to: The unit to lock to. Possible values are:

        - bytes
        - KiB
        - MiB
        - GiB
        - TiB
        - PiB
        - EiB
        - ZiB
        - YiB
    :rtype: *str*

    This function formats a capacity ``size`` into the greatest unit that \
    gives it a value of >= 1. Examples:

        - *1023* would be formatted as *bytes*: *1023 bytes*
        - *1024* would be formatted as *KiB*: *1 KiB*
        - etc.

    ``lock_to`` locks the formatting to the chosen unit.
    """
    # format byte-size
    for x in ["bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]:
        if x == lock_to or \
            size < 1024.0:
            return "%3.2f %s" % (size, x, )
        size /= 1024.0
    return "%3.1f%s" % (size, 'YiB')


def get_drives(drive_types, ignore_a=True):
    """ ..

    :param list drive_types: The drive-types to list. Valid enum members are:

        - win32file.DRIVE_CDROM
        - win32file.DRIVE_FIXED
        - win32file.DRIVE_NO_ROOT_DIR
        - win32file.DRIVE_RAMDISK
        - win32file.DRIVE_REMOTE
        - win32file.DRIVE_REMOVABLE
        - win32file.DRIVE_UNKNOWN

    :param bool ignore_a: Whether or not to ignore drive-letter *A:\\\\*.
    :rtype: *list*

    Returns a list of drive root paths (i.e. drive letters, network paths) \
    available to the system, depending on the desired types passed in through \
    ``drive_types``.
    """
    # VALIDATE DATA
    # drive_types
    check = False
    if not isinstance(drive_types, (list, tuple, )):
        check = True
    else:
        for drive_type in drive_types:
            if not drive_type in [win32file.DRIVE_CDROM,
                                  win32file.DRIVE_FIXED,
                                  win32file.DRIVE_NO_ROOT_DIR,
                                  win32file.DRIVE_RAMDISK,
                                  win32file.DRIVE_REMOTE,
                                  win32file.DRIVE_REMOVABLE,
                                  win32file.DRIVE_UNKNOWN]:
                check = True
    if check:
        logging.warning("`drive_types` needs to be a list of "\
                        "`win32file.DRIVE_*` constants.")
        return False

    # scan drives-letters, assemble requested drive-root-paths
    drive_letters = [
                     "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
                     "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                     "W", "X", "Y", "Z"
                     ]
    # ignore drive letter A by default (still detects positively as removable
    # drive even if it doesn't physically exist in system.
    if ignore_a:
        drive_letters.pop(0)
    out = []
    for drive_letter in drive_letters:
        drive_letter += ":\\"
        if win32file.GetDriveTypeW(drive_letter) in drive_types:
            out.append(drive_letter)
    # out
    return out
