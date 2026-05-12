import streamlit.web.cli as stcli
import os
import sys

def resolve_path(path):
    """Get the absolute path to the resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, path)

if __name__ == "__main__":
    # We need to point Streamlit to the actual app.py file
    # and pass the arguments as if we ran 'streamlit run app.py'
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("app.py"),
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())
