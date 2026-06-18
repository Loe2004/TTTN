"""Seed the database with realistic sample data for development/demo.

Usage:
    python manage.py seed_data            # create sample data (idempotent)
    python manage.py seed_data --flush    # delete existing seed data first
    python manage.py seed_data --qr       # also generate QR codes (uploads to Cloudinary, slower)
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from devices.models import Category, Device, Location, MaintenanceLog
from devices.utils import assign_qr_code

User = get_user_model()


CATEGORIES = [
    ("Laptop", "Máy tính xách tay phục vụ công việc văn phòng."),
    ("Desktop", "Máy tính để bàn."),
    ("Máy in", "Máy in laser và phun mực."),
    ("Router / Switch", "Thiết bị mạng."),
    ("Máy chiếu", "Thiết bị trình chiếu phòng họp."),
    ("Camera", "Camera giám sát an ninh."),
    ("Màn hình", "Màn hình rời cho máy tính."),
]

LOCATIONS = [
    ("Văn phòng Tầng 1", "Tòa A", "P.101"),
    ("Văn phòng Tầng 2", "Tòa A", "P.201"),
    ("Phòng họp lớn", "Tòa A", "P.301"),
    ("Phòng Server", "Tòa B", "P.B05"),
    ("Kho thiết bị", "Tòa B", "Kho 1"),
    ("Lễ tân", "Tòa A", "Sảnh"),
]

MANUFACTURERS = ["Dell", "HP", "Lenovo", "Asus", "Acer", "Cisco", "Canon", "Epson", "Samsung", "LG"]

DEVICE_NAMES = {
    "Laptop": ["Dell Latitude 5420", "HP EliteBook 840", "Lenovo ThinkPad X1", "Asus ExpertBook B9"],
    "Desktop": ["Dell OptiPlex 7090", "HP ProDesk 600", "Lenovo ThinkCentre M70"],
    "Máy in": ["Canon LBP6230", "HP LaserJet Pro M404", "Epson L3250"],
    "Router / Switch": ["Cisco Catalyst 2960", "TP-Link TL-SG1024", "Aruba 2530"],
    "Máy chiếu": ["Epson EB-X06", "BenQ MW550", "Sony VPL-EX430"],
    "Camera": ["Hikvision DS-2CD2143", "Dahua IPC-HFW2431", "Ezviz C3W"],
    "Màn hình": ["Dell P2419H", "LG 24MK600", "Samsung S24R350"],
}

MAINTENANCE_ACTIONS = [
    "Vệ sinh, bảo dưỡng định kỳ",
    "Thay thế linh kiện hỏng",
    "Cập nhật firmware/phần mềm",
    "Sửa lỗi kết nối mạng",
    "Thay mực / drum máy in",
    "Kiểm tra và thay pin",
]

SAMPLE_USERS = [
    ("manager01", "manager", "Trần", "Quản Lý"),
    ("tech01", "technician", "Lê", "Kỹ Thuật"),
    ("tech02", "technician", "Phạm", "Sửa Chữa"),
    ("viewer01", "viewer", "Nguyễn", "Xem"),
]


class Command(BaseCommand):
    help = "Seed the database with sample data for the QR Device Management System."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing devices, categories, locations, maintenance logs and seed users first.",
        )
        parser.add_argument(
            "--qr",
            action="store_true",
            help="Also generate QR codes for each device (uploads to Cloudinary, slower).",
        )
        parser.add_argument(
            "--devices",
            type=int,
            default=25,
            help="Number of devices to create (default: 25).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        flush = options["flush"]
        gen_qr = options["qr"]
        num_devices = options["devices"]

        if flush:
            self.stdout.write(self.style.WARNING("Đang xóa dữ liệu mẫu cũ..."))
            MaintenanceLog.objects.all().delete()
            Device.objects.all().delete()
            Category.objects.all().delete()
            Location.objects.all().delete()
            User.objects.filter(
                username__in=[u[0] for u in SAMPLE_USERS]
            ).delete()

        # --- Users -----------------------------------------------------------
        self.stdout.write("Tạo người dùng mẫu...")
        users = []
        for username, role, first, last in SAMPLE_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "first_name": first,
                    "last_name": last,
                    "role": role,
                },
            )
            if created:
                user.set_password("Password@123")
                user.save()
            users.append(user)

        # --- Categories ------------------------------------------------------
        self.stdout.write("Tạo danh mục...")
        categories = {}
        for name, desc in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                name=name, defaults={"description": desc}
            )
            categories[name] = cat

        # --- Locations -------------------------------------------------------
        self.stdout.write("Tạo vị trí...")
        locations = []
        for name, building, room in LOCATIONS:
            loc, _ = Location.objects.get_or_create(
                name=name,
                building=building,
                room=room,
            )
            locations.append(loc)

        # --- Devices ---------------------------------------------------------
        self.stdout.write(f"Tạo {num_devices} thiết bị...")
        statuses = [s[0] for s in Device.Status.choices]
        today = timezone.now().date()
        devices = []
        for i in range(num_devices):
            cat_name = random.choice(list(DEVICE_NAMES.keys()))
            category = categories[cat_name]
            base_name = random.choice(DEVICE_NAMES[cat_name])
            device = Device.objects.create(
                name=f"{base_name} #{i + 1:03d}",
                serial_number=f"SN-{random.randint(100000, 999999)}",
                model=base_name,
                manufacturer=random.choice(MANUFACTURERS),
                category=category,
                location=random.choice(locations),
                assigned_to=random.choice(users + [None, None]),
                status=random.choices(statuses, weights=[70, 20, 10])[0],
                purchase_date=today - timedelta(days=random.randint(30, 1200)),
                warranty_expiry=today + timedelta(days=random.randint(-200, 700)),
                notes=random.choice(
                    ["", "", "Thiết bị quan trọng.", "Cần theo dõi bảo hành."]
                ),
            )
            if gen_qr:
                try:
                    assign_qr_code(device)
                except Exception as exc:  # noqa: BLE001 - seeding shouldn't hard-fail
                    self.stderr.write(
                        self.style.WARNING(
                            f"  ! Bỏ qua QR cho {device.name}: {exc}"
                        )
                    )
            devices.append(device)

        # --- Maintenance logs ------------------------------------------------
        self.stdout.write("Tạo nhật ký bảo trì...")
        log_count = 0
        for device in devices:
            for _ in range(random.randint(0, 3)):
                MaintenanceLog.objects.create(
                    device=device,
                    performed_by=random.choice(users),
                    action=random.choice(MAINTENANCE_ACTIONS),
                    notes=random.choice(["", "Hoàn tất.", "Theo dõi thêm."]),
                    cost=Decimal(random.randint(0, 50)) * Decimal("100000"),
                    performed_at=timezone.now()
                    - timedelta(days=random.randint(1, 365)),
                )
                log_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "\n✅ Hoàn tất! Đã tạo: "
                f"{len(categories)} danh mục, {len(locations)} vị trí, "
                f"{len(users)} người dùng mẫu, {len(devices)} thiết bị, "
                f"{log_count} nhật ký bảo trì."
            )
        )
        self.stdout.write(
            "   Người dùng mẫu mật khẩu: Password@123 "
            f"({', '.join(u[0] for u in SAMPLE_USERS)})"
        )
        if not gen_qr:
            self.stdout.write(
                self.style.NOTICE(
                    "   (Chạy lại với --qr để sinh QR code cho thiết bị.)"
                )
            )
