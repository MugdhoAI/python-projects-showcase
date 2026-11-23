import pytest

from wifi_qr_generator import build_wifi_payload, escape_wifi_value, main


def test_wpa_payload():
    assert (
        build_wifi_payload("HomeNet", "secret123")
        == "WIFI:T:WPA;S:HomeNet;P:secret123;H:false;;"
    )


def test_open_network_has_no_password_field():
    assert (
        build_wifi_payload("Cafe", security="nopass")
        == "WIFI:T:nopass;S:Cafe;H:false;;"
    )


def test_hidden_network_flag():
    assert ";H:true;;" in build_wifi_payload("Net", "pw", hidden=True)


def test_special_characters_are_escaped():
    assert escape_wifi_value('a;b,c"d:e\\f') == 'a\\;b\\,c\\"d\\:e\\\\f'
    payload = build_wifi_payload("My;Net", "p:ss")
    assert "S:My\\;Net" in payload
    assert "P:p\\:ss" in payload


def test_empty_ssid_rejected():
    with pytest.raises(ValueError):
        build_wifi_payload("  ", "pw")


def test_ssid_length_limit():
    assert build_wifi_payload("a" * 32, "pw").startswith("WIFI:T:WPA;S:")
    with pytest.raises(ValueError):
        build_wifi_payload("a" * 33, "pw")


def test_unknown_security_rejected():
    with pytest.raises(ValueError):
        build_wifi_payload("Net", "pw", security="WPA3")


def test_password_rules():
    with pytest.raises(ValueError):
        build_wifi_payload("Net", security="WPA")
    with pytest.raises(ValueError):
        build_wifi_payload("Net", "pw", security="nopass")


def test_security_is_case_insensitive():
    assert build_wifi_payload("Net", "pw", security="wpa").startswith("WIFI:T:WPA;")


def test_cli_prints_payload(capsys):
    assert main(["HomeNet", "secret123"]) == 0
    assert "WIFI:T:WPA;S:HomeNet;P:secret123;H:false;;" in capsys.readouterr().out


def test_cli_reports_bad_input(capsys):
    assert main(["", "pw"]) == 2
    assert "error:" in capsys.readouterr().err
