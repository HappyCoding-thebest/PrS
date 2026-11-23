import pytest

from principale.liens import (
    LinkError,
    add_link,
    demo_links,
    import_links,
    normalize_instagram_url,
    read_links,
)


def test_normalizes_valid_publication_and_profile_urls():
    assert normalize_instagram_url("instagram.com/p/AbC_12?x=1", "publication") == (
        "https://www.instagram.com/p/AbC_12/"
    )
    assert normalize_instagram_url("https://instagram.com/mon.profil", "profil") == (
        "https://www.instagram.com/mon.profil/"
    )


@pytest.mark.parametrize(
    ("url", "kind"),
    [
        ("https://instagram.com.evil.example/p/ABC", "publication"),
        ("http://instagram.com/p/ABC", "publication"),
        ("https://instagram.com/p/ABC", "profil"),
        ("https://instagram.com/accounts/login", "profil"),
    ],
)
def test_rejects_invalid_instagram_urls(url, kind):
    with pytest.raises(LinkError):
        normalize_instagram_url(url, kind)


def test_add_link_deduplicates_and_stores_outside_repository(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTANT_HOME", str(tmp_path / "private"))
    assert add_link("publication", "instagram.com/p/ABC") is True
    assert add_link("publication", "https://www.instagram.com/p/ABC/") is False
    assert read_links("publication") == ["https://www.instagram.com/p/ABC/"]


def test_demo_links_use_reserved_invalid_domain():
    assert all(".example.invalid/" in url for url in demo_links("publication"))


def test_import_counts_duplicates_as_rejected_lines(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTANT_HOME", str(tmp_path / "private"))
    source = tmp_path / "links.txt"
    source.write_text(
        "https://instagram.com/p/ABC/\n"
        "https://instagram.com/p/ABC/\n"
        "https://example.com/p/NOPE/\n",
        encoding="utf-8",
    )

    assert import_links("publication", source) == (1, 2)
