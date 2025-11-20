#!/usr/bin/env python3
"""
Simple Tkinter GUI to POST design JSON to the local MCP server.
- Default server: http://127.0.0.1:8000
- Endpoint options: /call_tool (single tool) or /call_tools (multiple)

Usage:
- Run with the repo's venv Python (recommended):
    .venv/Scripts/python.exe tools/post_to_mcp_gui.py
- Or double-click the script if .py files are associated with Python.

The app shows response JSON and lets you save returned `script` field to a file.
"""

import json
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

DEFAULT_SERVER = "http://127.0.0.1:8000"
DEFAULT_TOOL = "CreateSketch"


def post_json(url, body_dict):
    data = json.dumps(body_dict).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_text = resp.read().decode("utf-8")
            return True, resp_text
    except urllib.error.HTTPError as e:
        try:
            err = e.read().decode("utf-8")
        except Exception:
            err = str(e)
        return False, f"HTTP {e.code}: {err}"
    except Exception as e:
        return False, str(e)


class MCPPosterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Post design JSON to MCP server")
        self.geometry("900x700")
        self.create_widgets()
        self.last_response = None

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Server row
        srv_frame = ttk.Frame(frm)
        srv_frame.pack(fill=tk.X)
        ttk.Label(srv_frame, text="Server URL:").pack(side=tk.LEFT)
        self.server_var = tk.StringVar(value=DEFAULT_SERVER)
        ttk.Entry(srv_frame, textvariable=self.server_var, width=40).pack(side=tk.LEFT, padx=6)

        ttk.Label(srv_frame, text="Endpoint:").pack(side=tk.LEFT, padx=(10, 0))
        self.endpoint_var = tk.StringVar(value="/call_tool")
        ttk.OptionMenu(srv_frame, self.endpoint_var, "/call_tool", "/call_tool", "/call_tools").pack(side=tk.LEFT)

        # Tool name and parameters
        tool_frame = ttk.Frame(frm)
        tool_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(tool_frame, text="Tool name:").pack(side=tk.LEFT)
        self.tool_var = tk.StringVar(value=DEFAULT_TOOL)
        ttk.Entry(tool_frame, textvariable=self.tool_var, width=30).pack(side=tk.LEFT, padx=6)

        ttk.Button(tool_frame, text="Paste JSON params from clipboard", command=self.paste_from_clipboard).pack(side=tk.LEFT, padx=8)

        # Parameters label + text
        ttk.Label(frm, text="Parameters (JSON):").pack(anchor=tk.W, pady=(10, 0))
        self.params_text = tk.Text(frm, height=12, wrap=tk.NONE)
        self.params_text.pack(fill=tk.BOTH, expand=False)
        self.params_text.insert("1.0", "{}")

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill=tk.X, pady=8)
        ttk.Button(btn_frame, text="Send", command=self.on_send).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Clear Params", command=lambda: self.params_text.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Save Last Script...", command=self.save_last_script).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)

        # Response label + text
        ttk.Label(frm, text="Response / Logs:").pack(anchor=tk.W, pady=(6, 0))
        self.resp_text = tk.Text(frm, height=16, wrap=tk.NONE)
        self.resp_text.pack(fill=tk.BOTH, expand=True)

    def paste_from_clipboard(self):
        try:
            clip = self.clipboard_get()
        except Exception:
            messagebox.showinfo("Clipboard", "No text in clipboard")
            return
        self.params_text.delete("1.0", tk.END)
        self.params_text.insert("1.0", clip)

    def on_send(self):
        server = self.server_var.get().strip().rstrip('/')
        endpoint = self.endpoint_var.get().strip()
        url = server + endpoint
        tool_name = self.tool_var.get().strip()
        params_raw = self.params_text.get("1.0", tk.END).strip()
        try:
            params = json.loads(params_raw) if params_raw else {}
        except Exception as e:
            messagebox.showerror("JSON error", f"Parameters are not valid JSON:\n{e}")
            return

        body = None
        if endpoint == "/call_tool":
            body = {"tool_name": tool_name, "parameters": params}
        else:
            # call_tools expects a list of tool calls
            body = [{"tool_name": tool_name, "parameters": params}]

        self.append_log(f"POST {url} with body:\n{json.dumps(body, indent=2)}\n")
        ok, resp = post_json(url, body)
        if ok:
            self.append_log("Response:\n" + resp + "\n")
            try:
                self.last_response = json.loads(resp)
            except Exception:
                self.last_response = None
        else:
            self.append_log("Error:\n" + resp + "\n")
            self.last_response = None

    def append_log(self, text):
        self.resp_text.insert(tk.END, text)
        self.resp_text.see(tk.END)

    def save_last_script(self):
        if not self.last_response:
            messagebox.showinfo("No response", "No previous successful response to save.")
            return
        script = None
        if isinstance(self.last_response, dict) and "script" in self.last_response:
            script = self.last_response["script"]
        elif isinstance(self.last_response, list) and len(self.last_response) > 0 and isinstance(self.last_response[0], dict) and "script" in self.last_response[0]:
            script = self.last_response[0]["script"]
        if not script:
            messagebox.showinfo("No script", "Response does not contain a 'script' field.")
            return
        f = filedialog.asksaveasfilename(defaultextension='.py', filetypes=[('Python files', '*.py'), ('All files', '*.*')], initialfile='generated_script.py')
        if not f:
            return
        try:
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write(script)
            messagebox.showinfo("Saved", f"Script saved to {f}")
        except Exception as e:
            messagebox.showerror("Save error", str(e))


if __name__ == '__main__':
    app = MCPPosterApp()
    app.mainloop()
