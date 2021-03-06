# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AdOrderLineMakeInvoice(models.TransientModel):
    _inherit = "ad.order.line.make.invoice"

    @api.multi
    def _prepare_invoice_line(self, line):
        res = super(AdOrderLineMakeInvoice, self)._prepare_invoice_line(line)
        if line.filtered('subscription'):
            if not line.product_id.delivery_obligation_account_id:
                raise UserError(_('Please define an delivery Obligation account for product %s')%line.product_id.name)
            res['account_id'] = line.product_id.delivery_obligation_account_id.id
            res['start_date'] = line.start_date
            res['end_date'] = line.end_date
            res['price_unit'] = line.price_unit
            res['name'] = line.name
        return res

    @api.model
    def _prepare_invoice(self, partner, published_customer, payment_mode, operating_unit, lines, invoice_date, posting_date):
        res = super(AdOrderLineMakeInvoice, self)._prepare_invoice(partner, published_customer, payment_mode,
                                                                   operating_unit, lines, invoice_date, posting_date)
        for invline in lines['lines']:
            if invline.sale_line_ids.filtered('subscription'):
                res['ad'] = False
                res['payment_term_id'] = partner.property_subscription_payment_term_id.id or False
                pay_mode = partner.subscription_customer_payment_mode_id
                res['payment_mode_id'] = pay_mode.id or False
                if res['type'] == 'out_invoice':
                    if pay_mode and pay_mode.bank_account_link == 'fixed':
                        res['partner_bank_id'] = pay_mode.fixed_journal_id.bank_account_id
                break
        return res
