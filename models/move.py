# -*- coding: utf-8 -*-

class Move:

    def __init__(self):
        self.id           = 0
        self.dbkcode      = None
        self.name         = None
        self.date         = None
        self.docnumber    = None
        self.ref          = None
        self.datedoc      = None
        self.partner_name = None

    def fromDictRow(self, row):
        self.id           = row['id']
        self.dbkcode      = row['dbkcode']
        self.name         = row['name']
        self.date         = row['date']
        self.docnumber    = row['docnumber']
        self.ref          = row['ref']
        self.datedoc      = row['datedoc']
        self.partner_name = row['partner_name']

    def readLines(self, cursor):
        pass