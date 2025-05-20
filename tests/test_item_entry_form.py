import contextlib
import importlib.util
import io
import sys
import tempfile
import types
import unittest

from src.storage import WorkSystem


class Dummy:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def load_module():
    """Load textual_ui.py with stub textual modules."""
    modules = {
        "textual.app": types.ModuleType("textual.app"),
        "textual.binding": types.ModuleType("textual.binding"),
        "textual.containers": types.ModuleType("textual.containers"),
        "textual.css.query": types.ModuleType("textual.css.query"),
        "textual.screen": types.ModuleType("textual.screen"),
        "textual.widget": types.ModuleType("textual.widget"),
        "textual.widgets": types.ModuleType("textual.widgets"),
    }
    modules["textual.app"].App = Dummy
    modules["textual.app"].ComposeResult = list
    modules["textual.binding"].Binding = Dummy
    modules["textual.containers"].Container = Dummy
    modules["textual.containers"].Horizontal = Dummy
    modules["textual.containers"].Vertical = Dummy
    modules["textual.css.query"].NoMatches = Exception
    modules["textual.screen"].Screen = Dummy
    modules["textual.widget"].Widget = Dummy

    for cls in [
        "Button",
        "DataTable",
        "Header",
        "Input",
        "Label",
        "Select",
        "Static",
        "TabbedContent",
        "TabPane",
        "Tree",
        "Footer",
    ]:
        setattr(modules["textual.widgets"], cls, Dummy)

    original = {}
    for name, mod in modules.items():
        original[name] = sys.modules.get(name)
        sys.modules[name] = mod

    spec = importlib.util.spec_from_file_location("tui_test", "src/textual_ui.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)

    for name, mod in original.items():
        if mod is None:
            del sys.modules[name]
        else:
            sys.modules[name] = mod

    return module


class TestItemEntryForm(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.work_system = WorkSystem(self.temp_db.name)

    def tearDown(self):
        self.temp_db.close()

    def test_compose_has_no_prints(self):
        module = load_module()
        form = module.ItemEntryForm(self.work_system, lambda data: None)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            list(form.compose())
        self.assertEqual(buf.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
