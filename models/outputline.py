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
    
    def setValues(self, move, line):
        if line.accountgl[:2] == '40':
            self.doctype = 1
        elif line.accountgl[:2] == '44':
            self.doctype = 2
        else:
            self.doctype = 3

        self.dbkcode    = move.dbkcode
        self.dbktype    = ""
        self.docnumber  = move.docnumber
        self.docorder   = ""
        self.opcode     = ""
        self.accountgl  = line.accountgl
        self.accountrp  = line.partner_ref
        self.bookyear   = ""
        self.period     = ""
        self.date       = ""
        self.datedoc    = move.datedoc
        self.duedate    = ""
        self.comment    = move.partner_name
        self.commentext = ""
        self.amount     = ""
        self.amounteur  = line.amounteur

        self.vatbase = 0
        if move.dbkcode == 'NCVEN':
            if(line.accountgl[:2] == '40'
            or line.accountgl[:2] == '44'
            or line.accountgl[:3] == '451'):
                self.vatbase = move.total_tax_amount
            if(line.accountgl[:3] == '451'
            or line.accountgl[:3] == '411'):
                self.vatbase = move.total_tax_amount * -1
        else:
            if(line.accountgl[:2] == '40'
            or line.accountgl[:2] == '44'
            or line.accountgl[:3] == '451'):
                self.vatbase = move.total_tax_amount
            if(line.accountgl[:3] == '701'
            or line.accountgl[:3] == '702'):
                self.vatbase = 0

        if(line.accountgl[:3] == '451'):
            self.vatcode = '211400'
        else:
            self.vatcode = ''

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

        # if self.vatbase is None:
        #     s_vatbase = ""
        # else:
        #     if self.vatbase == 0.0:
        #         s_vatbase = ""
        #     else:
        #         s_vatbase = "%.2f" % self.vatbase

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
