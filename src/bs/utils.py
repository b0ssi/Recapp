# -*- coding: utf-8 -*-

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
