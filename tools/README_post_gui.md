Post-to-MCP GUI
================

Small GUI for pasting design JSON and POSTing it to a running MCP server.

Files
- `post_to_mcp_gui.py` — Tkinter GUI app.

Quick run
- From the repo (recommended using the repo venv):
  - `./.venv/Scripts/python.exe tools/post_to_mcp_gui.py`
- Or double-click `post_to_mcp_gui.py` if your system runs .py with Python.

Usage
1. Set the server URL (default `http://127.0.0.1:8000`).
2. Choose endpoint `/call_tool` (single) or `/call_tools` (list).
3. Provide `tool_name` (default `CreateSketch`).
4. Paste parameters JSON into the Parameters box, or use the "Paste JSON params from clipboard" button.
5. Click `Send`.
6. If the response contains a `script` field, use `Save Last Script...` to save it as a `.py` file.

Notes
- The GUI uses only Python standard library modules so it should run in the repo venv without extra installs.
- If you want a true background app (no console) on Windows, run with the venv's `pythonw.exe` or create a shortcut that calls `pythonw`.

Security
- The GUI posts to whichever URL you put; ensure you only point it at trusted local servers.

Want an .exe?
- I can package this into a standalone Windows executable using `pyinstaller` if you want a double-clickable binary.
