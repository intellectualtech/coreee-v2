from odoo import http, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaaSPortal(http.Controller):

    @http.route('/saas/signup', auth='public', website=True)
    def signup_page(self, **kwargs):
        """SaaS signup page"""
        plans = http.request.env['saas.plan'].sudo().get_plans_for_website()
        return http.request.render('saas_portal.signup_template', {
            'plans': plans,
        })

    @http.route('/saas/create', auth='public', type='json', csrf=True)
    def create_tenant(self, **post):
        """Create new tenant"""
        try:
            plan = http.request.env['saas.plan'].sudo().browse(int(post.get('plan_id')))
            if not plan:
                return {'error': 'Invalid plan'}

            # Validate subdomain
            subdomain = post.get('subdomain', '').lower().strip()
            if not subdomain or len(subdomain) < 3:
                return {'error': 'Subdomain must be at least 3 characters'}

            # Check if subdomain exists
            existing = http.request.env['saas.tenant'].sudo().search([
                ('subdomain', '=', subdomain)
            ])
            if existing:
                return {'error': 'Subdomain already taken'}

            # Create tenant
            tenant = http.request.env['saas.tenant'].sudo().create({
                'name': post.get('company_name'),
                'subdomain': subdomain,
                'email': post.get('email'),
                'contact_person': post.get('contact_person'),
                'plan_id': plan.id,
                'company_size': post.get('company_size'),
                'industry': post.get('industry'),
            })

            # Create database
            tenant.action_create_database()

            # Create subscription
            subscription = http.request.env['saas.subscription'].sudo().create_trial_subscription(
                tenant.id, plan.id
            )
            tenant.subscription_id = subscription.id

            return {
                'success': True,
                'message': f'Account created! Check your email at {post.get("email")} for login details.',
                'login_url': f'{subdomain}.yourdomain.com',
            }

        except ValidationError as e:
            return {'error': str(e)}
        except Exception as e:
            _logger.error(f'Signup error: {e}')
            return {'error': 'An error occurred. Please try again.'}

    @http.route('/saas/pricing', auth='public', website=True)
    def pricing_page(self, **kwargs):
        """Pricing page"""
        plans = http.request.env['saas.plan'].sudo().get_plans_for_website()
        return http.request.render('saas_portal.pricing_template', {
            'plans': plans,
        })

    @http.route('/saas/dashboard', auth='user')
    def tenant_dashboard(self, **kwargs):
        """Tenant portal dashboard (after login in tenant DB)"""
        return http.request.render('saas_portal.dashboard_template')
