# -*- coding: utf-8 -*-

from .sourceline import SourceLine
from .outputline import OutputLine

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

        self.total_tax_amount = 0.0

        self.sourceLines = []
        self.outputLines = []

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
        self.sourceLines = []
        cursor.execute("""
            select
                aml.name            as name,
                aml.balance         as amounteur,
                aa.code             as accountgl,
                aml.partner_id      as partner_id,
                aml.product_id      as product_id,
                aml.tax_base_amount as tax_base_amount,
                at.amount           as account_tax_amount,
                p.name              as partner_name,
                p.ref               as partner_ref,
                aml.tax_line_id     as tax_line_id
            from account_move_line aml
            left join account_account aa on aa.id = aml.account_id
            left join account_tax at on at.id = aml.tax_line_id
            left join res_partner p on p.id = aml.partner_id
            where aml.move_id = %(move_id)s
            order by aa.code, aml.id
            """,
            {
                'move_id': self.id
            })
        for row in cursor.dictfetchall():
            line = SourceLine()
            line.fromDictRow(row)
            self.sourceLines.append(line)

        # Replace the account number in some cases
        for sourceLine in self.sourceLines:
            if sourceLine.accountgl == '701000':
                sourceLine.accountgl = '700000'

    def readTaxAmount(self, cursor):
        self.total_tax_amount = 0.0
        cursor.execute("""
            select tax_base_amount
            from account_move_line
            where account_move_line.move_id = %(move_id)s
            and tax_base_amount > 0.0
            and name = '21%%'
            """,
            {
                'move_id': self.id
            })
        row = cursor.fetchone()
        if row:
            self.total_tax_amount = row[0]

    def process(self):
        self.outputLines = []

        outputLine = None

        for sourceLine in self.sourceLines:
            if outputLine is None:
                outputLine = OutputLine()
                outputLine.setValues(self, sourceLine)
                self.outputLines.append(outputLine)
            else:
                if sourceLine.accountgl != outputLine.accountgl:
                    outputLine = OutputLine()
                    outputLine.setValues(self, sourceLine)
                    self.outputLines.append(outputLine)
                else:
                    outputLine.amounteur += sourceLine.amounteur
        
        # check if missing vatbase on lines where accountgl
        # is 400000 or 451000
        for line in self.outputLines:
            if(line.accountgl in ('400000', '451000') and line.vatbase == 0.0):
                line.vatbase = self.calcTotalSalesAmount()

    def calcTotalSalesAmount(self):
        """
        Return the total sales of all lines where accountgl
        starts with 7
        """
        total = 0.0
        for line in self.outputLines:
            if line.accountgl[:1] == '7':
                total += line.amounteur
        return total * -1

    def getCsvOutput(self):
        output = ""
        for line in self.outputLines:
            output += line.getCsvOutput()
            if line.accountgl == '400000':
                if line.vatbase == 0.0:
                    output += "NO VATBASE !!!\n"
        # output += "\n"
        return output
    