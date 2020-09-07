# -*- coding: utf-8 -*-

import datetime
from .move import Move

class Export:

    def __init__(self):
        self.dateFrom  = datetime.date.today()
        self.dateTo    = datetime.date.today()
        self.moves     = []
        self.csvOutput = ""

    def setDates(self, dateFrom, dateTo):
        self.dateFrom = dateFrom
        self.dateTo   = dateTo

    def getCsvOutput(self):
        return self.csvOutput
    
    def debug(self):
        print("Export from %s to %s" % (self.dateFrom, self.dateTo))

    def readData(self, cursor):
        self.csvOutput += "Ligne 1.\n"
        self.csvOutput += "Ligne 2.\n"
        self.csvOutput += "Ligne 3.\n"

        self.readMoves(cursor)
    
    def readMoves(self, cursor):
        self.moves = []
        cursor.execute("""
            select
                am.id,
                case
                    when am.name like 'FAC%%' then 'VENTES'
                    when am.name like 'NC%%'  then 'NCVEN'
                end as dbkcode,
                am.name,
                am.date,
                case
                    when am.name like 'FAC%%' then replace(substr(am.name, 5, 11), '/', '')
                    when am.name like 'NC%%'  then replace(substr(am.name, 4, 11), '/', '')
                end as docnumber,
                am.ref,
                to_char(am.date, 'YYYYMMDD') as datedoc,
                p.name as partner_name
            from account_move am
            left join res_partner p on p.id = am.partner_id
            where (am.name like 'FAC%%' or am.name like 'NC%%')
            and (am.date between %(date_from)s and %(date_to)s)
            order by dbkcode, docnumber
            """,
            {
                'date_from': self.dateFrom,
                'date_to'  : self.dateTo
            })
        for row in cursor.dictfetchall():
            move = Move()
            move.fromDictRow(row)
            move.readLines(cursor)
            self.moves.append(move)
            print(move.id, move.name, move.date)