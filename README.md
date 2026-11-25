# SkillBridge

SkillBridge is a Django application for students to maintain academic profiles and for faculty to describe opportunities and their required skills. Sprint 1 includes student and faculty registration, authentication, student skills, projects and certifications, faculty opportunity management, and an administrator skill catalogue. Sprint 2 adds opportunity discovery, search and filters, exact weighted skill matching, fit explanations, student applications, and ranked applicant views for owning faculty. Recommendations and other Sprint 3 stories remain upcoming.

Registration collects an email address, but authentication currently uses a username and password, rather than the email-based login in the earlier plan. Faculty registration is direct and does not verify institutional affiliation. Administrators are created with `createsuperuser`, not through public registration. Desktop and mobile visual review remains outstanding.

## Local development on Windows

Requires Python 3.14, Node.js 24 and npm. From PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm.cmd ci
npm.cmd run build:css
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/. The `runserver` command defaults to `config.settings_dev`, which enables Django's local static file server; an explicitly set `DJANGO_SETTINGS_MODULE` or `DJANGO_DEBUG=false` takes precedence. WSGI, ASGI and other management commands default to `config.settings`, where debug is disabled. Use `npm.cmd run watch:css` during frontend development. SQLite is the default; set `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` and `POSTGRES_PORT` for PostgreSQL. Supply a strong `DJANGO_SECRET_KEY` and appropriate `DJANGO_ALLOWED_HOSTS` outside local development. Production deployment and PostgreSQL have not yet been verified.

For fictional local demo accounts, set `$env:SKILLBRIDGE_ALLOW_DEMO_SEED='1'` and `$env:SKILLBRIDGE_DEMO_PASSWORD` to a local password of at least 12 characters, then run `.\.venv\Scripts\python.exe manage.py seed_demo`. The command prints that password and resets only the expected demo accounts' passwords to it. Reusing the same password makes repeated runs idempotent. It refuses PostgreSQL and is intended only for an explicitly authorised local environment. Never use demo credentials on a public instance.

Run `.\.venv\Scripts\python.exe -m pytest -v`, `.\.venv\Scripts\ruff.exe check .`, `.\.venv\Scripts\ruff.exe format --check .`, and `.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run` to verify changes.

## Contributors

Sarah Abbas, Vaibhav Khandelwal, Anirudh Goel and Vinayak Arora are acknowledged as project team members. Git history reflects actual contributions.

## Design system

The interface uses midnight navy navigation, indigo and violet hero surfaces, pearl backgrounds, and category-specific accents. Inter and Plus Jakarta Sans are served locally with system fallbacks. Shared component and motion guidance is in `docs/DESIGN_SYSTEM.md`; Tailwind compiles the source layers into `static/css/app.css`.
