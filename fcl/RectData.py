#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__ = 'Steven'


class Rect(object):
    """
    Class to store rectangle information
    Stores (x,y,w,h), the type of Rect, and the ID of the rect
    """
    def __init__(self, x, y, w, h, idtag="", typerect="text", value=""):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.data = (x, y, w, h)
        self.idtag = idtag  # name tag of the Rect
        self.typerect = typerect  # default
        self.value = value  # used for check/radio boxes

    def __iter__(self):
        return self.data

    def __eq__(self, other):
        return self.data == other.data

    def collide(self, rect):
        """Collision code"""
        x1, y1, w1, h1 = self.data
        x2, y2, w2, h2 = rect.data
        if all([x1 < x2 + w2,  x1+w1 > x2, y1 < y2+h2, y1+h1 > y2]):
                return True
        return False
#end