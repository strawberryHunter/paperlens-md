"""Smoke test the default one-document reading workspace in Streamlit."""
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_default_workspace_runs_without_streamlit_exception():
    app_file = Path(__file__).with_name("app.py")
    app = AppTest.from_file(str(app_file), default_timeout=30).run()
    assert not app.exception, [str(item.message) for item in app.exception]
    assert any("Simulation methods" in str(title.value) for title in app.title)
    assert len(app.tabs) == 2
    assert any("GROMACS" in str(button.label) for button in app.button)
