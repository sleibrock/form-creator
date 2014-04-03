#!/usr/bin/python
#-*- coding: utf-8 -*-

import wx
from fcl.FormCreator import FormCreator
from fcl.View import Preferences

__author__ = 'Steven'

if __name__ == "__main__":
    app = wx.App(False)
    FormCreator(None, Preferences.title)
    app.MainLoop()
# end