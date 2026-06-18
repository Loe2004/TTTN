"""Utility helpers for the devices app (QR code generation)."""

from io import BytesIO

import qrcode
from django.core.files.base import ContentFile


def build_qr_payload(device, request=None) -> str:
    """Return the string encoded in a device's QR code.

    Encodes an absolute URL to the device detail page. We append the UUID
    as a query parameter so our internal scanner can identify the device
    while keeping the QR code as a valid link for external scanners.
    """
    path = device.get_absolute_url()
    payload = f"{path}?u={device.uuid}"
    if request is not None:
        return request.build_absolute_uri(payload)
    return payload


def generate_qr_file(payload: str, filename: str) -> ContentFile:
    """Generate a PNG QR code for ``payload`` and return it as a ContentFile."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=filename)


def assign_qr_code(device, request=None, save: bool = True) -> None:
    """Generate and attach a QR code image to ``device`` (uploaded to Cloudinary)."""
    payload = build_qr_payload(device, request=request)
    qr_file = generate_qr_file(payload, filename=f"device_{device.uuid}.png")
    device.qr_code.save(qr_file.name, qr_file, save=save)
