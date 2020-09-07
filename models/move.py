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
                outputLine.amounteur += sourceLine.amounteur

        return

        # if invoiced from Point Of Sale : force the client
        if (self.ref and self.ref[:4] == 'POS/'):
            sourceLine.accountrp = '400751'
            sourceLine.comment   = 'VENTE CLIENTS DIVERS'

        for sourceLine in self.sourceLines:
            outputLine = OutputLine()
            outputLine.setValues(self, sourceLine)
            if sourceLine.accountgl != current_accountgl:
                if current_accountgl != '':
                    outputLine.accountgl = current_accountgl
                    outputLine.amounteur = current_amounteur
                    self.outputLines.append(outputLine)
                current_accountgl = sourceLine.accountgl
                current_amounteur = 0.0

    def getCsvOutput(self):
        output = ""
        for line in self.outputLines:
            output += line.getCsvOutput()
        return output
    