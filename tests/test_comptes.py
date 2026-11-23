import pytest

from principale.comptes import AccountError, add_account, choose_account, remove_account
from principale.configuration import default_config


def test_accounts_reject_duplicates_and_enforce_limit():
    config = default_config()
    add_account(config, "@Compte.un")
    with pytest.raises(AccountError, match="déjà enregistré"):
        add_account(config, "compte.UN")
    for index in range(2, 11):
        add_account(config, f"compte_{index}")
    with pytest.raises(AccountError, match="limite"):
        add_account(config, "compte_11")


def test_selection_and_removal_keep_active_account_valid():
    config = default_config()
    add_account(config, "premier")
    add_account(config, "second")
    choose_account(config, "second")

    remove_account(config, "second")

    assert config["active_account"] == "premier"
