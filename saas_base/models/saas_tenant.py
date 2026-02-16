import logging
import psycopg2
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class SaaSTenant(models.Model):
    _name = 'saas.tenant'
    _description = 'SaaS Tenant (Client Database)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Company Name', required=True, tracking=True)
    subdomain = fields.Char(string='Subdomain', required=True, unique=True, tracking=True)
    custom_domain = fields.Char(string='Custom Domain', tracking=True)
    
    # Database info
    db_name = fields.Char(string='Database Name', required=True, unique=True, readonly=True)
    admin_user = fields.Char(string='Admin Username', default='admin', readonly=True)
    admin_password = fields.Char(string='Admin Password', readonly=True)
    
    # Contact & Billing
    email = fields.Char(string='Admin Email', required=True, tracking=True)
    phone = fields.Char(string='Phone')
    contact_person = fields.Char(string='Contact Person')
    
    # Plan & Subscription
    plan_id = fields.Many2one('saas.plan', string='Plan', required=True, tracking=True)
    subscription_id = fields.Many2one('saas.subscription', string='Subscription', readonly=True)
    max_users = fields.Integer(string='Max Users', related='plan_id.max_users', readonly=True)
    current_users = fields.Integer(string='Current Users', compute='_compute_current_users')
    
    # Trial & Dates
    trial_start_date = fields.Date(string='Trial Start', readonly=True)
    trial_end_date = fields.Date(string='Trial End', readonly=True)
    is_trial = fields.Boolean(string='Is Trial', default=True)
    trial_days = fields.Integer(string='Trial Days', related='plan_id.trial_days')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('trial_expired', 'Trial Expired'),
        ('suspended', 'Suspended'),
        ('deleted', 'Deleted'),
    ], string='Status', default='draft', tracking=True)
    
    # Additional Info
    industry = fields.Char(string='Industry')
    company_size = fields.Selection([
        ('small', '1-10'),
        ('medium', '11-50'),
        ('large', '50+'),
    ], string='Company Size')
    
    notes = fields.Text(string='Internal Notes')
    created_date = fields.Datetime(string='Created', default=fields.Datetime.now, readonly=True)
    
    _sql_constraints = [
        ('subdomain_unique', 'unique(subdomain)', 'Subdomain must be unique!'),
        ('db_name_unique', 'unique(db_name)', 'Database name must be unique!'),
    ]

    @api.constrains('subdomain')
    def _check_subdomain(self):
        for record in self:
            if not record.subdomain or not record.subdomain.replace('-', '').isalnum():
                raise ValidationError(_('Subdomain can only contain letters, numbers, and hyphens'))
            if len(record.subdomain) < 3:
                raise ValidationError(_('Subdomain must be at least 3 characters'))

    def _compute_current_users(self):
        for tenant in self:
            try:
                # Count active users in tenant's database
                self.env.cr.execute("""
                    SELECT COUNT(*) FROM res_users 
                    WHERE db_name = %s AND active = True
                """, (tenant.db_name,))
                tenant.current_users = self.env.cr.fetchone()[0]
            except Exception as e:
                _logger.warning(f"Could not count users for {tenant.db_name}: {e}")
                tenant.current_users = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('db_name'):
                vals['db_name'] = f"saas_{vals['subdomain'].replace('-', '_')}_{fields.Datetime.now().strftime('%s')}"
        return super().create(vals_list)

    def action_create_database(self):
        """Create tenant database from template"""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('Database already created'))
        
        try:
            self._create_db_from_template()
            self._create_admin_user()
            self.trial_start_date = fields.Date.today()
            self.trial_end_date = fields.Date.today() + timedelta(days=self.trial_days)
            self.is_trial = True
            self.state = 'active'
            self._send_welcome_email()
        except Exception as e:
            _logger.error(f"Failed to create database for {self.subdomain}: {e}")
            raise ValidationError(_('Failed to create database: %s') % str(e))

    def _create_db_from_template(self):
        """Create PostgreSQL database from template"""
        db = self.env.cr.dbname
        template_db = 'saas_template'
        
        # PostgreSQL connection
        import psycopg2
        from odoo.sql_db import dsn
        
        conn = psycopg2.connect(dsn(self.env.cr.dbname))
        conn.autocommit = True
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"CREATE DATABASE {self.db_name} TEMPLATE {template_db}")
            _logger.info(f"Created database: {self.db_name}")
        except psycopg2.Error as e:
            if 'already exists' not in str(e):
                raise
        finally:
            cursor.close()
            conn.close()

    def _create_admin_user(self):
        """Create admin user in tenant database"""
        import secrets
        self.admin_password = secrets.token_urlsafe(16)
        # This will be executed in the tenant's database via a separate connection

    def _send_welcome_email(self):
        """Send welcome email to tenant admin"""
        template = self.env.ref('saas_base.email_template_welcome', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    def action_suspend(self):
        self.state = 'suspended'

    def action_activate(self):
        self.state = 'active'

    def action_delete(self):
        self.state = 'deleted'
        # In production, physically delete the database

    def action_upgrade_plan(self):
        """Open wizard to upgrade plan"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'saas.upgrade.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_tenant_id': self.id},
        }
