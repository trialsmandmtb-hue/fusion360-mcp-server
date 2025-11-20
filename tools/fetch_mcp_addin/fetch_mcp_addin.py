import adsk.core, adsk.fusion, traceback, urllib.request, urllib.error, json

# Configuration
SERVER_URL = 'http://127.0.0.1:8001/call_tool'
DEFAULT_TOOL_NAME = 'CreateSketch'
# Provide a safe default parameters dictionary so CreateSketch always has a 'plane' key.
# This avoids triggering server-side KeyError when the server expects 'plane' in parameters.
DEFAULT_PARAMS = {"plane": "xy"}
AUTO_EXECUTE = False


def _post_call(tool_name=DEFAULT_TOOL_NAME, params=None, timeout=10):
    try:
        payload = json.dumps({"tool_name": tool_name, "parameters": params or {}}).encode('utf-8')
        req = urllib.request.Request(SERVER_URL, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode('utf-8')
            return json.loads(raw)
        except urllib.error.HTTPError as he:
            # Attempt to read error body (FastAPI returns JSON with detail)
            try:
                body = he.read().decode('utf-8')
            except Exception:
                body = f'HTTP Error: {he.code} {he.reason}'
            ui = adsk.core.Application.get().userInterface
            ui.messageBox(f'HTTP error from MCP server:\n{body}', 'Fetch MCP Add-In')
            return None
    except Exception:
        ui = adsk.core.Application.get().userInterface
        ui.messageBox('Failed to contact MCP server:\n{}'.format(traceback.format_exc()), 'Fetch MCP Add-In')
        return None


def _confirm_and_run_script(script_text):
    ui = adsk.core.Application.get().userInterface
    try:
        if AUTO_EXECUTE:
            should_run = True
        else:
            preview = script_text
            if len(preview) > 4000:
                preview = preview[:4000] + '\n\n... (truncated)'
            msg = 'Script received:\n\n' + preview + '\n\nExecute this script now?'
            result = ui.messageBox(msg, 'MCP Script Preview', adsk.core.MessageBoxButtonTypes.YesNoMessageBoxType)
            should_run = (result == adsk.core.DialogResults.DialogYes)

        if should_run:
            loc = {}
            try:
                exec(script_text, loc)
                run_func = loc.get('run')
                if callable(run_func):
                    run_func(None)
                    ui.messageBox('Script executed successfully', 'Fetch MCP Add-In')
                else:
                    ui.messageBox('No callable run(context) found in script', 'Fetch MCP Add-In')
            except Exception:
                ui.messageBox('Error while executing script:\n{}'.format(traceback.format_exc()), 'Fetch MCP Add-In')
        else:
            ui.messageBox('Script execution cancelled by user.', 'Fetch MCP Add-In')
    except Exception:
        print('Confirm/run error:\n{}'.format(traceback.format_exc()))


def run(context):
    ui = adsk.core.Application.get().userInterface
    try:
        ui.messageBox('Fetch MCP Add-In: fetching script from {}...'.format(SERVER_URL), 'Fetch MCP Add-In')
        resp = _post_call(DEFAULT_TOOL_NAME, DEFAULT_PARAMS)
        if resp and isinstance(resp, dict):
            script = resp.get('script')
            if script:
                _confirm_and_run_script(script)
            else:
                ui.messageBox('No script field in response', 'Fetch MCP Add-In')
        else:
            ui.messageBox('No valid response from server', 'Fetch MCP Add-In')
    except Exception:
        ui.messageBox('Runtime error:\n{}'.format(traceback.format_exc()), 'Fetch MCP Add-In')


def stop(context):
    pass
