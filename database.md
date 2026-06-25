# Mô tả Cơ sở dữ liệu (Database Schema)

Dưới đây là tài liệu mô tả chi tiết các bảng (tables) và các cột (columns) trong cơ sở dữ liệu của project. 

Dựa trên cấu trúc SQL bạn cung cấp, có thể thấy cơ sở dữ liệu này bao gồm 2 phần:
1. Các bảng được thiết kế thủ công ban đầu (Sử dụng UUID làm khóa chính).
2. Các bảng được sinh ra bởi **Django ORM** (Có tiền tố app name như `devices_`, `accounts_`, sử dụng BigInt/Integer tự động tăng làm khóa chính).

---

## 1. Các bảng Quản lý Thiết bị (Thiết kế chung ban đầu)

### Bảng `categories` (Danh mục thiết bị)
Dùng để phân loại thiết bị.
- `id` (uuid): Khóa chính, tự động tạo chuỗi định danh.
- `name` (varchar): Tên danh mục thiết bị.
- `description` (text): Đoạn mô tả chi tiết về danh mục.
- `created_at` (timestamp): Thời gian danh mục được tạo.

### Bảng `locations` (Vị trí)
Lưu trữ thông tin các vị trí phòng ban/tòa nhà đặt thiết bị.
- `id` (uuid): Khóa chính.
- `name` (varchar): Tên vị trí (VD: Phòng IT, Tầng 3).
- `description` (text): Mô tả chi tiết vị trí.
- `created_at` (timestamp): Thời gian tạo dữ liệu.

### Bảng `devices` (Thiết bị)
Lưu trữ thông tin chi tiết về từng thiết bị cụ thể.
- `id` (uuid): Khóa chính.
- `name` (varchar): Tên của thiết bị.
- `serial_number` (varchar): Số Sê-ri của thiết bị (duy nhất).
- `category_id` (uuid): Khóa ngoại liên kết tới bảng `categories`.
- `location_id` (uuid): Khóa ngoại liên kết tới bảng `locations`.
- `image_url` (varchar): Đường dẫn lưu ảnh của thiết bị.
- `qr_code_url` (varchar): Đường dẫn lưu ảnh mã QR để quét.
- `status` (device_status): Trạng thái hiện tại của thiết bị (Mặc định 'HOAT_DONG').
- `purchase_date` (date): Ngày mua thiết bị.
- `last_maintenance_date` (date): Ngày thực hiện bảo trì lần cuối.
- `next_maintenance_date` (date): Lịch bảo trì tiếp theo.
- `notes` (text): Các ghi chú bổ sung.
- `created_at`, `updated_at` (timestamp): Thời gian tạo và lần cập nhật cuối.
- `assigned_to_user_id` (uuid): Người được giao sử dụng thiết bị (Khóa ngoại tới `users`).
- `created_by`, `updated_by` (uuid): Người tạo và người cập nhật bản ghi (Khóa ngoại tới `users`).

### Bảng `maintenance_logs` (Nhật ký bảo trì)
Lịch sử các lần bảo trì, sửa chữa thiết bị.
- `id` (uuid): Khóa chính.
- `device_id` (uuid): Khóa ngoại liên kết tới bảng `devices`.
- `maintenance_date` (date): Ngày thực hiện bảo trì.
- `description` (text): Chi tiết nội dung công việc bảo trì.
- `cost` (numeric): Chi phí bảo trì/sửa chữa.
- `performed_by` (varchar): Tên người hoặc đơn vị thực hiện bảo trì.
- `created_at` (timestamp): Thời gian ghi log.

---

## 2. Các bảng Phân quyền và Người dùng (Thiết kế ban đầu)

### Bảng `users` (Người dùng)
- `id` (uuid): Khóa chính.
- `username` (varchar): Tên đăng nhập (Duy nhất).
- `password_hash` (varchar): Chuỗi mã hóa của mật khẩu.
- `email` (varchar): Địa chỉ email (Duy nhất).
- `full_name` (varchar): Họ và tên đầy đủ.
- `phone_number` (varchar): Số điện thoại liên hệ.
- `is_active` (boolean): Đánh dấu tài khoản có đang hoạt động hay không.
- `last_login` (timestamp): Thời gian lần đăng nhập gần nhất.
- `created_at`, `updated_at` (timestamp): Thời gian tạo và cập nhật.

### Bảng `roles` (Vai trò) và `permissions` (Quyền hạn)
- **`roles`**: Lưu các vai trò trong hệ thống (VD: Admin, Staff). Gồm các cột: `id`, `name` (Duy nhất), `description`, `created_at`.
- **`permissions`**: Lưu danh sách các quyền cụ thể. Gồm: `id`, `code` (Mã quyền duy nhất), `name`, `description`, `created_at`.

### Bảng Trung gian (Mapping)
- **`user_roles`**: Bảng nối n-n giữa Người dùng và Vai trò. Gồm `user_id` và `role_id`.
- **`role_permissions`**: Bảng nối n-n giữa Vai trò và Quyền hạn. Gồm `role_id` và `permission_id`.

### Bảng `audit_logs` (Nhật ký Hệ thống/Kiểm toán)
Ghi nhận mọi thao tác thay đổi dữ liệu của người dùng.
- `id` (uuid): Khóa chính.
- `user_id` (uuid): Người thực hiện hành động.
- `action` (varchar): Tên hành động (VD: CREATE, UPDATE, DELETE).
- `table_name` (varchar): Tên bảng bị thay đổi.
- `record_id` (uuid): ID của bản ghi bị thay đổi.
- `old_values`, `new_values` (jsonb): Dữ liệu cũ và dữ liệu mới lưu dưới định dạng JSON.
- `ip_address` (varchar): Địa chỉ IP của người dùng.
- `created_at` (timestamp): Thời gian thực hiện hành động.

---

## 3. Các Bảng sinh ra từ Django Models (Hệ thống chạy thực tế)

Hệ thống có sử dụng framework Django, do đó đã sinh ra các bảng theo chuẩn ORM của Django, được chia theo các "app".

### Ứng dụng thiết bị (App `devices`)

#### Bảng `devices_category`
- `id` (bigint): Khóa chính, tự động tăng.
- `created_at`, `updated_at` (timestamp): Thời gian tạo/cập nhật.
- `name` (varchar): Tên danh mục (duy nhất).
- `description` (text): Mô tả.
- `is_active` (boolean): Cho phép ẩn/hiện danh mục.

#### Bảng `devices_location`
- `id` (bigint): Khóa chính, tự động tăng.
- `created_at`, `updated_at` (timestamp): Thời gian tạo/cập nhật.
- `name`, `building`, `room` (varchar): Tên vị trí, Tòa nhà, Phòng.
- `description` (text): Mô tả vị trí.
- `is_active` (boolean): Cho phép ẩn/hiện vị trí.

#### Bảng `devices_device`
Đây là bảng chính chứa thiết bị được quản lý qua Django.
- `id` (bigint): Khóa chính.
- `uuid` (uuid): Mã định danh (Duy nhất).
- `name` (varchar): Tên thiết bị.
- `serial_number`, `model`, `manufacturer` (varchar): Số Sê-ri, Đời máy, Hãng sản xuất.
- `status` (varchar): Trạng thái thiết bị.
- `purchase_date`, `warranty_expiry` (date): Ngày mua, Ngày hết hạn bảo hành.
- `image`, `qr_code` (varchar): Đường dẫn lưu hình ảnh và mã QR.
- `notes` (text): Ghi chú.
- `assigned_to_id` (bigint): Người dùng được cấp (Khóa ngoại tới `accounts_user`).
- `category_id`, `location_id` (bigint): Thuộc Danh mục và Vị trí nào.
- `is_active` (boolean): Ẩn/Hiện thiết bị.
- `created_at`, `updated_at` (timestamp).

#### Bảng `devices_maintenancelog`
- `id` (bigint): Khóa chính.
- `action` (varchar): Hành động bảo trì.
- `notes` (text): Ghi chú bảo trì.
- `cost` (numeric): Chi phí thực hiện.
- `performed_at` (timestamp): Thời điểm thực hiện bảo trì.
- `device_id` (bigint): Liên kết tới thiết bị.
- `performed_by_id` (bigint): Liên kết tới người dùng thực hiện.
- `created_at`, `updated_at` (timestamp).

### Ứng dụng Tài khoản (App `accounts`)

#### Bảng `accounts_user`
Định nghĩa Custom User của Django.
- `id` (bigint): Khóa chính.
- `password` (varchar): Mật khẩu băm.
- `last_login`, `date_joined` (timestamp): Đăng nhập cuối, Ngày tham gia.
- `username` (varchar): Tên đăng nhập (Duy nhất).
- `email`, `phone` (varchar): Email, Số điện thoại.
- `first_name`, `last_name` (varchar): Tên, Họ.
- `role` (varchar): Vai trò người dùng (Ví dụ: Admin, User, ...).
- `avatar` (varchar): Đường dẫn ảnh đại diện.
- `is_superuser`, `is_staff`, `is_active` (boolean): Các cờ phân quyền của Django.
- `created_at`, `updated_at` (timestamp).

- **Các bảng phụ trợ**: `accounts_user_groups` (Nối User-Group) và `accounts_user_user_permissions` (Nối User-Quyền hạn độc lập).

### Các Bảng Mặc định của Django (System tables)
- **`django_migrations`**: Lưu lịch sử chạy lệnh migrate database của Django.
- **`django_content_type`**: Lưu danh sách tất cả các Models có trong hệ thống (dùng cho phân quyền, log).
- **`auth_group`**, **`auth_permission`**, **`auth_group_permissions`**: Hệ thống Phân quyền (Nhóm và Quyền) mặc định của Django.
- **`django_admin_log`**: Lưu lại lịch sử Thêm/Sửa/Xóa thao tác thông qua trang quản trị (Admin Panel) của Django.
- **`django_session`**: Lưu session key và dữ liệu người dùng đang đăng nhập trên trình duyệt.
