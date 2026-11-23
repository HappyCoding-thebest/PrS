from principale.interface import MENU_OPTIONS


def test_menu_contains_all_requested_numbered_actions():
    assert [number for number, _label in MENU_OPTIONS] == list(range(1, 15))
