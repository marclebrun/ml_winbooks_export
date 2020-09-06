# -*- coding: utf-8 -*-

import datetime

class Export:

    def __init__(self):
        self.dateFrom = datetime.date.today()
        self.dateTo   = datetime.date.today()

    def setDates(self, dateFrom, dateTo):
        self.dateFrom = dateFrom
        self.dateTo   = dateTo
    
    def debug(self):
        print("Export from %s to %s" % (self.dateFrom, self.dateTo))
