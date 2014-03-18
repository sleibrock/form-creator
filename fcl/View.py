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
        self.idtag = ""  # name tag of the Rect
        self.typerect = "text"  # default

    def __iter__(self):
        return iter((self.x, self.y, self.w, self.h, self.idtag, self.typerect))

    def collide(self, other_rect):
        """
        Check if this rect collides against *other_rect
        """

        return True
        pass

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
        self.editmode = False  # don't let yourself go crazy on rectangle creation

        self.leftclick = False
        self.rightclick = False
        self.middleclick = False

        self.rects = []  # the rectangle storage
        self.image = None  # The bitmap variable
        self.init_click = (0, 0)
        self.offsetx, self.offsety = (0, 0)
        self.leftclick_topleft = (0, 0)
        self.leftclick_botright = (0, 0)
        self.displayrect = False  # mouse drag rect
        self.selrect = None  # selected rect

        # bindings
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.onpaint)
        self.Bind(wx.EVT_MOTION, self.motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.leftdown)
        self.Bind(wx.EVT_LEFT_UP, self.leftup)
        self.Bind(wx.EVT_RIGHT_DOWN, self.rightdown)
        self.Bind(wx.EVT_RIGHT_UP, self.rightup)
        self.Bind(wx.EVT_KEY_DOWN, self.keydown)

    def on_size(self, event):
        """Refresh info when app size changes"""
        self.Refresh()

    @staticmethod
    def createrect(init_click, end_click):
        """
        Create the rectangle from the positions
        x, y = init_click[0], init_click[1]
        w, h = end_click[0] - x, end_click[1] - y
        """
        x, y = init_click[0], init_click[1]
        w, h = end_click[0] - x, end_click[1] - y
        return tuple((x, y, w, h))

    def colliderectpos(self, pos):
        """
        Check the pos=(x,y) against all rects in the rect list
        """
        x, y = pos
        for R in self.rects:
            rx, ry, rw, rh = R.x + self.offsetx, R.y + self.offsety, R.w, R.h
            if all([x >= rx,  x <= rx + rw]):
                if all([y >= ry, y <= ry + rh]):
                    return R  # means it clicked a rectangle
        return None  # return none otherwise

    def colliderectrect(self, rect):
        """
        Check if *rect collides with any other rect in rect list
        """
        pass

    def deleteselectedrect(self):
        """
        Delete currently selected rectangle
        """
        if self.selrect is not None:
            print(str(self.selrect.data))
            for i, R in enumerate(self.rects):
                if R.data is self.selrect.data:
                    removal = i
            self.selrect = None
            self.rects.pop(removal)
        else:
            self.parent.SetStatusText("Can't find rectangle to delete")
        self.Refresh()

    def deleteallrects(self):
        """
        Delete all rects (shouldn't be very useful)
        """
        self.rects = []

    def applytype(self, Type):
        if self.selrect is not None:
            self.selrect.typerect = Type

    def applyname(self, Name):
        if self.selrect is not None:
            self.selrect.idtag = Name

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
                newx, newy = event.GetPosition()
                delta_x = self.init_click[0] - newx
                delta_y = self.init_click[1] - newy
                self.offsetx += delta_x
                self.offsety += delta_y
                self.init_click = (newx, newy)
        else:
            pass  # do nothing?
        self.Refresh()

    def keydown(self, event):
        """
        Mark certain actions to do basic tasks in the app
        """
        if event.GetKeyCode() in (wx.WXK_DELETE, wx.WXK_BACK):
            self.deleteselectedrect()
        event.Skip()

    def leftdown(self, event):
        self.leftclick = True
        pos = event.GetPosition()
        self.leftclick_topleft = pos
        self.leftclick_botright = pos  # fix minor issue to double-clicking
        r = self.colliderectpos(pos)
        if r is not None:
            # grab the rect that was clicked
            self.selrect = r
            self.parent.set_type(r.typerect)
            self.parent.idText.SetValue(r.idtag)
            self.parent.idText.SetFocus()
        else:
            # draw a new rectangle
            self.selrect = None
            self.displayrect = True
        self.Refresh()

    def leftup(self, event):
        event.Skip()
        self.leftclick = False
        if self.displayrect:
            # TODO: write a check to see if it collides with any other existing rectangles
            # make a rectangle, append it
            # We have to subtract the offsets to store the actual information
            # Then when drawing add the offsets
            x, y = self.leftclick_topleft[0] - self.offsetx, self.leftclick_topleft[1] - self.offsety
            x2, y2 = self.leftclick_botright[0] - self.offsetx, self.leftclick_botright[1] - self.offsety
            self.rects.append(Rect(*self.createrect((x, y), (x2, y2))))
            self.displayrect = False
        self.Refresh()

    def rightdown(self, event):
        event.Skip()
        self.rightclick = True
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.init_click = event.GetPosition()

    def rightup(self, event):
        event.Skip()
        self.rightclick = False
        self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        self.init_click = event.GetPosition()
        self.Refresh()

    def onpaint(self, event):
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
            dc.DrawBitmap(self.image, self.offsetx, self.offsety)
            # draw rectangles here etc
            # draw the left-click preview rectangle
            if self.displayrect:
                # draw the being-made rectangle
                dc.SetPen(wx.Pen(Preferences.displayRectangleBorder, 2, style=wx.DOT_DASH))
                dc.DrawRectangle(*self.createrect(self.leftclick_topleft, self.leftclick_botright))

            dc.SetPen(wx.Pen(Preferences.inactiveRectangleBorder, 1, style=wx.SOLID))
            for r in self.rects:
                dc.DrawRectangle(r.x + self.offsetx, r.y + self.offsety, r.w, r.h)
            if self.selrect is not None:
                dc.SetPen(wx.Pen(Preferences.highlightedRectangleBorder, 1, style=wx.SOLID))
                dc.DrawRectangle(self.selrect.x + self.offsetx, self.selrect.y + self.offsety,
                                 self.selrect.w, self.selrect.h)
        else:
            dc.SetPen(wx.Pen(wx.BLACK, 5))
            n = len(Preferences.noImgText)
            dc.DrawText(Preferences.noImgText, (w / 2)-n, (h / 2)-n)

# end