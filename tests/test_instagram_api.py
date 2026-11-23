import pytest

from principale.instagram_api import OfficialOAuthUnavailable, connect_official_account, official_api_status


def test_official_oauth_is_reported_as_unavailable_instead_of_faked():
    assert "non configurée" in official_api_status()
    with pytest.raises(OfficialOAuthUnavailable, match="application Meta"):
        connect_official_account()
