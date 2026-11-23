import json

import pytest

from principale.configuration import ConfigurationError, data_directory, load_config, save_config


def test_configuration_is_created_in_private_user_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTANT_HOME", str(tmp_path / "constant"))
    config = load_config()

    assert config["schema_version"] == 1
    assert data_directory() == tmp_path / "constant"
    assert (data_directory() / "config.json").is_file()


def test_invalid_configuration_fails_explicitly(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTANT_HOME", str(tmp_path))
    (tmp_path / "config.json").write_text(json.dumps({"schema_version": 999}), encoding="utf-8")

    with pytest.raises(ConfigurationError, match="non prise en charge"):
        load_config()


def test_saving_configuration_does_not_store_plaintext_password(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTANT_HOME", str(tmp_path))
    config = load_config()
    config["security"]["password_hash"] = "example-hash"
    save_config(config)

    assert "example-hash" in (tmp_path / "config.json").read_text(encoding="utf-8")
