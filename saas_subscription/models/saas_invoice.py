from odoo import models, fields, api

class SaaSInvoice(models.Model):
    _name = 'saas.invoice'
    _description = 'SaaS Invoice'
    _inherit = ['mail.thread']

    subscription_id = fields.Many2one('saas.subscription', string='Subscription', required=True)
    tenant_id = fields.Many2one('saas.tenant', string='Tenant', required=True)
    
    invoice_date = fields.Date(string='Invoice Date', required=True)
    due_date = fields.Date(string='Due Date', required=True)
    
    amount = fields.Float(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda s: s._get_default_currency())
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', tracking=True)
    
    paid_date = fields.Date(string='Paid Date')
    notes = fields.Text(string='Notes')
    
    # Accounting
    account_move_id = fields.Many2one('account.move', string='Account Move', readonly=True)

    @staticmethod
    def _get_default_currency():
        return 1  # USD

    def action_post(self):
        """Post invoice to accounting"""
        self.state = 'posted'
        # Create account move here if needed

    def action_mark_paid(self):
        self.state = 'paid'
        self.paid_date = fields.Date.today()
        self.subscription_id.state = 'active'

    def action_send_email(self):
        """Send invoice to tenant"""
        template = self.env.ref('saas_subscription.email_invoice_sent')
        if template:
            template.send_mail(self.id, force_send=True)
