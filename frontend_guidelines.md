Hệ thống Thiết kế UI/UX - QR Device Manager

Tài liệu này quy định các tiêu chuẩn về màu sắc, bố cục và kích thước của các thành phần giao diện (UI Components) cho hệ thống quản lý thiết bị bằng mã QR.
1. Bảng màu (Color Palette)

Hệ thống sử dụng tone màu chủ đạo là Tech Blue kết hợp nền sáng, mang lại cảm giác chuyên nghiệp, tập trung vào dữ liệu.
Tên	Mã Hex	Mục đích sử dụng
Primary Blue	#2563EB	Nút bấm chính, màu chủ đạo của hệ thống, link, icon active.
Primary Hover	#1D4ED8	Trạng thái hover của nút bấm chính.
Success Green	#10B981	Thông báo thành công, trạng thái thiết bị "Hoạt động".
Warning Yellow	#F59E0B	Trạng thái thiết bị "Đang bảo trì", cảnh báo nhẹ.
Danger Red	#EF4444	Nút xóa, lỗi, trạng thái thiết bị "Hỏng/Thanh lý".
Background	#F8FAFC	Màu nền của toàn bộ trang web (không dùng trắng tinh).
Surface/Card	#FFFFFF	Nền của các thẻ (Card), bảng (Table), sidebar.
Text Dark	#0F172A	Tiêu đề chính (H1, H2), text cần nhấn mạnh.
Text Muted	#64748B	Text phụ, mô tả, placeholder trong ô input.
Border Line	#E2E8F0	Đường viền của bảng, thẻ card, ô input.
2. Typography (Kiểu chữ)

Sử dụng Font chữ Inter hoặc Roboto (Sans-serif) để đảm bảo độ nét trên mọi màn hình.

    H1 (Tiêu đề trang): Size 24px | Font-weight: 700 (Bold) | Màu: Text Dark

    H2 (Tiêu đề Card/Section): Size 18px | Font-weight: 600 (Semi-bold) | Màu: Text Dark

    Body Text (Chữ thông thường): Size 14px | Font-weight: 400 (Regular) | Màu: Text Dark

    Small Text (Ghi chú, timestamp): Size 12px | Font-weight: 400 | Màu: Text Muted

3. Hệ thống Bố cục (Layout & Spacing)

Sử dụng hệ thống lưới (Grid) 12 cột. Layout chuẩn cho trang quản trị bao gồm Sidebar và Main Content.

    Sidebar (Thanh điều hướng trái): Chiều rộng cố định 260px. Nền màu Surface/Card.

    Header (Thanh trên cùng): Chiều cao cố định 64px. Chứa khung tìm kiếm và avatar user.

    Main Content (Vùng nội dung): Chiều rộng linh hoạt (calc(100vw - 260px)).

    Spacing (Khoảng cách chuẩn): Sử dụng bội số của 4 hoặc 8 (ví dụ: 4px, 8px, 16px, 24px, 32px).

        Padding chuẩn của một trang: 24px.

        Khoảng cách giữa các phần tử liên quan: 16px.

4. Kích thước & Quy chuẩn Components (Thành phần UI)
4.1. Buttons (Nút bấm)

Quy định bo góc (Border-radius): 6px (hoặc 0.375rem). Trọng lượng chữ luôn là 500 (Medium). Không có viền đen.
Loại Nút	Kích thước (Padding)	Chiều cao	Kích thước chữ	Áp dụng cho
Nhỏ (Small)	6px 12px	32px	12px	Các thao tác trong bảng (Sửa/Xóa).
Vừa (Medium)	8px 16px	40px	14px	Kích thước nút mặc định (Lưu, Thêm mới).
Lớn (Large)	12px 24px	48px	16px	Nút Đăng nhập, Nút Quét QR chính.
4.2. Tables (Bảng dữ liệu)

Bảng là thành phần quan trọng nhất của hệ thống quản lý.

    Bọc ngoài (Wrapper): Nền #FFFFFF, có border màu Border Line, border-radius 8px, thêm shadow mờ box-shadow: 0 1px 3px rgba(0,0,0,0.1).

    Header bảng (thẻ <th>): * Chiều cao: 48px.

        Nền xám nhạt (#F1F5F9).

        Chữ in hoa, size 12px, font-weight 600, màu Text Muted.

        Căn lề (Padding): 12px 16px.

    Dòng dữ liệu (thẻ <td>):

        Chiều cao tối thiểu: 56px.

        Căn lề (Padding): 16px.

        Hiệu ứng Hover: Nền đổi sang màu xám cực nhạt (#F8FAFC) khi trỏ chuột vào dòng.

        Border dưới của mỗi dòng: 1px solid #E2E8F0.

4.3. Inputs & Forms (Ô nhập liệu)

    Chiều cao chuẩn: 40px (bằng với nút Medium).

    Border: 1px solid #CBD5E1. Border-radius: 6px.

    Padding trong ô: 8px 12px.

    Trạng thái Focus: Đổi viền sang màu Primary Blue và thêm hiệu ứng viền sáng (ring): box-shadow: 0 0 0 2px rgba(37,99,235,0.2).

    Label (Nhãn): Nằm trên ô input, size 14px, font-weight 500, màu Text Dark, khoảng cách từ nhãn xuống ô input là 8px.

4.4. Cards & Modals (Thẻ và Hộp thoại)

    Card (Thẻ chứa số liệu thống kê):

        Nền #FFFFFF, border-radius 12px.

        Border: 1px solid #E2E8F0.

        Padding: 24px.

        Shadow: box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1).

    Modal (Hộp thoại popup):

        Background overlay (lớp phủ đen ngoài hộp thoại): Đen trong suốt rgba(0,0,0,0.5).

        Nội dung hộp thoại: Căn giữa màn hình, chiều rộng tối đa 500px (đối với form nhỏ) hoặc 800px (đối với form lớn/chi tiết). Border-radius 12px.

4.5. QR Scanner / Viewer (Khu vực quét QR)

    Khung hiển thị camera quét QR cần có tỷ lệ 1:1 (Vuông) hoặc 4:3.

    Bao quanh khung camera là một border đứt khúc (dashed) màu Primary Blue.

    Khi quét thành công, viền chuyển sang màu Success Green trong 1 giây để phản hồi thị giác.
