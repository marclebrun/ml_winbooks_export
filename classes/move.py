# -*- coding: utf-8 -*-

from .sourceline import SourceLine
from .outputline import OutputLine

DEBUG = False

class Move:

    def __init__(self):
        self.id           = 0
        self.dbkcode      = None
        self.name         = None
        self.date         = None
        self.docnumber    = None
        self.ref          = None
        self.datedoc      = None

        self.partner_ref  = None
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

    def readLines(self, cursor):
        self.sourceLines = []
        cursor.execute("""
            select
                aml.id              as id,
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

            # initialize partner info if not done yet
            if(self.partner_ref is None or self.partner_name is None):
                self.partner_ref  = row['partner_ref']
                self.partner_name = row['partner_name']

        # Replace the account number in some cases
        for sourceLine in self.sourceLines:
            if sourceLine.accountgl == '701000':
                sourceLine.accountgl = '700000'
            # Discount amounts are part of the sales amount,
            # therefore we include those lines on the 700000
            # account.
            if sourceLine.accountgl == '653000':
                sourceLine.accountgl = '700000'
        
        # Read the taxex ids applied to each line
        for sourceLine in self.sourceLines:
            sourceLine.tax_ids = []
            cursor.execute("""
                select account_tax_id
                from account_move_line_account_tax_rel
                where account_move_line_id = %(aml_id)s
                """,
                {
                    'aml_id': sourceLine.id
                })
            for row in cursor.dictfetchall():
                sourceLine.tax_ids.append(row['account_tax_id'])

    def readTaxAmount(self, cursor):
        """
        Returns the total sales amount of lines on which
        the 21% VAT is applied.
        """
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

        # if debug, display each source line with its information
        if DEBUG:
            print("%s :" % self.name)
            for sourceLine in self.sourceLines:
                print("  %s %10.2f %s" % (
                    sourceLine.accountgl,
                    sourceLine.amounteur,
                    ",".join([str(x) for x in sourceLine.tax_ids])
                ))

        # add one output line for each distinct accountgl found
        # in the source lines.
        outputLine = None
        for sourceLine in self.sourceLines:
            if outputLine is None:
                outputLine = self.makeNewLine(sourceLine)
                self.outputLines.append(outputLine)
            else:
                if sourceLine.accountgl != outputLine.accountgl:
                    outputLine = self.makeNewLine(sourceLine)
                    self.outputLines.append(outputLine)
                else:
                    outputLine.amounteur += sourceLine.amounteur
        
        # always calculate the vatbase for lines 400000 and 451000 equal
        # to the total sales amount of the move.
        for line in self.outputLines:
            if(line.accountgl in ('400000', '451000')):
                line.vatbase = self.calcTotalSalesAmount()
        
        # Add missing tax line.
        # For each line with 0% tax, add its sales amount to the
        # account 451000.
        vatbase = 0
        vatcode = ""
        for line in self.sourceLines:
            for tax_id in line.tax_ids:
                if tax_id == 11:
                    vatbase += line.amounteur
                    vatcode = "221000"
                if tax_id == 13:
                    vatbase += line.amounteur
                    vatcode = "214000"
                if tax_id == 157:
                    vatbase += line.amounteur
                    vatcode = "211100"
        if vatcode != "":
            outputLine = self.makeTaxLine(vatbase, vatcode)
            self.outputLines.append(outputLine)

    def makeNewLine(self, sourceLine):
        outputLine = OutputLine()
        
        if sourceLine.accountgl[:2] == '40':
            outputLine.doctype = 1
        elif sourceLine.accountgl[:2] == '44':
            outputLine.doctype = 2
        else:
            outputLine.doctype = 3
        
        outputLine.dbkcode   = self.dbkcode
        outputLine.docnumber = self.docnumber
        outputLine.accountgl = sourceLine.accountgl
        outputLine.accountrp = self.partner_ref
        outputLine.datedoc   = self.datedoc
        outputLine.comment   = self.partner_name
        outputLine.amounteur = sourceLine.amounteur
        outputLine.vatbase   = 0

        if(sourceLine.accountgl[:3] == '451'):
            outputLine.vatcode = '211400'
        else:
            outputLine.vatcode = ''
        
        # if invoiced from Point Of Sale, always force the client
        if (self.ref and self.ref[:4] == 'POS/'):
            outputLine.accountrp = '400751'
            outputLine.comment   = 'VENTE CLIENTS DIVERS'

        return outputLine

    def makeTaxLine(self, vatbase, vatcode):
        outputLine = OutputLine()
        outputLine.doctype   = 4
        outputLine.dbkcode   = self.dbkcode
        outputLine.docnumber = self.docnumber
        outputLine.accountgl = ""
        outputLine.accountrp = self.partner_ref
        outputLine.datedoc   = self.datedoc
        outputLine.comment   = self.partner_name
        outputLine.amounteur = 0
        outputLine.vatbase   = vatbase
        outputLine.vatcode   = vatcode
        return outputLine

    def calcTotalSalesAmount(self):
        """
        Returns the total sales of all output lines where
        accountgl starts with 7.
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
        return output

    def getDebugOutput(self):
        output = "%s/%s\r\n" % (self.dbkcode, self.docnumber)

        amount_balance = 0.0
        vatbase_balance = 0.0
        for line in self.outputLines:

            amount_balance += line.amounteur

            if line.doctype == 1:
                vatbase_balance += line.vatbase
            if line.doctype == 3:
                if line.accountgl != '451000':
                    vatbase_balance += line.vatbase
                if line.accountgl[:1] == '7':
                    vatbase_balance += line.amounteur
            if line.doctype == 4:
                vatbase_balance -= line.vatbase

            output += "    %1s %-10s : %10.2f / %10.2f  ==>>  %10.2f / %10.2f\r\n" % (
                line.doctype,
                line.accountgl,
                line.amounteur,
                line.vatbase,
                amount_balance,
                vatbase_balance
            )

        output += "    %12s :                          ==>>  %10.2f / %10.2f => %s\r\n" % (
            "BALANCES",
            amount_balance,
            vatbase_balance,
            "Ok" if(abs(amount_balance) < 0.001 and abs(vatbase_balance) < 0.001) else "ERROR"
        )

        output += "\r\n"
        return output