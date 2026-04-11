# 🐍 Python WSGI Entry Point Guide

## Overview

Gunicorn requires a WSGI entry point in the format `module:variable`. This document helps you identify the correct entry point for your Python web application.

---

## Common Framework Entry Points

### Flask Applications

**Standard structure:**
```
myapp/
├── app.py          # Entry point: app:app
├── wsgi.py         # Alternative: wsgi:application
└── __pycache__/
```

| Scenario | WSGI Entry | Example Command |
|----------|------------|-----------------|
| **Flask app in app.py** | `app:app` | `gunicorn app:app` |
| **Flask app with factory pattern** | `wsgi:application` | `gunicorn wsgi:application` |
| **Module named differently** | `mysite:app` | `gunicorn mysite:app` |

**Example - Flask with factory pattern:**
```python
# wsgi.py
from app import create_app

application = create_app()
```

Run with:
```bash
gunicorn wsgi:application
```

---

### Django Applications

Django uses its own WSGI handler, typically located in the project directory.

**Standard structure:**
```
myproject/
├── manage.py
├── wsgi.py         # Always: myproject.wsgi:application
├── asgi.py
└── myapp/
```

| Project Name | WSGI Entry |
|--------------|------------|
| `myproject` | `myproject.wsgi:application` |
| `webapp` | `webapp.wsgi:application` |

**Example - Django deployment:**
```bash
# Set WSGI_ENTRY environment variable
export WSGI_ENTRY=myproject.wsgi:application

gunicorn --workers 4 --bind unix:/var/www/myproject/gunicorn.sock $WSGI_ENTRY
```

---

### FastAPI Applications

FastAPI uses Starlette ASGI server but works with Gunicorn via `uvicorn[gunicorn]`.

**Standard structure:**
```
fastapi_app/
├── main.py       # Entry point: main:app
└── requirements.txt
```

| Format | WSGI Entry (with uvicorn) |
|--------|---------------------------|
| **ASGI app** | `main:app` |
| **Custom module** | `api:application` |

**Note:** For FastAPI, install `uvicorn[gunicorn]`:
```bash
pip install uvicorn[gunicorn]
```

Then configure gunicorn to use the `uvicorn.workers.UvicornWorker`:
```ini
ExecStart=/var/www/{project}/venv/bin/gunicorn -c gunicorn_config.py main:app
```

**gunicorn_config.py:**
```python
worker_class = 'uvicorn.workers.UvicornWorker'
workers = 4
bind = 'unix:/var/www/{project}/gunicorn.sock'
```

---

## How to Find Your Entry Point

### Method 1: Look at existing files

Check if there's an `app.py`, `wsgi.py`, or `main.py`:

```bash
ls -la /var/www/{project-name}/
```

Open each file and look for:
```python
app = Flask(__name__)           # Entry: app:app
application = Flask(__name__)   # Entry: wsgi:application
app = FastAPI()                 # Entry: main:app
```

### Method 2: Check your development command

What command do you use to run locally?

```bash
# Local dev
flask run              → app:app
python app.py          → app:app
uvicorn main:app --reload  → main:app
django-admin runserver         → django.wsgi is not used here
```

The entry point is usually the same for production.

### Method 3: Try common patterns

If unsure, try these in order:

1. `app:app` (most common)
2. `wsgi:application`
3. `main:app`
4. `{project_name}.wsgi:application` (Django)

Test one by one:
```bash
cd /var/www/{project-name}
source venv/bin/activate
gunicorn --bind 127.0.0.1:8000 app:app
# If this fails, try another entry point
```

---

## Setting the WSGI Entry Point

### Option 1: Environment Variable (Recommended)

Set before running deploy script:
```bash
export WSGI_ENTRY=your.module:application
python3 deploy-automation.py \
    --host YOUR_IP \
    --code ./myapp \
    --type python \
    --project myapp
```

### Option 2: Directly Edit systemd Service

After deployment, edit the service file:
```bash
sudo nano /etc/systemd/system/{project-name}.service
```

Change the ExecStart line:
```ini
ExecStart=/var/www/{project-name}/venv/bin/gunicorn \
  --workers 4 \
  --bind unix:/var/www/{project-name}/gunicorn.sock \
  your.module:application
```

Then reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart {project-name}
```

### Option 3: Use a Config File

Create `/var/www/{project-name}/gunicorn.conf.py`:
```python
bind = "unix:/var/www/{project-name}/gunicorn.sock"
workers = 4
wsgi_app = "your.module:application"
timeout = 120
```

Update systemd:
```ini
ExecStart=/var/www/{project-name}/venv/bin/gunicorn -c gunicorn.conf.py
```

---

## Troubleshooting

### Error: "No module named..."

**Problem:** Wrong module path

**Solution:** Check your project structure and adjust module name accordingly:
```bash
# If your file is app/app.py, the module is app.app
gunicorn app.app:application
```

### Error: "AttributeError: module 'app' has no attribute 'application'"

**Problem:** Variable name mismatch

**Solution:** Match the actual variable name in your code:
```python
# If you have `app = Flask(...)` use:
gunicorn app:app

# If you have `application = Flask(...)` use:
gunicorn app:application
```

### Error: "Address already in use"

**Problem:** Port conflict

**Solution:** Stop existing processes or change bind address:
```bash
# Check what's using port 8000
ss -tlnp | grep :8000

# Kill conflicting process or change bind
gunicorn --bind 127.0.0.1:8001 app:app
```

---

## Quick Reference Table

| Framework | Typical Entry | Customizable? | Notes |
|-----------|---------------|---------------|-------|
| Flask (standard) | `app:app` | Yes | Module:Variable |
| Flask (factory) | `wsgi:application` | Yes | Factory pattern |
| Django | `{project}.wsgi:application` | No | Standard location |
| FastAPI | `main:app` + UvicornWorker | Yes | Needs uvicorn workers |
| Bottle | `app:app` | Yes | Same pattern as Flask |
| Tornado | N/A | No | Use tornado.WEBHOOK |

---

## Environment Variable Examples

```bash
# Flask
export WSGI_ENTRY=app:app

# Django  
export WSGI_ENTRY=myproject.wsgi:application

# FastAPI
export WSGI_ENTRY=main:app

# Custom Flask
export WSGI_ENTRY=webapp.application:app

# With uvicorn for ASGI
export WSGI_ENTRY=main:app
export WORKER_CLASS=uvicorn.workers.UvicornWorker
```

Then in systemd service:
```ini
Environment="WSGI_ENTRY=$WSGI_ENTRY"
Environment="WORKER_CLASS=$WORKER_CLASS"
ExecStart=/path/to/gunicorn -c "$WORKER_CLASS" $WSGI_ENTRY
```

---

**Still stuck?** Run these diagnostic commands:

```bash
# List all Python files in project
find /var/www/{project-name} -name "*.py" | head -20

# Check for Flask/Django/FastAPI imports
grep -r "Flask\|Django\|FastAPI" /var/www/{project-name}/*.py 2>/dev/null | head -10
```

This will help identify your application framework and likely entry points.
