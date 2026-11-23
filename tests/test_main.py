from contextlib import nullcontext

from principale import main
from principale.auth import set_local_password
from principale.configuration import default_config, save_config


def test_login_success_clears_connection_screen_before_menu(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTANT_HOME", str(tmp_path / "constant"))
    config = default_config()
    set_local_password(config, "mot-de-passe-test")
    save_config(config)

    pages = []
    monkeypatch.setattr(main.interface, "begin_page", lambda title=None, **_kwargs: pages.append(title))
    monkeypatch.setattr(main.auth, "login", lambda _config: True)
    monkeypatch.setattr(main.interface, "show_dashboard", lambda **_kwargs: None)
    monkeypatch.setattr(main.interface, "show_menu", lambda: None)
    monkeypatch.setattr(main.interface, "prompt_choice", lambda: 0)
    monkeypatch.setattr(main.interface, "message", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main.interface, "full_screen", nullcontext)
    monkeypatch.setattr(main, "_online", lambda: False)

    assert main.run([]) == 0
    assert pages == ["Connexion", None, "Session terminée"]
