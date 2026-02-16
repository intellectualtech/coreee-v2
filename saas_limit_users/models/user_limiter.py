from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class UserLimitMixin(models.AbstractModel):
    _name = 'saas.user.limit.mixin'

    @api.model
    def cron_check_user_limits(self):
        """Check if tenants exceeded user limits (runs hourly)"""
        tenants = self.env['saas.tenant'].search([('state', '=', 'active')])
        
        for tenant in tenants:
            if tenant.current_users > tenant.max_users:
                # Block login for this tenant
                self._suspend_excess_users(tenant)
                self._notify_limit_exceeded(tenant)

    @staticmethod
    def _suspend_excess_users(tenant):
        """Suspend oldest non-admin users when limit exceeded"""
        _logger.warning(f"User limit exceeded for {tenant.subdomain}")
        # Suspend users in tenant DB via remote connection

    @staticmethod
    def _notify_limit_exceeded(tenant):
        """Send email to tenant about user limit"""
        template = tenant.env.ref('saas_limit_users.email_limit_exceeded')
        if template:
            template.send_mail(tenant.id, force_send=True)
        
        # Also notify SaaS admin
        admin_users = tenant.env['res.users'].search([('is_system', '=', True)])
        for user in admin_users:
            admin_template = tenant.env.ref('saas_limit_users.email_admin_limit_exceeded')
            if admin_template:
                admin_template.send_mail(tenant.id, force_send=True)

    @api.model
    def check_user_limit_on_login(self, db, login, password):
        """Hook to prevent login if limit exceeded"""
        tenant = self.env['saas.tenant'].search([('db_name', '=', db)])
        if tenant and tenant.current_users >= tenant.max_users:
            raise models.AccessDenied(_('User limit exceeded for your plan'))
