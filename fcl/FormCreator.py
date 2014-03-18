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

#TODO: Fix the function binding with Event.Skip() for everything

class FormCreator(wx.Frame):
    def __init__(self, parent, title):
        self.w, self.h = 800, 600
        wx.Frame.__init__(self, parent, title=title)

        # Basic frame information
        self.SetTitle("Form Creator " + Preferences.version)
        self.SetClientSize((self.w, self.h))
        self.Center()
        self.Maximize()
        bp = wx.BoxSizer(orient=wx.VERTICAL)
        bp.SetMinSize([self.w, self.h])  # set the min size of the window

        # Add the canvas for rectangular mapping
        self.v = View(self)
        self.idtext = wx.TextCtrl(self)
        self.applybutton = wx.Button(self, -1, " Apply ")
        self.img = ""

        self.listitems = ("text", "radio", "checkbox")
        self.listbox = wx.ListBox(self)
        for i, I in enumerate(self.listitems):
            self.listbox.Insert(I, i)

        # Bottom panel for text entry here with a horizontal sizer
        panelsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Test button creation
        panelsizer.Add(self.applybutton, 0, wx.EXPAND)
        panelsizer.Add(self.idtext, 1, wx.EXPAND)
        panelsizer.Add(self.listbox, 2, wx.EXPAND)

        # Start doing sizers
        bp.Add(self.v, 1, wx.EXPAND)
        bp.Add(panelsizer, 0, wx.BOTTOM | wx.EXPAND)
        self.SetSizer(bp)
        self.SetAutoLayout(1)
        bp.Fit(self)

        # Status bar info and data
        self.CreateStatusBar()
        self.SetStatusText("Welcome to Form Creator!")

        # File menu operations and buttons
        fmenu = wx.Menu()
        openbutton = fmenu.Append(wx.ID_OPEN, "Open", "Open up an image")
        savebutton = fmenu.Append(wx.ID_SAVE, "Save", "Save your work")
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
        self.Bind(wx.EVT_MENU, self.on_open, openbutton)
        self.Bind(wx.EVT_MENU, self.on_save, savebutton)
        self.Bind(wx.EVT_MENU, self.on_close, closebutton)
        self.Bind(wx.EVT_MENU, self.on_about, aboutbutton)
        self.Bind(wx.EVT_MENU, self.on_exit, exitbutton)
        self.Bind(wx.EVT_MENU, self.on_delete, deletebutton)
        self.Bind(wx.EVT_MENU, self.del_all, delallbutton)
        self.Bind(wx.EVT_LISTBOX, self.on_selection, self.listbox)
        self.Bind(wx.EVT_BUTTON, self.apply_name, self.applybutton)

    def on_open(self, event):
        """
        Open up an image and load it to the canvas
        """
        print("Opening a file" + str(wx.ID_OPEN))
        dirname = ""
        dlg = wx.FileDialog(self, "Choose a file", dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            self.img = join(dirname, filename)
            self.v.image = wx.Bitmap(self.img, type=wx.BITMAP_TYPE_ANY)
            self.v.rects = []
            self.v.Refresh()  # trigger onpaint
            self.SetTitle("Form Creator : " + self.img)
        dlg.Destroy()

    def on_save(self, event):
        """
        Copy the image from SRC to the destination directory + folder
        Then write the rectangle data to HTML format
        and also a new readable JSON format (called .RMAP)
        """
        # TODO: Make the Save function export an RMAP JSON and copy the original image to destination
        if self.v.image is not None:
            dlg = wx.FileDialog(self, "Choose a name to save the file", "", "", "*.RMAP", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetFilename()
                dirname = dlg.GetDirectory()
                dlg.Destroy()
            else:
                dirname = ""
                filename = "imagedata"

            # build a rectangle dictionary to use in a JSON export
            rmap_data = {}
            for i, r in enumerate(self.v.rects):
                d = {"x": r.x, "y": r.y, "w": r.w, "h": r.h,
                     "IDtag": r.idtag, "typeRect": r.typerect}
                rmap_data["rect"+str(i)] = d
            with open(join(dirname, filename), "w") as F:
                F.write(dumps(rmap_data, sort_keys=True, indent=4, separators=(',', ': ')))
            self.SetStatusText("RMAP saved to: " + str(join(dirname)))
        else:
            self.SetStatusText("You can't write data without an image!")

    def on_close(self, event):
        self.img = ""
        self.v.image = None
        self.v.editmode = False
        self.v.rects = []

    def on_apply(self, event):
        """Send text to the canvas to mark rectangles with text"""
        pass

    def on_selection(self, event):
        """
        Apply the selection from listbox to the rectangle selected (if any)
        """
        N = self.listitems[self.listbox.GetSelection()]
        if self.v.image is not None:
            self.v.applytype(N)


    def on_about(self, event):
        dlg = wx.MessageDialog(self, "A short description etc", "About FormCreator", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        print("Cya")
        self.Close(True)  # close program

    def on_delete(self, event):
        if self.v.image is not None:
            self.v.deleteselectedrect()

    def del_all(self, event):
        if self.v.image is not None:
            self.v.deleteallrects()

    def set_type(self, text):
        self.listbox.SetStringSelection(text)

    def apply_name(self, event):
        #print("we're typing")
        if self.v.image is not None:
            self.v.applyname(self.idtext.Value)

    def toggle_edit(self, event):
        """Turn on editing mode for canvas"""
        if self.v.image is not None:
            # invert the state of edit mode
            self.v.editmode = not self.v.editmode
#end