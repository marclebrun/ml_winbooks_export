# -*- coding: utf-8 -*-

from .line import Line

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
            line = Line()
            line.fromDictRow(row)
            self.sourceLines.append(line)

    def process(self):
        self.outputLines = []

    def getCsvOutput(self):
        output = ""
        for line in self.outputLines:
            output += line.getCsvOutput()
        return output
    