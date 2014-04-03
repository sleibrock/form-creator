#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__ = 'Steven'


class Rect(object):
    """
    Class to store rectangle information
    Stores (x,y,w,h), the type of Rect, the ID of the rect, and now the value of the rect
    """
    def __init__(self, x, y, w, h, idtag="", typerect="text", value=""):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.data = (x, y, w, h)
        self.idtag = idtag  # name tag of the Rect
        self.typerect = typerect  # default
        self.value = value  # used for check/radio boxes

    def __iter__(self):
        """
        The ability to unpack a rectangle into multiple functions is nice (via *rect)
        Normally you would use __iter__ for a collection of data
        but the only important data in a rectangle is it's positioning data
        """
        return self.data

    def __eq__(self, other):
        """
        The __eq__ method determines equality of one rect to another
        However this could be extended to normal lists/tuples as well if necessary
        """
        return self.data == other.data

    def collide(self, rect):
        """
        Collision code (not used in the main program)
        This doesn't take into calculation any offset data so it's not used
        Deprecated
        """
        x1, y1, w1, h1 = self.data
        x2, y2, w2, h2 = rect.data
        if all([x1 < x2 + w2,  x1+w1 > x2, y1 < y2+h2, y1+h1 > y2]):
                return True
        return False
#end