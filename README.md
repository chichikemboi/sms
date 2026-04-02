# Boenix Girls Senior School — SMS

A full School Management System built with Django + Supabase.

---

## Modules

| # | Module | Status |
|---|---|---|
| 1 | Auth & User Management | ✅ Done |
| 2 | Student Records | ✅ Done |
| 3 | Marks & Exam Analysis | 🔜 Next |
| 4 | Fee Management | 🔜 |
| 5 | Parent Letters (PDF) | 🔜 |
| 6 | Attendance | 🔜 |
| 7 | Staff Management | 🔜 |
| 8 | Resource Inventory | 🔜 |
| 9 | Timetable | 🔜 |
| 10 | Lesson Plans & Syllabus | 🔜 |

---

## Local Setup

### 1. Clone / download the project

```bash
cd boenix_sms
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Open .env and fill in your Supabase DB credentials and a SECRET_KEY
```

**Generating a SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Get Supabase credentials

1. Go to https://supabase.com → Create project
2. Go to **Settings → Database**
3. Copy **Host**, **Database name**, **User**, **Password**, **Port**
4. Paste into your `.env` file

### 6. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create the superuser (admin)

```bash
python manage.py createsuperuser
```
Then go to `/admin/` and set the user's **role** to `admin`.

### 8. Populate initial data (Streams & Classes)

```bash
python manage.py shell
```

```python
from students.models import Stream, ClassSection

# Create streams
f1 = Stream.objects.create(name='Form 1', label='Form One', order=1)
f2 = Stream.objects.create(name='Form 2', label='Form Two', order=2)
f3 = Stream.objects.create(name='Form 3', label='Form Three', order=3)
f4 = Stream.objects.create(name='Form 4', label='Form Four', order=4)

# Create sections (adjust to your actual streams)
for stream in [f1, f2, f3, f4]:
    ClassSection.objects.create(stream=stream, section='A')
    ClassSection.objects.create(stream=stream, section='B')

print("Done!")
exit()
```

### 9. Run the development server

```bash
python manage.py runserver
```

Open: http://127.0.0.1:8000

---

## Deploying to Render (free)

1. Push your project to a GitHub repository
2. Go to https://render.com → New Web Service
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn boenix_sms.wsgi:application`
5. Add all your `.env` variables under **Environment**
6. Deploy!

---

## User Roles

| Role | Code |
|---|---|
| Admin / Headteacher | `admin` |
| Class Teacher | `class_teacher` |
| Subject Teacher | `subject_teacher` |
| Parent (view only) | `parent` |
| Bursar / Accounts | `bursar` |
| Auditor | `auditor` |

Create users at `/accounts/users/` (admin only) or via Django admin.

---

## Tech Stack

- **Backend:** Django 4.2 (Python)
- **Database:** Supabase (PostgreSQL)
- **Hosting:** Render.com (free tier)
- **Frontend:** Bootstrap 5 + Bootstrap Icons
- **PDF Generation:** ReportLab (for parent letters & reports)
- **Static files:** WhiteNoise
