# The Tree House — Restaurant & Hotel Website

A responsive Flask website starter for a restaurant + hotel business. Includes a sample menu, food-order form, hotel room/table booking form, SQLite persistence, confirmation pages, and a basic admin view.

## Features
- Responsive homepage with menu cards and room/table booking
- Food orders with quantities, delivery details, notes and automatic total
- Hotel room booking with check-in/check-out validation
- Restaurant table booking request
- SQLite database created automatically (`tree_house.db`)
- Basic order/booking admin page at `/admin`
- Gunicorn `Procfile` for deployment

## Requirements
- Python 3.10 or newer
- pip

## Run on Windows (PowerShell)
```powershell
cd tree_house_flask
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Important before going live
1. Replace sample menu items/prices, hotel details, contact details, address, and images with your real business information.
2. Change `SECRET_KEY` using an environment variable. Do not use the development fallback in production.
3. **Protect `/admin` with authentication** before publishing. It is intentionally a demo view and currently has no login.
4. This starter stores order/booking requests; it does **not** charge payments or guarantee live room/table availability. Confirm each booking with the customer.
5. Add HTTPS, privacy policy, data retention controls and a production database if needed.
6. Configure an email/SMS/WhatsApp notification provider if you want instant alerts.

## Deploy
For a typical Render-style deployment:
- Push the project to a Git repository.
- Create a Python web service and use the included `Procfile` or start command `gunicorn app:app`.
- Add environment variable `SECRET_KEY`.
- Note: local SQLite files on many hosting platforms may not persist across deploys unless a persistent disk is configured. Use a managed PostgreSQL database for production.

## Project structure
```text
tree_house_flask/
├── app.py
├── requirements.txt
├── Procfile
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── confirmation.html
│   └── admin.html
└── static/
    ├── css/style.css
    └── js/main.js
```
