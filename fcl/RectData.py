#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__ = 'Steven'

#import unittest
import random
from itertools import combinations

import wx


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

#class TestRect(unittest.TestCase):
    #"""Unit case for Rect class"""
class RedrawColls(wx.Frame):
    def setUp(self):
        self.seq = range(1000)
        self.check = 0
        self.recs = []
        self.collrecs = []

    def create_rect(self):
        """
        Creates a rectangle with random placement and size.
        :rtype : rect
        """
        x = random.choice(self.seq)
        y = random.choice(self.seq)
        w = random.choice(self.seq)
        h = random.choice(self.seq)
        return Rect(x, y, w, h)

    def add_recs(self, x):
        """
        Adds a number of rectangles to 'recs' for testing.
        :param rect:
        """
        for i in range(0,x,1):
            self.recs.append(self.create_rect())

    def find_collision(self, x):
        """
        Checks the rectangles for collisions
        """
        self.add_recs(x)
        combos = combinations(self.recs, 2)

        for a, b in combos:
            if a.collide(b[1]):

                self.collrecs.append(a)
                self.collrecs.append(b)
                #self.collrecs.append([pair[0], pair[1]])
                #self.assertTrue(pair[0].collide(pair[1]))

    def disp_collisions(self):
        """
        displays collisons for inspection.
        """
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        dc.SetBrush(wx.Brush("0000FF000", style=wx.LINE))

        for rec in self.collrecs:
            dc.DrawRectangle(rec)

class DataTestApp(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.SetTitle(title)
        self.view = RectDraw(self)
        self.button = wx.Button(self, 1, " Run Test ")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.view)
        sizer.Add(self.button)
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        sizer.Fit(self)
        self.Bind(wx.EVT_BUTTON, self.button, self.on_press)

    def on_press(self, event):
        event.Skip()
        self.view.start_test()

class RectDraw(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.rects = set()

    def on_size(self, event):
        """Refresh info when app size changes"""
        self.Refresh()
        event.Skip()

    def start_test(self):
        # create rectanlges using random numbers
        test_rects = []
        for x in range(1000):
            x = random.randint(0, 800)
            y = random.randint(0, 800)
            w = random.randint(0, 800)
            h = random.randint(0, 800)
            test_rects.append(Rect(x, y, w, h))

        combos = combinations(test_rects)
        for a, b in combos:
            if a.collide(b):
                self.rects.append(a)  # shouldn't have duplicates because it's a set
                self.rects.append(b)

    def onpaint(self, event):
        event.Skip()
        w, h = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.SetBrush(wx.Brush("000000", style=wx.TRANSPARENT))
        dc.SetPen(wx.Pen(wx.RED, 2, style=wx.SOLID))

        for rect in self.rects:
            dc.DrawRectangle(*rect.data)



if __name__ == "__main__":
    app = wx.DataTestApp(False)
    app.MainLoop()
#end