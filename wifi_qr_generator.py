"""Generate the payload (and optionally a PNG) for a WiFi QR code.

The payload follows the widely used ZXing WiFi format::

    WIFI:T:WPA;S:<ssid>;P:<password>;H:false;;

Scanners read that string and offer to join the network. The special
characters ``\\ ; , " :`` inside a field must be backslash escaped, which
is the part hand written payloads most often get wrong.

Only the payload builder is required. Rendering a PNG uses the optional
``qrcode`` package; without it the CLI prints the payload so it can be
pasted into any QR generator.
"""

from __future__ import annotations

import argparse
import sys

# Characters that must be escaped inside a WIFI: field value.
SPECIAL_CHARS = '\\;,":'

SECURITY_TYPES = ("WPA", "WEP", "NOPASS")
# The payload spells the open network type in lower case: T:nopass.
_CANONICAL = {"NOPASS": "nopass"}


def escape_wifi_value(value: str) -> str:
    """Return *value* with ZXing special characters backslash escaped."""
    return "".join(f"\\{char}" if char in SPECIAL_CHARS else char for char in value)


def build_wifi_payload(
    ssid: str,
    password: str = "",
    security: str = "WPA",
    hidden: bool = False,
) -> str:
    """Build a validated ``WIFI:`` payload string.

    Raises:
        ValueError: if the SSID is empty or longer than 32 octets, the
            security type is unknown, or a password is supplied for an
            open network (or missing for a secured one).
    """
    if not ssid or not ssid.strip():
        raise ValueError("SSID must not be empty")
    if len(ssid.encode("utf-8")) > 32:
        raise ValueError("SSID must be at most 32 octets")
    security = _CANONICAL.get(security.upper(), security.upper())
    if security.upper() not in SECURITY_TYPES:
        raise ValueError(
            f"security must be one of WPA, WEP, nopass, got {security!r}"
        )
    if security == "nopass" and password:
        raise ValueError("an open (nopass) network must not have a password")
    if security != "nopass" and not password:
        raise ValueError(f"a {security} network requires a password")

    fields = [f"T:{security}", f"S:{escape_wifi_value(ssid)}"]
    if security != "nopass":
        fields.append(f"P:{escape_wifi_value(password)}")
    fields.append(f"H:{'true' if hidden else 'false'}")
    return "WIFI:" + ";".join(fields) + ";;"


def save_qr_png(payload: str, output_path: str) -> None:
    """Render *payload* as a QR PNG. Requires the optional ``qrcode`` package."""
    try:
        import qrcode
    except ImportError as exc:  # pragma: no cover, depends on environment
        raise RuntimeError(
            "saving a PNG needs the optional 'qrcode' package: pip install qrcode"
        ) from exc
    qrcode.make(payload).save(output_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a WiFi QR code payload.")
    parser.add_argument("ssid", help="network name")
    parser.add_argument("password", nargs="?", default="", help="network password")
    parser.add_argument(
        "--security",
        default="WPA",
        type=lambda value: "nopass" if value.upper() == "NOPASS" else value.upper(),
        choices=("WPA", "WEP", "nopass"),
        help="default: WPA",
    )
    parser.add_argument("--hidden", action="store_true", help="network is hidden")
    parser.add_argument("--output", help="also save a QR PNG to this path")
    args = parser.parse_args(argv)

    try:
        payload = build_wifi_payload(
            args.ssid, args.password, args.security, args.hidden
        )
        if args.output:
            save_qr_png(payload, args.output)
            print(f"Saved QR code to {args.output}")
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
