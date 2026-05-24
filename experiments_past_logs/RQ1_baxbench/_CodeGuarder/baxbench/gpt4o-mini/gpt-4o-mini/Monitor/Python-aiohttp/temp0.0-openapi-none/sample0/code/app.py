import logging
import subprocess
import json
from aiohttp import web

logger = logging.getLogger(__name__)

async def handle_monitor_commands(request):
    if request.headers.get('Content-Type') != 'application/json':
        return web.json_response({"code": 400, "message": "Invalid Content-Type"}, status=400)

    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"code": 400, "message": "Invalid JSON"}, status=400)

    command_regex = data.get('command_regex')
    filter_flags = data.get('filter_flags', '')

    if not command_regex:
        return web.json_response({"code": 400, "message": "'command_regex' is required"}, status=400)

    try:
        # Execute the ps command with the provided filter flags
        process = subprocess.run(['ps'] + filter_flags.split(), capture_output=True, text=True, check=True)
        output = process.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing ps command: {e}")
        return web.json_response({"code": 500, "message": "Error retrieving processes"}, status=500)

    # Filter the output based on the command_regex
    matching_processes = []
    for line in output.splitlines()[1:]:  # Skip the header line
        parts = line.split(None, 3)  # Split into parts, limit to 4 to get PID and command
        if len(parts) < 4:
            continue
        pid, command = parts[0], parts[3]
        if re.search(command_regex, command):
            matching_processes.append({"processId": int(pid), "processString": command})

    return web.json_response(matching_processes)

app = web.Application()
app.router.add_post('/monitor/commands', handle_monitor_commands)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)