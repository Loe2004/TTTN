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

## 🗄️ Phase 3 — Database Models

- [ ] **Role** model (name, description, permission flags)
- [ ] **User** model (custom; linked to Role; phone, avatar)
- [ ] **Category** model (device category: name, description)
- [ ] **Location** model (building / room / department hierarchy)
- [ ] **Device** model
  - [ ] `uuid` (UUIDField, unique, indexed — used in QR codes)
  - [ ] name, serial number, model, manufacturer
  - [ ] FK → Category, FK → Location
  - [ ] status (`active`, `maintenance`, `broken/disposed`)
  - [ ] purchase date, warranty expiry, assigned user
  - [ ] image (Cloudinary), qr_code image (Cloudinary)
  - [ ] created_at / updated_at timestamps
- [ ] **MaintenanceLog** model (FK → Device, FK → User, action, notes, cost, date)
- [ ] Register all models in Django admin
- [ ] Create & run migrations
- [ ] Seed initial data (roles, sample categories/locations) via fixture or management command

---

## 🛠️ Phase 4 — Core CRUD & Cloudinary Integration

- [ ] Device **list** view (table, pagination, search, filters by status/category/location)
- [ ] Device **detail** view
- [ ] Device **create** (form with image upload → Cloudinary)
- [ ] Device **edit/update**
- [ ] Device **delete** (with confirmation modal)
- [ ] Category CRUD
- [ ] Location CRUD
- [ ] MaintenanceLog CRUD (add log to a device)
- [ ] Cloudinary upload validation (file type, size)
- [ ] Forms styled per design system (inputs, labels, buttons)
- [ ] Apply RBAC to all CRUD actions

---

## 📷 Phase 5 — QR Code System

- [ ] Auto-generate a QR code on device creation (encodes device `uuid` or detail URL)
- [ ] Store generated QR image in Cloudinary
- [ ] Endpoint to view / download a device's QR code
- [ ] Printable QR label view (name + QR for physical attachment)
- [ ] Bulk QR generation / export (optional)
- [ ] **Frontend Camera Scanner**
  - [ ] Integrate a JS QR scanner library (e.g. `html5-qrcode`)
  - [ ] Scanner page following design system (1:1 frame, dashed Primary Blue border)
  - [ ] On scan success: green border feedback for 1s, then fetch device info
  - [ ] API endpoint to resolve `uuid` → device detail (JSON)
  - [ ] Handle invalid / unknown QR gracefully

---

## 🎨 Phase 6 — Frontend Development (per `frontend_guidelines.md`)

- [ ] Base template (`base.html`) with Sidebar (260px) + Header (64px) + Main Content layout
- [ ] Load Inter / Roboto font; set up CSS variables for the color palette
- [ ] Implement design tokens (colors, spacing multiples of 4/8, radii)
- [ ] Sidebar navigation component (Surface/Card bg, active link = Primary Blue)
- [ ] Header component (search box + user avatar)
- [ ] Button styles: Small (32px) / Medium (40px) / Large (48px), radius 6px
- [ ] Table component (wrapper radius 8px + shadow; `<th>` 48px `#F1F5F9`; `<td>` 56px hover `#F8FAFC`)
- [ ] Form/input styles (40px height, focus ring `rgba(37,99,235,0.2)`)
- [ ] Card component (radius 12px, padding 24px, shadow)
- [ ] Modal component (overlay `rgba(0,0,0,0.5)`, max-width 500/800px, radius 12px)
- [ ] Status badges (Success Green / Warning Yellow / Danger Red)
- [ ] Responsive behavior check
- [ ] Configure static files pipeline (`STATICFILES_DIRS`, `collectstatic`)

---

## 📊 Phase 7 — Dashboard & Statistics

- [ ] Dashboard page (landing after login)
- [ ] Summary counters (total devices, active, in maintenance, broken)
- [ ] Devices-by-category breakdown
- [ ] Devices-by-location breakdown
- [ ] Status distribution chart (e.g. Chart.js pie/bar)
- [ ] Recent maintenance activity feed
- [ ] Recently added devices list
- [ ] Cards styled per design system

---

## 🚀 Phase 8 — Polish & Deployment (Optional / Future)

- [ ] Unit tests for models, views, and RBAC
- [ ] Input validation & error handling pass
- [ ] Production settings (`DEBUG=False`, secure cookies, `ALLOWED_HOSTS`)
- [ ] `collectstatic` + static hosting (WhiteNoise or CDN)
- [ ] Deployment (Railway / Render / Fly.io / VPS)
- [ ] README with setup instructions
- [ ] Rotate the committed development secrets before going live
