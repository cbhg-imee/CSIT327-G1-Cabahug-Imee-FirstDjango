# CampusConnect

A Django campus portal with user registration, login, a secure per-user profile page,
and a role-aware dashboard, wrapped in a **Tactile Neomorphic Industrial Control Panel**
interface (raised/recessed panels, physical push-buttons, pulsing LED indicators and
segmented LCD readouts) built on Bootstrap 5.

## Author

| | |
|---|---|
| **Name** | Cabahug, Imee |
| **Section** | G1 |
| **School** | Cebu Institute of Technology – University (CIT-U) |
| **Course / Subject** | CSIT327-Information Management 2 |


## Features

- **Sign up** with Django's `messages` framework: a success notification is shown as a dismissible Bootstrap alert.
- **Login / Logout** with Bootstrap-styled forms.
- **Profile page** (`UpdateView`) where users view/update their own details.
  - Anonymous users are redirected to the login page.
  - Logged-in users get **403 Forbidden** when trying to view or edit another user's profile (IDOR protection).
  - `role`, `is_staff` and `is_superuser` cannot be changed through the profile or sign-up forms.
- **Dark mode**: a physical rocker switch in the navbar toggles light/dark. It follows your system preference by default and remembers your choice.
- **Dashboard** with LCD-style readouts (member count, role, course, last login), a segmented *profile completeness* gauge, system-status LEDs and quick actions.
- **Themed error pages**: custom `403` (access denied) and `404` (not found) pages in the same control-panel style.
- **Accessible contrast**: signal colors stay on LEDs/glows; text uses WCAG-AA-compliant shades in both themes.
- **Admin panel** restricted to users with the `ADMIN` role.
- Shared `templates/base.html` (Bootstrap 5 CDN, neomorphic CSS, responsive navbar, messages container) extended by every page.

## Tech stack

Python 3.12+ · Django 6.1 · SQLite · Bootstrap 5.3 (CDN) · JetBrains Mono (Google Fonts)

## Project structure

```
campusconnect/            project settings & root URLs
accounts/                 CustomUser model, forms, SignUpView, ProfileUpdateView
dashboard/                DashboardView, AdminPanelView
templates/
  base.html               layout + neomorphic CSS + navbar + messages
  includes/               reusable form-field / form-error partials
  registration/           login.html, signup.html
  accounts/profile.html   profile edit panel
  dashboard/              home.html, admin_panel.html
  403.html, 404.html      themed error pages
```

## Setup and execution

```bash
# 1. Clone and enter the project
git clone https://github.com/cbhg-imee/CSIT327-G1-Cabahug-Imee-FirstDjango.git
cd CSIT327-G1-Cabahug-Imee-FirstDjango

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate             # Windows:
source .venv/bin/activate          # macOS/Linux

# 3. Install dependencies
pip install django

# 4. Apply database migrations
python manage.py migrate

# 5. (Optional) create an administrator account
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

Then open <http://127.0.0.1:8000/> in browser.

| URL | Description |
|---|---|
| `/accounts/signup/` | Create an account |
| `/accounts/login/` | Log in |
| `/accounts/profile/<id>/` | Edit **your own** profile (403 for anyone else's) |
| `/` | Dashboard (login required) |
| `/admin_panel/` | Members list (`ADMIN` role only) |
| `/admin/` | Django admin site |



## Running the tests

```bash
python manage.py test
```
