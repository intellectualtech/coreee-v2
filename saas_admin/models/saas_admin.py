from odoo import models, fields, api, _
import psycopg2
import logging

_logger = logging.getLogger(__name__)

class SaaSAdminActions(models.Model):
    _name = 'saas.admin.action'
    _description = 'Admin Actions Log'

    tenant_id = fields.Many2one('saas.tenant', string='Tenant')
    action = fields.Selection([
        ('create', 'Create'),
        ('suspend', 'Suspend'),
        ('activate', 'Activate'),
        ('delete', 'Delete'),
        ('module_install', 'Install Module'),
        ('module_uninstall', 'Uninstall Module'),
        ('user_limit_change', 'Change User Limit'),
        ('plan_change', 'Change Plan'),
    ], string='Action')
    
    details = fields.Text(string='Details')
    executed_by = fields.Many2one('res.users', string='Executed By', default=lambda self: self.env.user)
    executed_date = fields.Datetime(string='Executed', default=fields.Datetime.now)

class SaaSAdminPanel(models.AbstractModel):
    _name = 'saas.admin.mixin'

    @staticmethod
    def install_module_remote(tenant_db, module_name):
        """Install module in tenant database"""
        try:
            # Execute remote SQL to install module
            _logger.info(f"Installing {module_name} in {tenant_db}")
            # Implementation would use remote DB connection
        except Exception as e:
            _logger.error(f"Failed to install module: {e}")
            raise

    @staticmethod
    def get_tenant_stats():
        """Get SaaS platform statistics"""
        env = models.request.env
        return {
            'total_tenants': env['saas.tenant'].search_count([]),
            'active_tenants': env['saas.tenant'].search_count([('state', '=', 'active')]),
            'trial_tenants': env['saas.tenant'].search_count([('is_trial', '=', True)]),
            'total_users': sum(t.current_users for t in env['saas.tenant'].search([])),
            'monthly_revenue': sum(s.monthly_price for s in env['saas.subscription'].search([])),
        }
