"""Streamlit headless smoke test of the default clean reading workspace."""
from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_default_workspace_runs_without_streamlit_exception():
    app = AppTest.from_file(str(Path(__file__).with_name("app.py")), default_timeout=30).run()
    assert not app.exception, [str(item.message) for item in app.exception]
    assert any("Simulation methods" in str(item.value) for item in app.title)
    assert len(app.tabs) == 2
    assert len(app.dataframe) >= 1
    assert any("GROMACS" in str(widget.value) for widget in app.dataframe)
