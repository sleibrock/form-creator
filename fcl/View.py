#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__ = 'Steven'
import wx

from RectData import Rect
from Preferences import Preferences


class View(wx.Panel):
    """
    The Image Viewing class
    Blits an image onto the screen and allows you to draw rectangles over it
    Rect data is exported in JSON format for later use
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)  # super
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        # Keep track of the parent
        self.parent = parent  # parent window/frame reference
        self.leftclick = False  # three state variables of mouse pressing
        self.rightclick = False
        self.middleclick = False
        self.rects = []  # the rectangle storage
        self.image = None  # The bitmap variable
        self.init_click = (0, 0)  # initial click to store mouse position
        self.offsetx, self.offsety = (0, 0)  # offset stored to transform rectangles into the viewing plane
        self.leftclick_topleft = (0, 0)  # position stored when mouseclick is pressed
        self.leftclick_botright = (0, 0)  # position stored when mouseclick is released
        self.displayrect = False  # mouse drag rect
        self.selrect = None  # selected rect
        self.valuedict = {}  # dictionary used to calculate values of radios/checkboxes
        self.selectedrects = []  # list used to store group selection of rectangles

        # bindings
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.onpaint)
        self.Bind(wx.EVT_MOTION, self.motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.leftdown)
        self.Bind(wx.EVT_LEFT_UP, self.leftup)
        self.Bind(wx.EVT_RIGHT_DOWN, self.rightdown)
        self.Bind(wx.EVT_RIGHT_UP, self.rightup)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.middown)
        self.Bind(wx.EVT_MIDDLE_UP, self.midup)

    def on_size(self, event):
        """Refresh info when app size changes"""
        self.Refresh()
        event.Skip()

    @staticmethod
    def createrect(init_click, end_click):
        """
        Create the rectangle from the positions
        x, y = init_click[0], init_click[1]
        w, h = end_click[0] - x, end_click[1] - y
        """
        x, y = init_click[0], init_click[1]
        w, h = abs(end_click[0] - x), abs(end_click[1] - y)
        return tuple((x, y, w, h))

    @staticmethod
    def generate_data(rects):
        """Static dictionary generator"""
        rmap_data = {}
        for i, r in enumerate(rects):
            d = {"x": r.x, "y": r.y, "w": r.w, "h": r.h,
                 "idtag": r.idtag, "typerect": r.typerect, "value": r.value}
            rmap_data["rect"+str(i)] = d
        return rmap_data

    def generate_rmap(self):
        """Generate a JSON RMAP dictionary"""
        return View.generate_data(self.rects)

    def colliderectpos(self, pos):
        """
        Check the pos=(x,y) against all rects in the rect list
        """
        x, y = pos
        for R in self.rects:
            # offset rectangle positions into proper plane
            rx, ry, rw, rh = R.x + self.offsetx, R.y + self.offsety, R.w, R.h
            if all([x >= rx, x <= rx + rw, y >= ry, y <= ry + rh]):
                return R  # means it clicked a rectangle
        return None  # return none otherwise

    def colliderects(self, rect):
        """
        Check if *rect collides with any other rect in rect list
        """
        x1, y1, w1, h1 = rect.data
        for R in self.rects:
            # don't use offsets here, as it was invalid
            x2, y2, w2, h2 = R.data
            if all([x1 < x2 + w2,  x1+w1 > x2, y1 < y2+h2, y1+h1 > y2]):
                return True
        return False

    def deleteselectedrect(self):
        """
        Delete currently selected rectangle
        We don't have a __cmp__ for Rects so use another deletion method
        Also you shouldn't remove from a list while iterating through it
        """
        removal = None
        if self.selrect is not None:
            for i, R in enumerate(self.rects):
                if R.data == self.selrect.data:
                    removal = i
            self.selrect = None
            if removal is not None:
                self.rects.pop(removal)
        else:
            self.parent.SetStatusText(Preferences.cantFindRectangle)
        self.Refresh()

    def deleteallrects(self):
        """
        Delete all rects (shouldn't be very useful)
        Use in emergencies
        """
        self.rects = list()

    def applytype(self, typerect):
        """
        Apply the type to the current selected rect(s)
        Now applies to all rectangles stored in mass selection
        """
        if self.selrect is not None:
            self.selrect.typerect = typerect
        if len(self.selectedrects):
            for r in self.selectedrects:
                r.typerect = typerect

    def applyname(self, name):
        """Apply the name to the current selected rect(s)"""
        if self.selrect is not None:
            self.selrect.idtag = name
        if len(self.selectedrects):
            for i, r in enumerate(self.selectedrects):
                r.idtag = name + str(i+1)

    def update_values(self):
        """Add values to multiple input types"""
        values = {}
        for rect in self.rects:
            if rect.typerect in ("checkbox", "radio"):
                if rect.idtag in values:
                    rect.value = values[rect.idtag]
                    values[rect.idtag] += 1
                else:
                    rect.value = 0
                    values[rect.idtag] = 1

    def read_json(self, json):
        """
        Read the json.loads data, convert to Rects
        Keep rectangles with no ID tags to save progress/work on unnameds
        """
        for i, k in json.items():
            print("{0} - {1}".format(i, k))
            data = (k["x"], k["y"], k["w"], k["h"], k["idtag"], k["typerect"], k["value"])
            rect_addition = Rect(*data)
            self.rects.append(rect_addition)

    def clear_all(self):
        """
        Clear all data from the view (basically emptying it out
        """
        self.image = None
        self.selrect = None
        self.displayrect = None
        self.offsetx, self.offsety = 0, 0
        self.rects = []
        self.Refresh()  # redraw with onpaint

    @staticmethod
    def filter_list(rects, minwidth=10, minheight=10):
        """Static filter a list (used to not ruin stored data)"""
        filt = lambda r: all([r.w > minwidth, r.h > minheight])
        return [Rectangle for Rectangle in rects if filt(Rectangle)]

    @staticmethod
    def clean_list(rects):
        """Static clean list method"""
        filt = lambda r: len(r.idtag.strip())
        return [Rectangle for Rectangle in rects if filt(Rectangle)]

    def filter_rects(self, minwidth=10, minheight=10):
        """Filter any bad rects that are just too tiny"""
        self.rects = View.filter_list(self.rects, minwidth, minheight)

    def cleanup(self):
        """Clean up rects that don't have name tags"""
        self.rects = View.clean_list(self.rects)

    def statistics(self):
        """
        Return statistics of the current View
        (total # of rects, # of text rects, # of checks, # radios, # of named)
        """
        # Redundant code to avoid using if-statements (they're boring)
        types = [rect.typerect for rect in self.rects]
        s = len(types)
        t = len([string for string in types if string == "text"])
        c = len([string for string in types if string == "checkbox"])
        r = len([string for string in types if string == "radio"])
        n = len([nametag for nametag in self.rects if nametag.idtag != ""])
        return tuple((s, t, c, r, n))

    ###########################################  Event handler basic functions
    def motion(self, event):
        """
        Function for event managing mouse motion
        """
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

    def leftdown(self, event):
        """
        Leftclick-down event
        Currently positions are absolute so rectangle width/height can never be negative
        Unless sorting is implemented this won't be changed
        """
        # TODO: ensure the mouse positions are in order (otherwise it screws up)
        self.leftclick = True
        pos = event.GetPosition()
        self.leftclick_topleft = pos
        self.leftclick_botright = pos  # fix minor issue to double-clicking
        r = self.colliderectpos(pos)
        self.selectedrects = []
        if r is not None:
            # grab the rect that was clicked
            self.selrect = r
            self.parent.set_type(r.typerect)
            self.parent.idtext.SetValue(r.idtag)
            self.parent.idtext.SetFocus()
            self.parent.idtext.SetInsertionPointEnd()
            self.parent.idtext.SelectAll()
        else:
            # draw a new rectangle
            self.selrect = None
            self.displayrect = True
        self.Refresh()

    def leftup(self, event):
        """
        Create a new rectangle, test if it hits anything, append it
        Subtract the image panning offsets for HTML purposes
        """
        event.Skip()
        self.leftclick = False
        if self.displayrect:
            x, y = self.leftclick_topleft[0] - self.offsetx, self.leftclick_topleft[1] - self.offsety
            x2, y2 = self.leftclick_botright[0] - self.offsetx, self.leftclick_botright[1] - self.offsety
            r = Rect(*self.createrect((x, y), (x2, y2)))
            if not self.colliderects(r):
                self.rects.append(r)
                self.selrect = r  # upon creation of a rect, set focus to text
                self.parent.set_type(r.typerect)
                self.parent.idtext.SetValue(r.idtag)
                self.parent.idtext.SetFocus()
            else:
                # don't use the rectangle we just made
                pass
            self.displayrect = False
        self.Refresh()

    def rightdown(self, event):
        """
        Right-click down event
        Multiple-rectangle selection is now implemented
        Right-click is also used to pan across the image plane
        """
        event.Skip()
        pos = event.GetPosition()
        r = self.colliderectpos(pos)
        if r is not None:
            # add the rect that was clicked to the rect group
            self.selrect = None
            self.selectedrects.append(r)
        else:
            # go back to normal panning controls
            self.rightclick = True
            self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
            self.init_click = event.GetPosition()
        self.Refresh()

    def rightup(self, event):
        event.Skip()
        self.rightclick = False
        self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))  # set cursor back to sys default
        self.init_click = event.GetPosition()
        self.Refresh()

    def middown(self, event):
        """Mid-down event has no use right now"""
        event.Skip()
        self.middleclick = True

    def midup(self, event):
        """Delete a the current selected rectangle"""
        event.Skip()
        self.middleclick = False
        if self.selrect is not None:
            self.deleteselectedrect()

    def onpaint(self, event):
        """
        The main Drawing function
        All visuals are done here
        Rect states of drawing: unnamed, named, and currently being added via mouse
        Preferences.py stores the color preferences for the program
        """
        # TODO: future feature of zooming in on the image (use of a zoom variable? enhanced bitdrawing?)
        event.Skip()
        w, h = self.GetClientSize()  # these two aren't used much right now
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        # Cause the render to draw unfilled rectangles with borders (may be root of problems)
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
            for r in self.rects:
                if r.idtag.strip() != "":  # condition for a tag being completely empty
                    dc.SetPen(wx.Pen(Preferences.inactiveRectangleBorder, 1, style=wx.SOLID))
                    dc.DrawRectangle(r.x + self.offsetx, r.y + self.offsety, r.w, r.h)
                else:
                    dc.SetPen(wx.Pen(Preferences.errorRectangleBorder, 1, style=wx.SOLID))
                    dc.DrawRectangle(r.x + self.offsetx, r.y + self.offsety, r.w, r.h)
            if self.selrect is not None:
                dc.SetPen(wx.Pen(Preferences.highlightedRectangleBorder, 1, style=wx.SOLID))
                dc.DrawRectangle(self.selrect.x + self.offsetx, self.selrect.y + self.offsety,
                                 self.selrect.w, self.selrect.h)
            if len(self.selectedrects):
                dc.SetPen(wx.Pen(Preferences.highlightedRectangleBorder, 2, style=wx.DOT_DASH))
                for r in self.selectedrects:
                    dc.DrawRectangle(r.x + self.offsetx, r.y + self.offsety, r.w, r.h)
        else:
            dc.SetPen(wx.Pen(wx.BLACK, 5))
            n = len(Preferences.noImgText) * 5
            dc.DrawText(Preferences.noImgText, (w / 2)-n, (h / 2))
# end