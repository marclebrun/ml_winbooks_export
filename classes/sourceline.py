# -*- coding: utf-8 -*-

class SourceLine:

    def __init__(self):
        self.id                 = None
        self.name               = None
        self.amounteur          = None
        self.accountgl          = None
        self.partner_id         = None
        self.product_id         = None
        self.tax_base_amount    = None
        self.account_tax_amount = None
        self.partner_name       = None
        self.partner_ref        = None
        self.tax_line_id        = None
        self.tax_ids            = []
    
    def fromDictRow(self, row):
        self.id                 = row['id']
        self.name               = row['name']
        self.amounteur          = row['amounteur']
        self.accountgl          = row['accountgl']
        self.partner_id         = row['partner_id']
        self.product_id         = row['product_id']
        self.tax_base_amount    = row['tax_base_amount']
        self.account_tax_amount = row['account_tax_amount']
        self.partner_name       = row['partner_name']
        self.partner_ref        = row['partner_ref']
        self.tax_line_id        = row['tax_line_id']
