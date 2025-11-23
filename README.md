# SureSave

SureSave is a digital savings application backend built with Django and Django REST Framework.
This repository implements a custom user model that supports authentication using either
email or phone number, email verification via django-allauth, and JWT authentication with
Simple JWT and dj-rest-auth.

## Features

- Custom user model (`users.CustomUser`) using `email` as the `USERNAME_FIELD`.
- Login using email or phone number (`email_or_phone` field supported on login).
- Email verification with django-allauth (email confirmation sets `is_verified=True`).
- JWT authentication via `djangorestframework-simplejwt` and `dj-rest-auth`.
- API schema with `drf-spectacular`.

## Requirements

- Python 3.11+ (this project uses 3.13 in development environment but any 3.11+ should work)
- Django 5.x
- A database configured via environment variables (default expects MySQL, but SQLite can be used for local testing)

## Quickstart (Windows PowerShell)

1. Create and activate the virtual environment (if not already present):

```powershell
python -m venv suresave-env
& .\suresave-env\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file or set the following environment variables (example keys):

```
SECRET_KEY=your-secret-key
DEBUG=True
DB_ENGINE=django.db.backends.sqlite3            # or mysql/postgresql
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_TLS=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

4. Run migrations and create a superuser:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server:

```powershell
python manage.py runserver
```

## Authentication / Registration

This project uses a custom registration and login flow that integrates with `dj-rest-auth` and `allauth`.

- Registration endpoint: `/dj-rest-auth/registration/`
	- Expected JSON payload:

```json
{
	"email": "user@example.com",
	"phone_number": "1234567890",
	"full_name": "Alice Example",
	"password1": "strongpassword",
	"password2": "strongpassword"
}
```

- Login endpoint: `/dj-rest-auth/login/`
	- Accepts `email_or_phone` plus `password`. The backend maps `email_or_phone` into `email`/`username` for compatibility.

```json
{
	"email_or_phone": "user@example.com",
	"password": "yourpassword"
}
```

- After registration, an email confirmation link will be sent (console backend by default in development). When the confirmation link is clicked, the `is_verified` field on the user is set to `true` via an Allauth signal handler.

Notes:
- The `phone_number` is normalized to digits-only before save. Keep this in mind when creating users directly.
- The admin login form accepts email or phone in the username field thanks to the custom authentication backend.

## Email Confirmation

- The project is configured to use django-allauth for email verification. For development the console email backend is enabled by default so confirmation links are printed to the console.
- You can change email behavior by adjusting the email-related environment variables in your `.env` and `suresave/settings.py`.

## Running Tests

If you add tests, run them with:

```powershell
python manage.py test
```

## API Schema

- drf-spectacular is included. Visit `/api/schema/` (or the configured path) to view the OpenAPI schema when the server is running.

## Development notes

- Custom login serializer is implemented at `api/serializers.py` with `CustomLoginSerializer` — it accepts `email_or_phone` and authenticates using the custom backend in `users/backends.py`.
- The `users/signals.py` file contains a receiver for the `allauth.account.signals.email_confirmed` signal to set `user.is_verified=True`.
- If you change storage format for phone numbers, make sure to update the normalization logic in `users/models.py` and the manager.

## Contributing

- Fork the repository and open a pull request. Add tests for new functionality and keep changes minimal and focused.

## License

Specify your license here (e.g., MIT) or remove this section if not applicable.

---

If you'd like, I can also:
- Add example curl requests for registration/login, or
- Add a `.env.example` file to the repo, or
- Add unit tests for the authentication flow (email and phone). Just tell me which you'd prefer.




