import aiohttp
from aiohttp import web
import subprocess
import json
import re

async def monitor_commands(request):
    try:
        data = await request.json()
        command_regex = data['command_regex']
        filter_flags = data.get('filter_flags', 'aux')

        # Sanitize filter_flags input
        if not re.match(r'^(aux|-T|[ ]*)$', filter_flags):
            raise web.HTTPBadRequest(reason="Invalid filter flags")

        # Limit regular expression complexity
        if len(command_regex) > 100 or re.search(r'\(\?{1,}', command_regex):
            raise web.HTTPBadRequest(reason="Regex too complex or too long")

        # Execute the ps command
        process = subprocess.Popen(['ps'] + filter_flags.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return web.json_response({'code': 500, 'message': 'Error executing ps command'}, status=500)

        # Decode the output and filter based on the regex
        output = stdout.decode('utf-8')
        lines = output.splitlines()[1:]  # Skip the header line
        matching_processes = []

        for line in lines:
            parts = line.split()
            if len(parts) > 0:
                process_id = int(parts[0])
                process_string = ' '.join(parts[1:])
                if re.search(command_regex, process_string):
                    matching_processes.append({
                        'processId': process_id,
                        'processString': process_string
                    })

        return web.json_response(matching_processes)

    except json.JSONDecodeError:
        return web.json_response({'code': 400, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return web.json_response({'code': 500, 'message': str(e)}, status=500)

app = web.Application()
app.router.add_post('/monitor/commands', monitor_commands)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)