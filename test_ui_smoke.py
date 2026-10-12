"""Headless UI smoke test: exercises the default synthetic-example reading workflow."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_default_workspace_runs_without_streamlit_exception():
    app_file=Path(__file__).with_name("app.py")
    app=AppTest.from_file(str(app_file), default_timeout=25).run()
    assert not app.exception, [str(item.message) for item in app.exception]
    assert any("Read the methods" in str(title.value) for title in app.title)
    assert len(app.tabs)==3
