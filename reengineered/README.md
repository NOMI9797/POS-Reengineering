# Reengineered POS (Django)

## Setup

Requires **Python 3.12 or 3.13**. Django 5.2 LTS does not support newer Python versions yet.

```bash
cd reengineered
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py test              # run all tests
python manage.py runserver
```

## Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | dev-only key | Secret key (set in any shared or deployed environment) |
| `DJANGO_DEBUG` | `1` | `0` to turn debug off |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated host names |
| `POS_DB_ENGINE` | `django.db.backends.sqlite3` | e.g. `django.db.backends.postgresql` |
| `POS_DB_NAME`, `POS_DB_USER`, `POS_DB_PASSWORD`, `POS_DB_HOST`, `POS_DB_PORT` | SQLite file `db.sqlite3` | Database connection |

## Architecture (target)

```
Presentation   Django views + templates (MVT)          ← Member C
Business       <app>/services.py, domain models, core/ ← Members A, C
Data access    <app>/repositories.py over Django ORM   ← Member B
Database       SQLite (dev/test) / PostgreSQL           ← Member B
```

| App | Responsibility | Legacy origin |
|---|---|---|
| `core` | Shared value objects (`Money`) | `util/Util.java`, `double` money fields |
| `members` | Members and loyalty points | `customer/member/*` |
| `inventory` | Categories, products, stock | `category/*`, `product/*` |

Apps still to be added: `discounts`, `sales` (checkout), `accounts` (storekeeper login), `vendors`.
