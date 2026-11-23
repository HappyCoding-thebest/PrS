from principale.auth import demo_license_status, password_is_configured, set_local_password, verify_local_password
from principale.configuration import default_config


def test_local_password_is_hashed_and_verified():
    config = default_config()
    set_local_password(config, "un-secret-local")

    assert password_is_configured(config)
    assert verify_local_password(config, "un-secret-local")
    assert not verify_local_password(config, "mauvais-secret")
    assert "un-secret-local" not in str(config)


def test_demo_license_is_local_not_server_validated():
    config = default_config()
    assert demo_license_status(config)["valid"] is False
    set_local_password(config, "un-secret-local")
    status = demo_license_status(config)
    assert status["valid"] is True
    assert status["mode"] == "démo locale"
    assert "pas une licence commerciale" in status["notice"]
