#!/usr/bin/python
#-*- coding: utf-8 -*-
from fcl import View

__author__ = 'Steven'

from os.path import join
import wx
from View import View, Preferences
from json import loads, dumps

"""
Form Creator app design class
All functionality of the GUI here
"""


class FormCreator(wx.Frame):
    def __init__(self, parent, title):
        self.W, self.H = 800, 600
        wx.Frame.__init__(self, parent, title=title)

        # Basic frame information
        self.SetTitle("Form Creator " + Preferences.version)
        self.SetClientSize((self.W, self.H))
        self.Center()
        self.Maximize()
        bp = wx.BoxSizer(orient=wx.VERTICAL)
        bp.SetMinSize([self.W, self.H])  # set the min size of the window

        # Add the canvas for rectangular mapping
        self.v = View(self)
        self.idText = wx.TextCtrl(self)
        self.applyButton = wx.Button(self, -1, " Apply ")

        self.listitems = ("text", "radio", "checkbox")
        self.listbox = wx.ListBox(self)
        for i, I in enumerate(self.listitems):
            self.listbox.Insert(I, i)

        # Bottom panel for text entry here with a horizontal sizer
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Test button creation
        panelSizer.Add(self.applyButton, 0, wx.EXPAND)
        panelSizer.Add(self.idText, 1, wx.EXPAND)
        panelSizer.Add(self.listbox, 2, wx.EXPAND)

        # Start doing sizers
        bp.Add(self.v, 1, wx.EXPAND)
        bp.Add(panelSizer, 0, wx.BOTTOM | wx.EXPAND)
        self.SetSizer(bp)
        self.SetAutoLayout(1)
        bp.Fit(self)

        # Status bar info and data
        self.CreateStatusBar()
        self.SetStatusText("Welcome to Form Creator!")

        # File menu operations and buttons
        fmenu = wx.Menu()
        openbutton = fmenu.Append(wx.ID_OPEN, "Open", "Open up an image")
        savebutton = fmenu.Append(wx.ID_OPEN, "Save", "Save your work")
        closebutton = fmenu.Append(wx.ID_CLOSE, "Close", "Close an image mapping")
        fmenu.AppendSeparator()
        aboutbutton = fmenu.Append(wx.ID_ABOUT, "&About", "Info on this program")
        fmenu.AppendSeparator()
        exitbutton = fmenu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")
        emenu = wx.Menu()
        deletebutton = emenu.Append(wx.ID_DELETE, "&Delete", "Delete the current selection")
        delallbutton = emenu.Append(wx.ID_EXECUTE, "Delete All", "Delete all rectangles (panic mode!)")

        mb = wx.MenuBar()
        mb.Append(fmenu, "&File")
        mb.Append(emenu, "&Edit")

        # etc
        self.SetMenuBar(mb)
        self.Show(True)

        # Bindings
        self.Bind(wx.EVT_MENU, self.onOpen, openbutton)
        self.Bind(wx.EVT_MENU, self.onSave, savebutton)
        self.Bind(wx.EVT_MENU, self.onClose, closebutton)
        self.Bind(wx.EVT_MENU, self.onAbout, aboutbutton)
        self.Bind(wx.EVT_MENU, self.onExit, exitbutton)
        self.Bind(wx.EVT_MENU, self.onDelete, deletebutton)
        self.Bind(wx.EVT_MENU, self.delAll, delallbutton)
        self.Bind(wx.EVT_LISTBOX, self.onSelection, self.listbox)
        self.Bind(wx.EVT_BUTTON, self.applyName, self.applyButton)

    def onOpen(self, event):
        """
        Open up an image and load it to the canvas
        """
        event.Skip()
        self.dirname = ""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.img = join(self.dirname, self.filename)
            self.v.image = wx.Bitmap(self.img, type=wx.BITMAP_TYPE_ANY)
            self.v.rects = []
            self.v.Refresh()  # trigger onPaint
            self.v.calcBoundaries()
            self.SetTitle("Form Creator : " + self.img)
        dlg.Destroy()

    def onClose(self, event):
        event.Skip()
        self.v.image = None
        self.v.editMode = False
        self.v.rects = []

    def onApply(self, event):
        """Send text to the canvas to mark rectangles with text"""
        event.Skip()
        pass

    def onSelection(self, event):
        """
        Apply the selection from listbox to the rectangle selected (if any)
        """
        event.Skip()
        N = self.listitems[self.listbox.GetSelection()]
        if self.v.image is not None:
            self.v.applyType(N)

    def onSave(self, event):
        """
        Copy the image from SRC to the destination directory + folder
        Then write the rectangle data to HTML format
        and also a new readable JSON format (called .RMAP)
        """
        # TODO: Make the Save function export an RMAP JSON and copy the original image to destination
        if self.v.image is not None:
            event.Skip()
            dlg = wx.FileDialog(self, "Choose a name to save the file", "", "", "*.RMAP", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetFilename()
                dirname = dlg.GetDirectory()
                dlg.Destroy()
            else:
                dirname = ""
                filename = "imagedata"

            # build a rectangle dictionary to use in a JSON export
            RMAPdata = {}
            for i, R in enumerate(self.v.rects):
                d = {"x": R.x, "y": R.y, "w": R.w, "h": R.h,
                     "IDtag": R.IDtag, "typeRect": R.typeRect}
                RMAPdata["rect"+str(i)] = d
            with open(join(dirname, filename), "w") as F:
                F.write(dumps(RMAPdata, sort_keys=True, indent=4, separators=(',', ': ')))
            self.SetStatusText("RMAP saved to: " + str(join(dirname)))
        else:
            self.SetStatusText("You can't write data without an image!")
        event.Skip()

    def onAbout(self, event):
        event.Skip()
        dlg = wx.MessageDialog(self, "A short description etc", "About FormCreator", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def onExit(self, event):
        event.Skip()
        self.Close(True)  # close program

    def onDelete(self, event):
        event.Skip()
        if self.v.image is not None:
            self.v.deleteSelectedRect()

    def delAll(self, event):
        event.Skip()
        if self.v.image is not None:
            self.v.deleteAllRects()

    def setTypeText(self, text):
        self.listbox.SetStringSelection(text)

    def applyName(self, event):
        #print("we're typing")
        if self.v.image is not None:
            self.v.applyName(self.idText.Value)
        event.Skip()

    def toggleEditMode(self, event):
        """Turn on editing mode for canvas"""
        if self.v.image is not None:
            # invert the state of edit mode
            self.v.editMode = not self.v.editMode
#end