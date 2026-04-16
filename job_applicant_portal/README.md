# Job Applicant Portal — Odoo 19
## Custom Module

---

## Features
- ✅ Public job application form at `/jobs/apply`
- ✅ "I'm Feeling Lucky" submit button
- ✅ Auto email with portal credentials immediately after form submission
- ✅ Candidate portal at `/my/application` with:
  - Personal info display (Name, Email, Phone, Position)
  - Real-time kanban stage progress tracker
  - Current status explanation banner
  - Activity timeline
- ✅ 6 Kanban stages: New → 1st Interview → 2nd Interview → On Hold → Hired → Rejected

---

## Installation Steps

### 1. Copy Module
```bash
cp -r job_applicant_portal /path/to/odoo/custom_addons/
```

### 2. Update Odoo Config
Make sure `custom_addons` is in your `addons_path` in `odoo.conf`:
```ini
addons_path = /odoo/addons,/odoo/custom_addons
```

### 3. Restart Odoo
```bash
sudo systemctl restart odoo
# OR
python odoo-bin --config=odoo.conf
```

### 4. Install Module
- Go to: **Settings → Apps → Update Apps List**
- Search: `Job Applicant Portal`
- Click **Install**

---

## Configuration After Install

### A. Add Job Positions (Required)
1. Go to **Recruitment → Job Positions**
2. Create positions (e.g. "UI Designer", "Backend Developer")
3. Set **Website Published = True** so they appear in the form

### B. Configure Outgoing Email
1. Go to **Settings → Technical → Outgoing Mail Servers**
2. Add your SMTP server (Gmail, SendGrid, etc.)
3. Test the connection

### C. Publish Jobs on Website
1. Go to **Website → Jobs** (if using website job pages)
2. OR just ensure jobs are active in Recruitment

---

## How It Works

```
Candidate fills form at /jobs/apply
           ↓
Clicks "I'm Feeling Lucky"
           ↓
Controller creates hr.applicant record (stage: New)
           ↓
Portal user created with temp password
           ↓
Email sent → credentials + portal link
           ↓
Candidate logs in at /web/login
           ↓
Redirected to /my/application
           ↓
Sees kanban progress + current status
           ↓
HR moves card in backend Kanban
           ↓
Portal updates automatically ✅
```

---

## URL Reference

| URL | Auth | Description |
|-----|------|-------------|
| `/jobs/apply` | Public | Job application form |
| `/jobs/apply/submit` | Public (POST) | Form submission handler |
| `/jobs/apply/thank-you` | Public | Success page |
| `/my/application` | Portal User | Candidate status portal |
| `/my/application/<id>?token=<token>` | Public | Token-based first-time access |

---

## Kanban Stages (Auto-created on install)

| Stage | Sequence | Folded | Hired Stage |
|-------|----------|--------|-------------|
| New | 1 | No | No |
| 1st Interview | 2 | No | No |
| 2nd Interview | 3 | No | No |
| On Hold | 4 | Yes | No |
| Hired | 5 | No | Yes |
| Rejected | 6 | Yes | No |

---

## Module Structure

```
job_applicant_portal/
├── __manifest__.py
├── __init__.py
├── controllers/
│   ├── __init__.py
│   └── main.py              ← Form submit + portal routes
├── models/
│   ├── __init__.py
│   └── hr_applicant.py      ← Credential generation + email sending
├── data/
│   ├── recruitment_stages.xml   ← 6 kanban stages
│   └── mail_template.xml        ← Credentials email template
├── views/
│   ├── website_job_form_template.xml      ← Public form + thank you
│   ├── portal_my_application_template.xml ← Candidate portal
│   └── res_config_settings_views.xml
├── security/
│   └── ir.model.access.csv
└── static/src/js/
    └── job_form.js          ← Frontend UX
```

---

## Troubleshooting

**Email not sending?**
→ Check Settings → Technical → Outgoing Mail Servers

**No jobs in dropdown?**
→ Go to Recruitment → Job Positions → set Website Published = True

**Portal shows "No Application Found"?**
→ Make sure candidate logged in with the SAME email used in the form

**Module not appearing in Apps?**
→ Run: Settings → Apps → Update Apps List first
