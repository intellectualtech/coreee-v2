from odoo import models, fields, api

class SaaSPlan(models.Model):
    _name = 'saas.plan'
    _description = 'SaaS Plan'

    name = fields.Char(string='Plan Name', required=True)
    description = fields.Text(string='Description')
    
    # Pricing
    price_monthly = fields.Float(string='Monthly Price')
    price_yearly = fields.Float(string='Yearly Price')
    price_per_user = fields.Float(string='Price Per User (Monthly)')
    setup_fee = fields.Float(string='Setup Fee', default=0)
    
    # User Limits
    min_users = fields.Integer(string='Min Users', default=1)
    max_users = fields.Integer(string='Max Users', default=999)
    
    # Trial
    trial_days = fields.Integer(string='Trial Days', default=14)
    
    # Features
    included_modules = fields.Many2many(
        'ir.module.module',
        string='Included Modules',
        domain=[('state', '=', 'installed')]
    )
    
    # Status
    active = fields.Boolean(string='Active', default=True)
    sort_order = fields.Integer(string='Sort Order', default=10)
    
    class Meta:
        _order = 'sort_order, name'

    @api.model
    def get_plans_for_website(self):
        """Get plans for public display"""
        return self.search([('active', '=', True)], order='sort_order')
