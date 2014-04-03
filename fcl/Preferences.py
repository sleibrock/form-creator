#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__ = 'Steven'

import wx


class Preferences(object):
    """
    Class to store application preferences
    Stores strings to use in basic messages/alerts as well
    Colors can use either wx.COLOR constants or "######" Hex value codes
    """
    version = "1.0"
    title = "FormCreator " + version
    staticFolder = "static"
    SkeletonFile = "skeleton.html"
    highlightedRectangleBorder = wx.GREEN
    displayRectangleBorder = wx.RED
    inactiveRectangleBorder = wx.BLUE
    errorRectangleBorder = wx.RED
    noImgText = "Load an image to process"
    welcomeMessage = "Welcome to Form Creator!"
    noRmapFound = "No RMAP data found, starting from scratch"
    RmapFound = "RMAP found, loading rectangles into buffer"
    failedToSave = "Failed to save!"
    failedToOpen = "Failed to open target file"
    failedToExport = "Failed to export the file"
    RmapSaved = "RMAP data saved to: {0}"
    noImageLoaded = "You can't save data without an image!"
    cantFindRectangle = "Can't find rectangle to delete"
    deletingRect = "Deleting selected rectangle"
    deletingAllRects = "Deleting all rects! (Careful!)"
    filterRects = "Filtering bad rectangles"
    cleanRects = "Cleaning up rects with no names"
    statisticalData = "{0} Total Rectangles\n{1} Text Rects\n{2} Check Rects\n{3} Radio Rects\n{4} Names tagged"
    aboutAppInstructions = ["Open up an image, left click to drag rectangles",
                            "Right click to pan around the image",
                            "Middle click to delete a selected rectangle",
                            "Use menu options for further operations (filter, delete all, etc)",
                            "Saving creates a new folder with JSON data and an HTML file"]
#end