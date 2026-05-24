import aiohttp
from aiohttp import web
import subprocess
import re
import json

async def monitor_processes(request):
    try:
        # Parse the JSON request body
        data = await request.json()
        command_regex = data.get('command_regex')
        filter_flags = data.get('filter_flags', '')

        # Validate the command_regex input
        if not isinstance(command_regex, str) or not command_regex:
            return web.json_response({'code': 400, 'message': 'Invalid command_regex'}, status=400)

        # Construct the command securely
        command = ['ps'] + filter_flags.split() + ['-eo', 'pid,comm']
        
        # Execute the command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        output = result.stdout.decode()

        # Filter the output based on the command_regex
        process_list = []
        for line in output.splitlines()[1:]:  # Skip the header line
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            pid, process_string = parts
            if re.search(command_regex, process_string):
                process_list.append({'processId': int(pid), 'processString': process_string})

        return web.json_response(process_list)

    except subprocess.CalledProcessError as e:
        return web.json_response({'code': 500, 'message': 'Error executing command'}, status=500)
    except json.JSONDecodeError:
        return web.json_response({'code': 400, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return web.json_response({'code': 500, 'message': str(e)}, status=500)

app = web.Application()
app.router.add_post('/monitor/commands', monitor_processes)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)