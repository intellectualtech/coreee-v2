from datetime import datetime, timedelta
from odoo import models, fields, api, _

class SaaSSubscription(models.Model):
    _name = 'saas.subscription'
    _description = 'SaaS Subscription'
    _inherit = ['mail.thread']

    tenant_id = fields.Many2one('saas.tenant', string='Tenant', required=True, ondelete='cascade')
    plan_id = fields.Many2one('saas.plan', string='Plan', required=True)
    
    # Billing
    billing_interval = fields.Selection([
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], string='Billing Interval', default='monthly')
    
    next_invoice_date = fields.Date(string='Next Invoice Date')
    last_invoice_date = fields.Date(string='Last Invoice Date')
    
    # Trial
    is_trial = fields.Boolean(string='Is Trial', default=True)
    trial_start = fields.Date(string='Trial Start')
    trial_end = fields.Date(string='Trial End')
    
    # Status
    state = fields.Selection([
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='trial', tracking=True)
    
    # Invoices
    invoice_ids = fields.One2many('saas.invoice', 'subscription_id', string='Invoices')
    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count')
    
    # Pricing calculation
    monthly_price = fields.Float(string='Monthly Price', compute='_compute_monthly_price')
    yearly_price = fields.Float(string='Yearly Price', compute='_compute_yearly_price')
    
    created_date = fields.Datetime(string='Created', default=fields.Datetime.now)

    def _compute_monthly_price(self):
        for sub in self:
            plan = sub.plan_id
            users = sub.tenant_id.current_users
            sub.monthly_price = plan.price_monthly + (users * plan.price_per_user)

    def _compute_yearly_price(self):
        for sub in self:
            sub.yearly_price = sub.monthly_price * 12

    def _compute_invoice_count(self):
        for sub in self:
            sub.invoice_count = len(sub.invoice_ids)

    @api.model
    def create_trial_subscription(self, tenant_id, plan_id):
        """Create trial subscription for new tenant"""
        trial_end = fields.Date.today() + timedelta(days=plan_id.trial_days)
        return self.create({
            'tenant_id': tenant_id,
            'plan_id': plan_id,
            'is_trial': True,
            'trial_start': fields.Date.today(),
            'trial_end': trial_end,
            'state': 'trial',
        })

    @api.model
    def cron_check_trial_expiration(self):
        """Check for expired trials daily"""
        expired = self.search([
            ('is_trial', '=', True),
            ('trial_end', '<', fields.Date.today()),
            ('state', '=', 'trial'),
        ])
        for sub in expired:
            sub.state = 'suspended'
            sub.tenant_id.state = 'trial_expired'
            self._send_trial_expired_email(sub)

    @api.model
    def cron_generate_invoices(self):
        """Generate recurring invoices"""
        today = fields.Date.today()
        active_subs = self.search([
            ('state', 'in', ['active', 'past_due']),
            ('is_trial', '=', False),
        ])
        
        for sub in active_subs:
            if sub.next_invoice_date and sub.next_invoice_date <= today:
                sub._generate_invoice()

    def _generate_invoice(self):
        """Generate invoice for subscription"""
        invoice = self.env['saas.invoice'].create({
            'subscription_id': self.id,
            'tenant_id': self.tenant_id.id,
            'amount': self.monthly_price if self.billing_interval == 'monthly' else self.yearly_price,
            'invoice_date': fields.Date.today(),
            'due_date': fields.Date.today() + timedelta(days=14),
            'state': 'draft',
        })
        
        # Set next invoice date
        if self.billing_interval == 'monthly':
            self.next_invoice_date = fields.Date.today() + timedelta(days=30)
        else:
            self.next_invoice_date = fields.Date.today() + timedelta(days=365)
        
        self.last_invoice_date = fields.Date.today()
        return invoice

    def action_upgrade_plan(self, new_plan_id):
        """Upgrade to different plan"""
        self.plan_id = new_plan_id
        # Generate prorated invoice
        self._generate_prorated_invoice()

    def action_convert_to_paid(self):
        """Convert trial to paid subscription"""
        self.is_trial = False
        self.state = 'active'
        self.next_invoice_date = fields.Date.today() + timedelta(days=30)
        self._generate_invoice()

    @staticmethod
    def _send_trial_expired_email(subscription):
        """Notify tenant trial expired"""
        template = subscription.env.ref('saas_subscription.email_trial_expired')
        if template:
            template.send_mail(subscription.tenant_id.id, force_send=True)
