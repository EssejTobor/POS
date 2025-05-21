import sys
import types

from main import main, parse_args


def _make_stub_cli(called):
    cli = types.ModuleType("src.cli")

    def fake_main():
        called.append("cli")

    cli.main = fake_main
    return cli


def _make_stub_tui(called):
    app_mod = types.ModuleType("src.pos_tui.app")

    def fake_main():
        called.append("tui")

    app_mod.main = fake_main
    pos_tui = types.ModuleType("src.pos_tui")
    pos_tui.app = app_mod
    return pos_tui, app_mod


# parse_args tests


def test_parse_args_cli():
    args = parse_args(["--cli"])
    assert args.cli is True


def test_parse_args_default():
    args = parse_args([])
    assert args.cli is False


# main function tests


def test_main_cli_invokes_cli(monkeypatch):
    called = []
    stub_cli = _make_stub_cli(called)
    stub_src = types.ModuleType("src")
    stub_src.cli = stub_cli
    monkeypatch.setitem(sys.modules, "src", stub_src)
    monkeypatch.setitem(sys.modules, "src.cli", stub_cli)

    main(["--cli"])

    assert called == ["cli"]


def test_main_uses_tui_when_available(monkeypatch):
    called = []
    stub_cli = _make_stub_cli(called)
    stub_pos_tui, stub_app = _make_stub_tui(called)
    stub_src = types.ModuleType("src")
    stub_src.cli = stub_cli
    stub_src.pos_tui = stub_pos_tui
    monkeypatch.setitem(sys.modules, "src", stub_src)
    monkeypatch.setitem(sys.modules, "src.cli", stub_cli)
    monkeypatch.setitem(sys.modules, "src.pos_tui", stub_pos_tui)
    monkeypatch.setitem(sys.modules, "src.pos_tui.app", stub_app)

    main([])

    assert called == ["tui"]


def test_main_falls_back_to_cli_on_import_error(monkeypatch):
    called = []
    stub_cli = _make_stub_cli(called)
    stub_src = types.ModuleType("src")
    stub_src.cli = stub_cli
    # Do not provide pos_tui to trigger ImportError
    monkeypatch.setitem(sys.modules, "src", stub_src)
    monkeypatch.setitem(sys.modules, "src.cli", stub_cli)

    main([])

    assert called == ["cli"]
