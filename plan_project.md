# 📋 QR Device Management System — Project Plan

> A Django-based system for managing physical devices via QR codes, with role-based
> access control, Cloudinary image storage, a Supabase (PostgreSQL) database, and a
> dashboard. The UI must strictly follow `frontend_guidelines.md` (the design system).

**Legend:** `- [ ]` = todo · `- [x]` = done

**Stack:** Django 6.0 · PostgreSQL (Supabase) · Cloudinary · `qrcode` + `Pillow` · `django-environ`

---

## ✅ Phase 1 — Setup & Configuration

- [x] Create and activate a Python virtual environment (`venv`)
- [x] Install core dependencies (`django`, `psycopg2-binary`, `django-environ`, `cloudinary`, `django-cloudinary-storage`, `qrcode`, `Pillow`)
- [x] Generate `requirements.txt`
- [x] Initialize Django project (`config`) and core app (`devices`)
- [x] Create `.env` and `.env.example` files
- [x] Create `.gitignore` (exclude `venv/`, `.env`, `db.sqlite3`, media, etc.)
- [x] Configure `settings.py` to read secrets via `django-environ`
- [x] Configure Supabase PostgreSQL connection (with `sslmode=require`)
- [x] Configure Cloudinary storage (`STORAGES` + `CLOUDINARY_STORAGE`)
- [x] Register `devices`, `cloudinary`, `cloudinary_storage` in `INSTALLED_APPS`
- [x] Verify DB connectivity (`python manage.py check` / `migrate`)
- [x] Run initial `migrate` to create Django's built-in tables on Supabase
- [x] Initialize git repository and make first commit
- [x] Create custom `User` model (`accounts.User`, RBAC role field) **before** first migrate

---

## 🔐 Phase 2 — Authentication & User Management

- [x] Create an `accounts` (or `users`) app for auth concerns
- [x] Decide on a custom `User` model (extend `AbstractUser`) — *done before first migrate*
- [x] **Login** page + view (session-based auth, styled per design system)
- [x] ~~**Register** (public)~~ → replaced by **Admin User Management** (decision: admin-managed users only)
- [x] **Logout** flow (POST, Django 6 requirement)
- [x] **Forgot Password** (email reset token flow via Gmail SMTP)
- [x] **Change Password** (authenticated user)
- [x] **Role-Based Access Control (RBAC)**
  - [x] Define roles: `Admin`, `Manager`, `Technician`, `Viewer`
  - [x] Permission decorators / mixins (`RoleRequiredMixin`, `AdminRequiredMixin`, `role_required`)
  - [x] Restrict views/actions by role (User Management = Admin only)
- [x] **User Management (Admin)**: list (search + pagination), create, edit, delete (self-delete guarded)
- [x] Profile page (view/edit own info + avatar to Cloudinary)
- [x] Configure `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`
- [x] Email backend configuration for password reset (Gmail SMTP via `.env`)
- [x] Base layout + design-system CSS (`templates/base.html`, `static/css/base.css`)
- [x] Seed admin account (`admin` / `Admin@123456`, role=admin)

---

## ✅ Phase 3 — Database Models

- [x] **Role** — handled via `User.role` choices field (admin/manager/technician/viewer) for early-stage RBAC
- [x] **User** model (custom; role, phone, avatar)
- [x] **Category** model (device category: name, description)
- [x] **Location** model (building / room / department hierarchy)
- [x] **Device** model
  - [x] `uuid` (UUIDField, unique, indexed — used in QR codes)
  - [x] name, serial number, model, manufacturer
  - [x] FK → Category, FK → Location
  - [x] status (`active`, `maintenance`, `broken/disposed`)
  - [x] purchase date, warranty expiry, assigned user
  - [x] image (Cloudinary), qr_code image (Cloudinary)
  - [x] created_at / updated_at timestamps
- [x] **MaintenanceLog** model (FK → Device, FK → User, action, notes, cost, date)
- [x] Register all models in Django admin
- [x] Create & run migrations (applied to Supabase)
- [x] Seed sample data via `seed_data` management command (categories, locations, users, devices, maintenance logs)

---

## ✅ Phase 4 — Core CRUD & Cloudinary Integration

- [x] Device **list** view (table, pagination, search, filters by status/category/location)
- [x] Device **detail** view
- [x] Device **create** (form with image upload → Cloudinary)
- [x] Device **edit/update**
- [x] Device **delete** (with confirmation modal)
- [x] Category CRUD
- [x] Location CRUD
- [x] MaintenanceLog CRUD (add log to a device)
- [x] Cloudinary upload validation (file type, size)
- [x] Forms styled per design system (inputs, labels, buttons)
- [x] Apply RBAC to all CRUD actions

---

## ✅ Phase 5 — QR Code System

- [x] Auto-generate a QR code on device creation (encodes device detail URL / `uuid`)
- [x] Store generated QR image in Cloudinary
- [x] Endpoint to view / download a device's QR code
- [x] Printable QR label view (name + QR for physical attachment)
- [ ] Bulk QR generation / export (optional — chưa làm)
- [x] **Frontend Camera Scanner**
  - [x] Integrate a JS QR scanner library (`html5-qrcode`)
  - [x] Scanner page following design system (1:1 frame, dashed Primary Blue border)
  - [x] On scan success: green border feedback, then fetch device info
  - [x] API endpoint to resolve `uuid` → device detail (JSON)
  - [x] Handle invalid / unknown QR gracefully

---

## ✅ Phase 6 — Frontend Development (per `frontend_guidelines.md`)

- [x] Base template (`base.html`) with Sidebar (260px) + Header (64px) + Main Content layout
- [x] Load font; set up CSS variables for the color palette
- [x] Implement design tokens (colors, spacing multiples of 4/8, radii)
- [x] Sidebar navigation component (Surface/Card bg, active link = Primary Blue)
- [x] Header component (search box + user avatar)
- [x] Button styles: Small (32px) / Medium (40px) / Large (48px), radius 6px
- [x] Table component (wrapper radius 8px + shadow; `<th>` `#F1F5F9`; `<td>` hover `#F8FAFC`)
- [x] Form/input styles (40px height, focus ring `rgba(37,99,235,0.2)`)
- [x] Card component (radius 12px, padding 24px, shadow)
- [x] Modal / confirm pages styled per design system
- [x] Status badges (Success Green / Warning Yellow / Danger Red)
- [x] 403 / access-denied page styled
- [x] Configure static files pipeline (`STATICFILES_DIRS`)

---

## ✅ Phase 7 — Dashboard & Statistics

- [x] Dashboard page (landing after login)
- [x] Summary counters (total devices, active, in maintenance, broken)
- [x] Devices-by-category breakdown
- [x] Devices-by-location breakdown
- [x] Status distribution chart (Chart.js)
- [x] Recent maintenance activity feed
- [x] Recently added devices list
- [x] Cards styled per design system

---

## 🚀 Phase 8 — Polish & Deployment (Optional / Future)

- [ ] Unit tests for models, views, and RBAC
- [ ] Input validation & error handling pass
- [ ] Production settings (`DEBUG=False`, secure cookies, `ALLOWED_HOSTS`)
- [ ] `collectstatic` + static hosting (WhiteNoise or CDN)
- [ ] Deployment (Railway / Render / Fly.io / VPS)
- [ ] README with setup instructions
- [ ] Rotate the committed development secrets before going live
