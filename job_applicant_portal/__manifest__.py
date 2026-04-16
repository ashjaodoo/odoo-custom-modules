# -*- coding: utf-8 -*-
{
    'name': 'Job Applicant Portal',
    'version': '19.0.1.0.0',
    'category': 'Recruitment',
    'summary': 'Public job application form with portal access and kanban status tracking',
    'description': """
        Job Applicant Portal
        ====================
        - Public job application form (website)
        - "I'm Feeling Lucky" submit button
        - Auto email with portal credentials on submission
        - Candidate portal: view application status
        - Kanban stages: New, 1st Interview, 2nd Interview, On Hold, Hired, Rejected
    """,
    'author': 'Custom',
    'depends': [
        'base',
        'hr_recruitment',
        'portal',
        'website',
        'mail',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/recruitment_stages.xml',
        'data/mail_template.xml',
        'views/website_job_form_template.xml',
        'views/portal_my_application_template.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'job_applicant_portal/static/src/js/job_form.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
