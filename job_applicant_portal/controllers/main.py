# -*- coding: utf-8 -*-
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)


class JobApplicantPortalController(http.Controller):

    # =========================================================================
    # PUBLIC: Job Application Form
    # =========================================================================

    @http.route('/jobs/apply', type='http', auth='public', website=True, sitemap=True)
    def job_application_form(self, job_id=None, **kwargs):
        """Render the public job application form."""
        jobs = request.env['hr.job'].sudo().search([('website_published', '=', True)])
        selected_job = None
        if job_id:
            selected_job = request.env['hr.job'].sudo().browse(int(job_id))

        return request.render('job_applicant_portal.website_job_application_form', {
            'jobs': jobs,
            'selected_job': selected_job,
            'error': kwargs.get('error', ''),
        })

    @http.route('/jobs/apply/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def job_application_submit(self, **post):
        """Handle job application form submission."""
        # Validate required fields
        required = ['partner_name', 'email_from', 'partner_phone', 'job_id']
        for field in required:
            if not post.get(field, '').strip():
                return request.redirect(
                    f'/jobs/apply?error=missing_fields&job_id={post.get("job_id", "")}'
                )

        try:
            job = request.env['hr.job'].sudo().browse(int(post['job_id']))
            if not job.exists():
                return request.redirect('/jobs/apply?error=invalid_job')

            # Get the first "New" stage for this job's department
            stage = request.env['hr.recruitment.stage'].sudo().search(
                [('name', 'ilike', 'New')], limit=1
            )

            # Create applicant record
            applicant = request.env['hr.applicant'].sudo().create({
                'partner_name': post['partner_name'].strip(),
                'email_from': post['email_from'].strip().lower(),
                'partner_phone': post['partner_phone'].strip(),
                'job_id': job.id,
                'department_id': job.department_id.id or False,
                'stage_id': stage.id if stage else False,
                'description': post.get('cover_letter', '').strip() or False,
                'source_id': request.env.ref(
                    'utm.utm_source_website', raise_if_not_found=False
                ) and request.env.ref('utm.utm_source_website').id or False,
            })

            # Send portal credentials email
            applicant.action_send_portal_credentials()

            _logger.info(
                "New job application submitted: %s for %s",
                post['partner_name'], job.name
            )

            return request.redirect('/jobs/apply/thank-you')

        except Exception as e:
            _logger.error("Job application submission error: %s", str(e))
            return request.redirect('/jobs/apply?error=submission_failed')

    @http.route('/jobs/apply/thank-you', type='http', auth='public', website=True)
    def job_application_thankyou(self, **kwargs):
        """Thank you page after successful submission."""
        return request.render('job_applicant_portal.website_job_application_thankyou', {})

    # =========================================================================
    # PORTAL: Candidate Application Status
    # =========================================================================

    @http.route('/my/application', type='http', auth='user', website=True)
    def my_application(self, **kwargs):
        """Portal page - candidate views their application status."""
        user = request.env.user

        # Find applicant record linked to this portal user
        applicant = request.env['hr.applicant'].sudo().search(
            [('portal_user_id', '=', user.id)], limit=1
        )

        if not applicant:
            return request.render('job_applicant_portal.portal_no_application', {})

        # Get all stages in order for progress display
        stages = request.env['hr.recruitment.stage'].sudo().search(
            [], order='sequence asc'
        )

        # Build kanban stage info
        kanban_stages = []
        current_sequence = applicant.stage_id.sequence if applicant.stage_id else 0

        for stage in stages:
            kanban_stages.append({
                'id': stage.id,
                'name': stage.name,
                'is_current': stage.id == applicant.stage_id.id,
                'is_done': stage.sequence < current_sequence,
                'sequence': stage.sequence,
            })

        return request.render('job_applicant_portal.portal_my_application', {
            'applicant': applicant,
            'stages': kanban_stages,
            'page_name': 'application',
        })

    @http.route('/my/application/<int:applicant_id>', type='http', auth='public', website=True)
    def my_application_token(self, applicant_id, token=None, **kwargs):
        """
        Token-based access for first login before portal session is established.
        Redirects to login with next URL set to /my/application
        """
        applicant = request.env['hr.applicant'].sudo().browse(applicant_id)

        if not applicant.exists():
            return request.redirect('/web/login')

        if not applicant._check_portal_access(token):
            return request.redirect('/web/login?error=invalid_token')

        # If user is already logged in and is the portal user
        if request.env.user != request.env.ref('base.public_user') and \
                request.env.user.id == applicant.portal_user_id.id:
            return request.redirect('/my/application')

        # Redirect to login with next pointing to portal
        return request.redirect(
            f'/web/login?redirect=/my/application&login={applicant.email_from}'
        )
