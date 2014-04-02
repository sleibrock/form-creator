#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__ = 'Steven'

from RectData import Rect
import random
from itertools import combinations
import wx


class DataTestApp(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.SetTitle(title)
        self.SetClientSize((800,600))
        self.view = RectDraw(self)
        self.button = wx.Button(self, 1, " Run Test ")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.view)
        sizer.Add(self.button)
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        sizer.Fit(self)
        self.Show(True)
        self.Bind(wx.EVT_BUTTON, self.on_press, self.button)

    def on_press(self, event):
        event.Skip()
        self.view.start_test()


class RectDraw(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.rects = set()
        self.Bind(wx.EVT_PAINT, self.onpaint)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        """Refresh info when app size changes"""
        self.Refresh()
        event.Skip()

    def start_test(self):
        # create rectanlges using random numbers
        self.rects = set()
        test_rects = []
        for x in range(100):
            x = random.randint(0, 800)
            y = random.randint(0, 800)
            w = random.randint(0, 800)
            h = random.randint(0, 800)
            test_rects.append(Rect(x, y, w, h))

        combos = combinations(test_rects, 2)
        for a, b in combos:
            if a.collide(b):
                self.rects.add(a)  # shouldn't have duplicates because it's a set
                self.rects.add(b)
        self.Refresh()
        print("len(s): {0}".format(len(self.rects)))

    def onpaint(self, event):
        event.Skip()
        print("painting")
        w, h = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.SetBrush(wx.Brush(wx.BLACK))
        dc.SetPen(wx.Pen(wx.RED, 2, style=wx.SOLID))

        for rect in self.rects:
            print(rect.data)
            dc.DrawRectangle(5, 5, 20, 20)
            dc.DrawRectangle(*rect.data)


if __name__ == "__main__":
    app = wx.App(False)
    DataTestApp(None, "DataTest")
    app.MainLoop()
#end
