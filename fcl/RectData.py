#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__ = 'Steven'

import unittest
import random
from itertools import combinations


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

    def collide(self, rect):
        """Collision code"""
        pass

class TestRect(unittest.TestCase):
    """Unit case for Rect class"""

    def setUp(self):
        self.seq = range(1000)
        self.check = 0
        self.recs = []

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

    def add_recs(self):
        """
        Adds a number of rectangles to 'recs' for testing.
        :param rect:
        """
        for i in range(0,100,1):
            self.recs.append(self.create_rect())

    def test_collision(self):
        """
        Checks the rectangles for collisions
        """
        self.add_recs()
        combos = combinations(self.recs, 2)
        for pair in combos:
            self.assertTrue(pair[0].collide(pair[1]))