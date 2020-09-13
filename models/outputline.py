# -*- coding: utf-8 -*-

class OutputLine:

    def __init__(self):
        self.doctype    = 0
        self.dbkcode    = ""
        self.dbktype    = ""
        self.docnumber  = ""
        self.docorder   = ""
        self.opcode     = ""
        self.accountgl  = ""
        self.accountrp  = ""
        self.bookyear   = ""
        self.period     = ""
        self.date       = ""
        self.datedoc    = ""
        self.duedate    = ""
        self.comment    = ""
        self.commentext = ""
        self.amount     = ""
        self.amounteur  = 0
        self.vatbase    = 0
        self.vatcode    = ""
        self.curramount = ""
        self.currcode   = ""
        self.cureurbase = ""
        self.vattax     = ""
        self.vatimput   = ""
        self.currate    = ""
        self.remindlev  = ""
        self.matchno    = ""
    
    def getCsvOutput(self):
        output = ""

        s_amounteur = "%.2f" % self.amounteur
        s_amounteur = s_amounteur.rstrip('0').rstrip('.')

        s_vatbase = ("%.2f" % self.vatbase) or "0.00"
        if s_vatbase == "0.00":
            s_vatbase = ""

        output += "%d,"  % self.doctype
        output += "%s,"  % self.dbkcode
        output += "%s,"  % self.dbktype
        output += "%s,"  % self.docnumber
        output += "%s,"  % self.docorder
        output += "%s,"  % self.opcode
        output += "%s,"  % self.accountgl
        output += "%s,"  % self.accountrp
        output += "%s,"  % self.bookyear
        output += "%s,"  % self.period
        output += "%s,"  % self.date
        output += "%s,"  % self.datedoc
        output += "%s,"  % self.duedate
        output += "%s,"  % self.comment
        output += "%s,"  % self.commentext
        output += "%s,"  % self.amount
        output += "%s,"  % s_amounteur
        output += "%s,"  % s_vatbase
        output += "%s,"  % self.vatcode
        output += "%s,"  % self.curramount
        output += "%s,"  % self.currcode
        output += "%s,"  % self.cureurbase
        output += "%s,"  % self.vattax
        output += "%s,"  % self.vatimput
        output += "%s,"  % self.currate
        output += "%s,"  % self.remindlev
        output += "%s\n" % self.matchno

        return output
