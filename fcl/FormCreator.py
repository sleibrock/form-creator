#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__ = 'Steven'

from os.path import join, isfile
from os import mkdir, rename
from shutil import copy
from json import loads, dumps
import wx
from View import View
from Preferences import Preferences
# TODO: make a popup window showing text data of all rects?
# TODO: fix the issue of the invisible rectangles


class FormCreator(wx.Frame):
    """
    FormCreator GUI class frame
    All design layout code goes into this class
    """
    def __init__(self, parent, title):
        """Initializer"""
        wx.Frame.__init__(self, parent, title=title)
        self.w, self.h = 800, 600

        # Basic frame information
        self.SetTitle("Form Creator " + Preferences.version)
        self.SetClientSize((self.w, self.h))
        self.Center()
        self.Maximize()
        bp = wx.BoxSizer(orient=wx.VERTICAL)
        bp.SetMinSize([self.w, self.h])  # set the min size of the window

        # Add the canvas for rectangular mappi8ng
        self.view = View(self)
        self.idtext = wx.TextCtrl(self, 33)
        self.applybutton = wx.Button(self, -1, " Apply ")
        self.filename = ""
        self.img = ""
        self.rmap_loaded = False
        self.idtext.SetFocus()

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
        bp.Add(self.view, 1, wx.EXPAND)
        bp.Add(panelsizer, 0, wx.BOTTOM | wx.EXPAND)
        self.SetSizer(bp)
        self.SetAutoLayout(1)
        bp.Fit(self)

        # Status bar info and data
        self.CreateStatusBar()
        self.SetStatusText(Preferences.welcomeMessage)

        # File menu operations and buttons
        fmenu = wx.Menu()
        openbutton = fmenu.Append(wx.ID_OPEN, "Open", "Open up an image")
        savebutton = fmenu.Append(wx.ID_SAVE, "Save", "Save your work")
        closebutton = fmenu.Append(wx.ID_CLOSE, "Close", "Close an image mapping")
        exportbutton = fmenu.Append(wx.ID_ADD, "Export", "Export to a print page")
        printbutton = fmenu.Append(wx.ID_BOLD, "Print", "Print all rectangles to text")
        fmenu.AppendSeparator()
        aboutbutton = fmenu.Append(wx.ID_ABOUT, "About", "Info on this program")
        statsbutton = fmenu.Append(wx.ID_STATIC, "Stats", "Statistical data on the view")
        fmenu.AppendSeparator()
        exitbutton = fmenu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")
        emenu = wx.Menu()
        filtbutton = emenu.Append(wx.ID_CUT, "Filter", "Filter any 'bad' rectangles we can't use")
        fmenu.AppendSeparator()
        cleanbutton = emenu.Append(wx.ID_ABORT, "Clean", "Remove any rectangles that don't have ID tags")
        deletebutton = emenu.Append(wx.ID_DELETE, "Delete", "Delete the current selection")
        delallbutton = emenu.Append(wx.ID_EXECUTE, "Delete All", "Delete all rectangles (panic mode!)")

        mb = wx.MenuBar()
        mb.Append(fmenu, "&File")
        mb.Append(emenu, "&Edit")

        # etc
        self.SetMenuBar(mb)
        self.Show(True)

        self.view.SetFocus()

        # Bindings
        self.Bind(wx.EVT_MENU, self.on_open, openbutton)
        self.Bind(wx.EVT_MENU, self.on_save, savebutton)
        self.Bind(wx.EVT_MENU, self.on_close, closebutton)
        self.Bind(wx.EVT_MENU, self.on_print, printbutton)
        self.Bind(wx.EVT_MENU, self.export_print_page, exportbutton)
        self.Bind(wx.EVT_MENU, self.on_about, aboutbutton)
        self.Bind(wx.EVT_MENU, self.on_stats, statsbutton)
        self.Bind(wx.EVT_MENU, self.on_exit, exitbutton)
        self.Bind(wx.EVT_MENU, self.filter, filtbutton)
        self.Bind(wx.EVT_MENU, self.cleanup, cleanbutton)
        self.Bind(wx.EVT_MENU, self.on_delete, deletebutton)
        self.Bind(wx.EVT_MENU, self.del_all, delallbutton)
        self.Bind(wx.EVT_LISTBOX, self.on_selection, self.listbox)
        self.Bind(wx.EVT_BUTTON, self.apply_name, self.applybutton)
        self.Bind(wx.EVT_TEXT, self.typing, self.idtext)

    def typing(self, event):
        """
        Set the text being typed to the rectangle's name
        """
        event.Skip()
        if self.view.image is not None:
            self.view.applyname(self.idtext.Value)

    def on_print(self, event):
        """Print button for debugging"""
        event.Skip()
        if self.view is not None:
            for r in self.view.rects:
                print("{0} : {1} - {2}".format(r.idtag, r.typerect, r.data))

    def on_open(self, event):
        """
        Open up an image and load it to the canvas
        """
        event.Skip()
        dirname = ""
        dlg = wx.FileDialog(self, "Choose a file", dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            self.img = join(dirname, self.filename)
            self.view.image = wx.Bitmap(self.img, type=wx.BITMAP_TYPE_ANY)
            self.view.rects = []
            self.view.Refresh()  # trigger onpaint
            self.SetTitle("Form Creator : " + self.img)

            # Read for an RMAP file
            fname = self.filename.split(".")
            fname.pop()
            rmap_file = join(dirname, ".".join(fname + ["rmap"]))

            if isfile(rmap_file):
                # the file is here!
                with open(rmap_file, "r") as f:
                    rmap_rects = loads(f.read())
                    self.view.read_json(rmap_rects)
                    self.rmap_loaded = True
                self.SetStatusText(Preferences.RmapFound)
            else:
                self.SetStatusText(Preferences.noRmapFound)
                self.rmap_loaded = False
        dlg.Destroy()

    def export_print_page(self, event):
        """Export a print page using a JSON file"""
        event.Skip()
        if self.view.image is not None:
            # We don't require an RMAP file, just rect data that we can generate
            dlg = wx.FileDialog(self, "Choose a JSON file to load", "", "", "", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetFilename()
                dirname = dlg.GetDirectory()
                dlg.Destroy()
            else:
                self.SetStatusText(Preferences.failedToOpen)
                return False
            rmap_data = self.view.rects
            try:
                with open(join(dirname, filename), "r") as f:
                    json_data = loads(f.read())
            except Exception as e:
                self.SetStatusText(Preferences.failedToExport)
                return False
            fd = self.img.split(".")
            fd.pop()
            fname = ".".join(fd)
            rmap_data = View.filter_list(rmap_data)
            rmap_data = View.clean_list(rmap_data)
            rmap_data = View.generate_data(rmap_data)
            self.write_html_printpage(self.filename, fname, rmap_data, json_data)
        else:
            self.SetStatusText(Preferences.noImageLoaded)

    def on_save(self, event):
        """
        Copy the image from SRC to the destination directory + folder
        Then write the rectangle data to HTML format
        and also a new readable JSON format (called .RMAP)
        """
        event.Skip()
        if self.view.image is not None:
            self.view.update_values()
            rmap_data = self.view.generate_rmap()

            if self.rmap_loaded:  # this means we previously had an RMAP file loaded, so save to that
                # Use self.img as the main determiner
                # remove extension of file
                fpath = self.img.split(".")
                ext = fpath.pop()
                fpath = ".".join(fpath)

                # rewrite the RMAP and HTML
                self.write_html_rmap(fpath, rmap_data,  fpath.split('\\').pop() + "." + ext)
                self.SetStatusText(Preferences.RmapSaved.format(fpath))
            else:
                dlg = wx.FileDialog(self, "Choose a name to save the file", "", "", "rmap", wx.SAVE)
                if dlg.ShowModal() == wx.ID_OK:
                    filename = dlg.GetFilename().replace(".rmap", "")
                    dirname = dlg.GetDirectory()
                    dlg.Destroy()
                else:
                    self.SetStatusText(Preferences.failedToSave)
                    return False
                # make a directory with the filename
                newdir = join(dirname, filename)
                mkdir(newdir)

                # Copy the original image
                copy(self.img, join(newdir, self.filename))
                fname = self.filename.split(".")
                new_fname = ".".join([filename, fname.pop()])
                rename(join(newdir, self.filename), join(newdir, new_fname))

                # export HTML/CSS data to a new HTML file
                self.write_html_rmap(join(newdir, filename), rmap_data, new_fname)
                self.SetStatusText(Preferences.RmapSaved.format(str(join(newdir, new_fname))))
        else:
            self.SetStatusText(Preferences.noImageLoaded)

    @staticmethod
    def write_html_rmap(filepath, rmap_data, new_fname=""):
        """HTML and RMAP export code"""
        with open(filepath+".rmap", "w") as F:  # dump the JSON RMAP
            F.write(FormCreator.export_json(rmap_data))
        with open(join(Preferences.staticFolder, Preferences.SkeletonFile), "r") as f:  # read skeleton file
            skeletal_data = f.read()
        with open(filepath+".html", "w") as f:  # write the HTML/css file
            page_title = new_fname
            css = 3*"\t" + ".sourceImage{ z-index: -1; }\n"
            html = 3*"\t" + "<img src=\"{0}\" class=\"sourceImage\" />\n".format(new_fname)
            text_size_divider = 9  # size to divide rect width by for HTML text
            for key, r in rmap_data.items():
                # append CSS - horiz: off by 10px, vert: off by 10px
                css += 3*"\t" + "."+key+"{position:absolute;top:"+str(r["y"]+10)+"px;left:"+str(r["x"]+10)+"px;}\n"
                # append HTML
                if r["typerect"] == "text" and r["idtag"].strip() != "":
                    i = 3*"\t" + "<input type=\"text\" class=\"{0}\" size=\"{1}\" name=\"{2}\" id=\"{2}\" />\n"
                    html += i.format(key, r["w"]/text_size_divider, r["idtag"])
                elif r["idtag"].strip() != "":  # don't add rects without tags
                    i = 3*"\t" + "<input type=\"{0}\" class=\"{1}\" name=\"{2}\" id=\"{2}\" value=\"{3}\" />\n"
                    html += i.format(r["typerect"], key, r["idtag"], r["value"])
            f.write(skeletal_data.format(page_title, css, html))

    @staticmethod
    def write_html_printpage(iname, filepath, rmap_data, json_data):
        """For future use in writing data to an HTML page (similar code as write_html_rmap)"""
        # TODO: data test writing to an HTML print page
        with open(join(Preferences.staticFolder, Preferences.SkeletonFile), "r") as f:
            skeletal_data = f.read()
        with open(filepath+".print.html", "w") as f:
            css = ".sourceImage{z-index:-1;}\n"
            html = "<img src=\"{0}\" class=\"sourceImage\" />\n".format(iname)
            for key, r in rmap_data.items():
                css += "."+key+"{position:absolute;top:"+str(r["y"]+10)+"px;left:"+str(r["x"]+10)+"px;}\n"
                if r["typerect"] == "text" and r["idtag"].strip() != "":
                    print(r)
                    html += "<p class=\"{0}\">{1}</p>".format(key, json_data[r["idtag"]]["value"])
                else:
                    # <input type"radio" checked> creates a checked radio
                    # we need json info if the field was selected
                    pass
            f.write(skeletal_data.format("", css, html))

    @staticmethod
    def export_json(data):
        """Export JSON etc"""
        return dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def on_close(self, event):
        """Close the image and remove excess data from the viewer"""
        event.Skip()
        self.img = ""
        self.view.clear_all()
        self.rmap_loaded = False

    def on_selection(self, event):
        """Apply the selection from listbox to the rectangle selected (if any)"""
        event.Skip()
        n = self.listitems[self.listbox.GetSelection()]
        if self.view.image is not None:
            self.view.applytype(n)

    def filter(self, event):
        """Filter any bad rectangles from the buffer"""
        event.Skip()
        if self.view.image is not None:
            self.view.filter_rects()
            self.SetStatusText(Preferences.filterRects)

    def cleanup(self, event):
        """Cleaning function"""
        event.Skip()
        if self.view.image is not None:
            self.view.cleanup()
            self.SetStatusText(Preferences.cleanRects)

    def on_about(self, event):
        """Instruction dialog for the program"""
        event.Skip()
        dlg = wx.MessageDialog(self, "\n".join(Preferences.aboutAppInstructions), "About FormCreator", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def on_stats(self, event):
        """Statistical count data for the current view"""
        event.Skip()
        if self.view.image is not None:
            s, t, c, r, n = self.view.statistics()
            dlg = wx.MessageDialog(self, Preferences.statisticalData.format(s, t, c, r, n), "Statistics", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.SetStatusText(Preferences.noImageLoaded)

    def on_exit(self, event):
        """Exit the program"""
        event.Skip()
        self.view.clear_all()
        self.Close(True)  # close program

    def on_delete(self, event):
        """Delete selected rect"""
        event.Skip()
        if self.view.image is not None:
            self.view.deleteselectedrect()
            self.SetStatusText(Preferences.deletingRect)

    def del_all(self, event):
        """Delete all rects"""
        event.Skip()
        if self.view.image is not None:
            self.view.deleteallrects()
            self.SetStatusText(Preferences.deletingAllRects)

    def set_type(self, text):
        """Change the selection in the listbox"""
        self.listbox.SetStringSelection(text)

    def apply_name(self, event):
        """Apply the text to the rectangle"""
        event.Skip()
        if self.view.image is not None:
            self.view.applyname(self.idtext.Value)
#end