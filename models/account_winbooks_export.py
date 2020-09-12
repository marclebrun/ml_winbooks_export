# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import datetime
from io import BytesIO
import base64
from .export import Export

class MLWinbooksExport(models.TransientModel):
    _name = 'ml.winbooks.export'
    _description = 'ML Winbooks Export'

    data = fields.Binary(
        string   = 'CSV',
        readonly = True,
    )

    export_filename = fields.Char(
        string  = 'CSV Filename',
        size    = 128,
        default = 'export.csv'
    )

    company_id = fields.Many2one(
        string       = 'Company',
        comodel_name = 'res.company',
        readonly     = True,
        default      = lambda self: self.env.user.company_id
    )
    
    date_from = fields.Date(
        string   = 'Start Date',
        required = True
    )
    
    date_to = fields.Date(
        string   = 'End Date',
        required = True
    )

    def action_manual_export_invoice_entries(self):
        self.ensure_one()
        self.export_filename = 'ANT.txt'

        d = self.read(['date_from', 'date_to'])[0]

        export = Export()
        export.setDates(d['date_from'], d['date_to'])
        export.readData(self.env.cr)
        export.process()

        # FICHIER POUR DEBUG
        debug_export_path = '/home/marc/odoo/export_winbooks/MODULE_DEBUG.txt'
        f = open(debug_export_path, "w")
        f.write(export.getCsvOutput())
        f.close()
        print("Données exportées dans le fichier \"%s\"" % debug_export_path)

        self.write({
            'data': base64.encodestring(export.getCsvOutput().encode())
        })

        return {
            'type'     : 'ir.actions.act_window',
            'res_model': 'ml.winbooks.export',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id'   : self.id,
            'views'    : [(False, 'form')],
            'target'   : 'new',
        }

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        # Find the dates of the previous month
        today = datetime.date.today()
        first = today.replace(day = 1)
        lastMonthEnd = first - datetime.timedelta(days=1)
        lastMonthStart = lastMonthEnd.replace(day=1)

        res.update({
            'date_from': lastMonthStart,
            'date_to'  : lastMonthEnd,
        })
        return res
