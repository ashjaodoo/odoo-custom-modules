# -*- coding: utf-8 -*-
import secrets
import string
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    portal_token = fields.Char(
        string='Portal Token',
        copy=False,
        readonly=True,
        help="Unique token for candidate portal access"
    )
    portal_user_id = fields.Many2one(
        'res.users',
        string='Portal User',
        copy=False,
        readonly=True,
        help="Portal user linked to this applicant"
    )
    credentials_sent = fields.Boolean(
        string='Credentials Sent',
        default=False,
        copy=False,
        help="Whether portal credentials email has been sent"
    )

    # -------------------------------------------------------------------------
    # Credential Generation
    # -------------------------------------------------------------------------

    def _generate_portal_token(self):
        """Generate a secure unique portal token."""
        return secrets.token_urlsafe(20)

    def _generate_temp_password(self, length=10):
        """Generate a temporary password for the portal user."""
        alphabet = string.ascii_letters + string.digits
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            # Ensure at least one digit and one letter
            if any(c.isdigit() for c in password) and any(c.isalpha() for c in password):
                return password

    # -------------------------------------------------------------------------
    # Portal User Creation
    # -------------------------------------------------------------------------

    def _get_or_create_portal_user(self, temp_password):
        """
        Find existing portal user by email or create a new one.
        Returns the res.users record.
        """
        self.ensure_one()
        email = self.email_from
        name = self.partner_name or email

        if not email:
            raise UserError(_("Applicant email is required to create portal access."))

        ResUsers = self.env['res.users'].sudo()
        ResPartner = self.env['res.partner'].sudo()

        # Check if user already exists
        existing_user = ResUsers.search([('login', '=', email)], limit=1)
        if existing_user:
            # Update password and make sure they have portal access
            existing_user.write({'password': temp_password})
            portal_group = self.env.ref('base.group_portal')
            if portal_group not in existing_user.groups_id:
                existing_user.write({'groups_id': [(4, portal_group.id)]})
            return existing_user

        # Find or create partner
        partner = ResPartner.search([('email', '=', email)], limit=1)
        if not partner:
            partner = ResPartner.create({
                'name': name,
                'email': email,
                'phone': self.partner_phone or False,
            })

        # Create portal user
        portal_group = self.env.ref('base.group_portal')
        user = ResUsers.create({
            'name': name,
            'login': email,
            'email': email,
            'password': temp_password,
            'partner_id': partner.id,
            'groups_id': [(6, 0, [portal_group.id])],
            'share': True,
        })
        return user

    # -------------------------------------------------------------------------
    # Send Credentials Email
    # -------------------------------------------------------------------------

    def action_send_portal_credentials(self):
        """
        Main method called after form submission:
        1. Generate token and password
        2. Create/update portal user
        3. Send credentials email
        """
        self.ensure_one()

        temp_password = self._generate_temp_password()
        token = self._generate_portal_token()

        # Create portal user
        portal_user = self._get_or_create_portal_user(temp_password)

        # Save token and user reference
        self.write({
            'portal_token': token,
            'portal_user_id': portal_user.id,
            'credentials_sent': True,
        })

        # Build portal URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        portal_url = f"{base_url}/my/application/{self.id}?token={token}"

        # Send email via template
        template = self.env.ref(
            'job_applicant_portal.email_template_portal_credentials',
            raise_if_not_found=False
        )
        if template:
            template.with_context(
                temp_password=temp_password,
                portal_url=portal_url,
            ).send_mail(self.id, force_send=True)
            _logger.info(
                "Portal credentials email sent to %s for applicant %s",
                self.email_from, self.partner_name
            )
        else:
            _logger.warning("Email template 'email_template_portal_credentials' not found.")

        return portal_user

    # -------------------------------------------------------------------------
    # Portal Access Check
    # -------------------------------------------------------------------------

    def _check_portal_access(self, token):
        """Validate token for portal access."""
        self.ensure_one()
        return self.portal_token and self.portal_token == token
