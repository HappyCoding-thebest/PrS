import json

from principale.journal import read_entries, record


def test_journal_strips_url_parameters_and_records_no_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTANT_HOME", str(tmp_path))
    record(
        account="compte_local",
        operation="ouverture",
        url="https://www.instagram.com/p/ABC/?token=secret#fragment",
        status="ouvert",
        message="test",
    )

    entries = read_entries()
    assert entries[0]["url"] == "https://www.instagram.com/p/ABC/"
    assert "secret" not in json.dumps(entries)
