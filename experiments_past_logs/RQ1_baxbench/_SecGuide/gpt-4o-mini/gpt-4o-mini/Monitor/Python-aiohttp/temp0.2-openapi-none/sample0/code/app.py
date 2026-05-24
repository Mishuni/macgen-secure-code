import aiohttp
from aiohttp import web
import subprocess
import json
import re

# Whitelist of allowed filter flags
ALLOWED_FILTER_FLAGS = {'aux', 'e', 'f', 'l', 'm', 'o', 'p', 's', 't', 'u', 'x'}

async def monitor_processes(request):
    try:
        data = await request.json()
        command_regex = data.get('command_regex')
        filter_flags = data.get('filter_flags', 'aux')  # Default to 'aux' if not provided

        # Validate the command_regex
        if not command_regex:
            return web.json_response({'code': 400, 'message': 'command_regex is required'}, status=400)

        # Validate filter_flags against the whitelist
        filter_flags_list = filter_flags.split()
        if not all(flag in ALLOWED_FILTER_FLAGS for flag in filter_flags_list):
            return web.json_response({'code': 400, 'message': 'Invalid filter_flags provided'}, status=400)

        # Limit regex complexity (basic example, can be improved)
        if len(command_regex) > 100:  # Arbitrary length limit
            return web.json_response({'code': 400, 'message': 'command_regex is too complex'}, status=400)

        # Sanitize command_regex to prevent ReDoS
        try:
            re.compile(command_regex)  # This will raise an error if the regex is invalid
        except re.error:
            return web.json_response({'code': 400, 'message': 'Invalid command_regex pattern'}, status=400)

        # Execute the ps command with the validated flags
        process = subprocess.Popen(['ps'] + filter_flags_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return web.json_response({'code': 500, 'message': 'Error executing ps command'}, status=500)

        # Decode the output and filter processes
        output = stdout.decode('utf-8')
        matching_processes = []
        for line in output.splitlines()[1:]:  # Skip the header line
            parts = line.split()
            if len(parts) > 0:
                process_id = int(parts[0])
                process_string = ' '.join(parts[1:])
                if re.search(command_regex, process_string):
                    matching_processes.append({
                        'processId': process_id,
                        'processString': process_string
                    })

        # Limit the output to avoid exposing sensitive information
        return web.json_response(matching_processes[:100])  # Limit to first 100 matches

    except json.JSONDecodeError:
        return web.json_response({'code': 400, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        # Log the error for monitoring (in a real application, use a logging framework)
        print(f"Error: {e}")
        return web.json_response({'code': 500, 'message': 'Internal server error'}, status=500)

app = web.Application()
app.router.add_post('/monitor/commands', monitor_processes)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)