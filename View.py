#!/usr/bin/python
#-*- coding: utf-8 -*-

__author__ = 'Steven'

import wx

"""
View data classes and objects
functionality of drawing and data management here
"""
class Rect(object):
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.data = (x, y, w, h)
        self.IDtag = ""  # name tag of the Rect
        self.typeRect = "text"  # default

    def __iter__(self):
        return iter((self.x, self.y, self.w, self.h, self.IDtag, self.typeRect))

class Preferences(object):
    """
    Class to store application preferences
    Load from JSON format preferrably (if really necessary)
    """
    version = "0.1"
    highlightedRectangleBorder = wx.GREEN
    displayRectangleBorder = wx.RED
    inactiveRectangleBorder = wx.BLUE
    noImgText = "Load an image to process"

class View(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        # Keep track of the parent
        self.parent = parent
        self.editMode = False  # don't let yourself go crazy on rectangle creation

        self.leftclick = False
        self.rightclick = False
        self.middleclick = False

        self.rects = []  # the rectangle storage
        self.image = None  # The bitmap variable
        self.init_click = (0, 0)
        self.offsetX, self.offsetY = (0, 0)
        self.leftclick_topleft = (0, 0)
        self.leftclick_botright = (0, 0)
        self.displayRect = False  # mouse drag rect
        self.selRect = None  # selected rect

        # bindings
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_MOTION, self.motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.leftDown)
        self.Bind(wx.EVT_LEFT_UP, self.leftUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.rightDown)
        self.Bind(wx.EVT_RIGHT_UP, self.rightUp)
        self.Bind(wx.EVT_KEY_DOWN, self.keyDown)

    def calcBoundaries(self):
        """
        Calculate image moving properties
        (Might be used later, who knows)
        """
        if self.image is not None:
            self.width = self.image.GetWidth()
            self.height = self.image.GetHeight()
        self.maxX, self.maxY = self.GetClientSize()
        self.minX, self.minY = 0, 0

    def onSize(self, event):
        """Refresh info when app size changes"""
        event.Skip()
        self.Refresh()
        self.calcBoundaries()

    def createRect(self, init_click, end_click):
        """
        Create the rectangle from the positions
        x, y = init_click[0], init_click[1]
        w, h = end_click[0] - x, end_click[1] - y
        """
        x, y = init_click[0], init_click[1]
        w, h = end_click[0] - x, end_click[1] - y
        return tuple((x, y, w, h))

    def collideRectPos(self, pos):
        """
        Check the pos=(x,y) against all rects in the rect list
        """
        x, y = pos
        for R in self.rects:
            rx, ry, rw, rh = R.x + self.offsetX, R.y + self.offsetY, R.w, R.h
            if all([x >= rx,  x <= rx + rw]):
                if all([y >= ry, y <= ry + rh]):
                    return R  # means it clicked a rectangle
        return None  # return none otherwise

    def collideRectRect(self, rect):
        """
        Check if *rect collides with any other rect in rect list
        """
        pass

    def deleteSelectedRect(self):
        """
        Delete currently selected rectangle
        """
        if self.selRect is not None:
            print(str(self.selRect.data))
            for i, R in enumerate(self.rects):
                if R.data is self.selRect.data:
                    removal = i
            self.selRect = None
            self.rects.pop(removal)
        else:
            self.parent.SetStatusText("Can't find rectangle to delete")
        self.Refresh()

    def deleteAllRects(self):
        """
        Delete all rects (shouldn't be very useful)
        """
        self.rects = []
        event.Skip()

    def applyType(self, Type):
        if self.selRect is not None:
            self.selRect.typeRect = Type

    def applyName(self, Name):
        if self.selRect is not None:
            self.selRect.IDtag = Name

    def motion(self, event):
        # The big mouse event determiner
        if self.leftclick and self.rightclick:
            # both left and right
            pass
        elif self.leftclick and not self.rightclick:
            # left click only
            self.leftclick_botright = event.GetPosition()
        elif self.rightclick and not self.leftclick:
            # Move the image using offsets
            if self.image is not None:
                newX, newY = event.GetPosition()
                delta_x = self.init_click[0] - newX
                delta_y = self.init_click[1] - newY
                self.offsetX += delta_x
                self.offsetY += delta_y
                self.init_click = (newX, newY)
        else:
            pass  # do nothing?
        self.Refresh()

    def keyDown(self, event):
        """
        Mark certain actions to do basic tasks in the app
        """
        if event.GetKeyCode() in (wx.WXK_DELETE, wx.WXK_BACK):
            self.deleteSelectedRect()
        event.Skip()

    def leftDown(self, event):
        self.leftclick = True
        pos = event.GetPosition()
        self.leftclick_topleft = pos
        self.leftclick_botright = pos  # fix minor issue to double-clicking
        R = self.collideRectPos(pos)
        if R is not None:
            # grab the rect that was clicked
            self.selRect = R
            self.parent.setTypeText(R.typeRect)
            self.parent.idText.SetValue(R.IDtag)
            self.parent.idText.SetFocus()
        else:
            # draw a new rectangle
            self.selRect = None
            self.displayRect = True
        self.Refresh()

    def leftUp(self, event):
        event.Skip()
        self.leftclick = False
        if self.displayRect:
            # TODO: write a check to see if it collides with any other existing rectangles
            # make a rectangle, append it
            # We have to subtract the offsets to store the actual information
            # Then when drawing add the offsets
            x, y = self.leftclick_topleft[0] - self.offsetX, self.leftclick_topleft[1] - self.offsetY
            x2, y2 = self.leftclick_botright[0] - self.offsetX, self.leftclick_botright[1] - self.offsetY
            self.rects.append(Rect(*self.createRect((x, y), (x2, y2))))
            self.displayRect = False
        self.Refresh()

    def rightDown(self, event):
        event.Skip()
        self.rightclick = True
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.init_click = event.GetPosition()

    def rightUp(self, event):
        event.Skip()
        self.rightclick = False
        self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        self.init_click = event.GetPosition()
        self.Refresh()

    def onPaint(self, event):
        """
        The main Drawing function
        All visuals are done here
        """
        w, h = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.SetBrush(wx.Brush("000000", style=wx.TRANSPARENT))

        if self.image is not None:
            # draw the new bitmap
            dc.DrawBitmap(self.image, self.offsetX, self.offsetY)
            # draw rectangles here etc
            # draw the left-click preview rectangle
            if self.displayRect:
                # draw the being-made rectangle
                dc.SetPen(wx.Pen(Preferences.displayRectangleBorder, 2, style=wx.DOT_DASH))
                dc.DrawRectangle(*self.createRect(self.leftclick_topleft, self.leftclick_botright))

            dc.SetPen(wx.Pen(Preferences.inactiveRectangleBorder, 1, style=wx.SOLID))
            for R in self.rects:
                dc.DrawRectangle(R.x + self.offsetX, R.y + self.offsetY, R.w, R.h)
            if self.selRect is not None:
                dc.SetPen(wx.Pen(Preferences.highlightedRectangleBorder, 1, style=wx.SOLID))
                dc.DrawRectangle(self.selRect.x + self.offsetX, self.selRect.y + self.offsetY,
                                 self.selRect.w, self.selRect.h)
        else:
            dc.SetPen(wx.Pen(wx.BLACK, 5))
            n = len(Preferences.noImgText)
            dc.DrawText(Preferences.noImgText, (w / 2)-n, (h / 2)-n)

# end