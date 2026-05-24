import aiohttp
from aiohttp import web
import subprocess
import json
import re

async def monitor_processes(request):
    try:
        data = await request.json()
        command_regex = data['command_regex']
        filter_flags = data.get('filter_flags', 'aux')

        # Validate filter_flags to prevent command injection
        valid_flags = {'aux', 'x', 'T'}
        flags = filter_flags.split()
        if not all(flag in valid_flags for flag in flags):
            return web.json_response({'code': 400, 'message': 'Invalid filter flags'}, status=400)

        # Run the ps command with the specified flags
        process = subprocess.Popen(['ps'] + flags, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return web.json_response({'code': 500, 'message': 'Error executing ps command'}, status=500)

        # Decode the output and filter processes
        output = stdout.decode('utf-8')
        lines = output.splitlines()
        matching_processes = []

        # Skip the header line
        for line in lines[1:]:
            if re.search(command_regex, line):
                parts = line.split()
                process_id = int(parts[1])  # Assuming the second column is the PID
                matching_processes.append({
                    'processId': process_id,
                    'processString': line
                })

        return web.json_response(matching_processes)

    except json.JSONDecodeError:
        return web.json_response({'code': 400, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return web.json_response({'code': 500, 'message': str(e)}, status=500)

app = web.Application()
app.router.add_post('/monitor/commands', monitor_processes)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)