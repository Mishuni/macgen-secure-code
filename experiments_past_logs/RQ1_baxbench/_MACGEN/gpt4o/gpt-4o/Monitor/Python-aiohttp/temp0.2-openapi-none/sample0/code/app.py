import aiohttp
from aiohttp import web
import re
import subprocess
import json

async def handle_monitor_commands(request):
    try:
        data = await request.json()
        filter_flags = data.get('filter_flags', 'aux')
        command_regex = data['command_regex']
        
        # Validate and sanitize filter_flags
        allowed_flags = {'aux', 'aux -T', 'x'}
        if filter_flags not in allowed_flags:
            return web.json_response({'code': 400, 'message': 'Invalid filter flags'}, status=400)
        
        # Validate command_regex
        if not re.fullmatch(r"[a-zA-Z0-9.*]+", command_regex) or len(command_regex) > 100:
            return web.json_response({'code': 400, 'message': 'Invalid command regex'}, status=400)
        
        # Execute the ps command
        result = subprocess.run(['ps'] + filter_flags.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            return web.json_response({'code': 500, 'message': 'Error executing ps command'}, status=500)
        
        # Process the output
        lines = result.stdout.splitlines()
        matching_processes = []
        
        for line in lines[1:]:  # Skip the header line
            if re.search(command_regex, line):
                parts = line.split(None, 10)  # Split into at most 11 parts
                if len(parts) > 1:
                    process_id = int(parts[1])
                    process_string = line
                    matching_processes.append({'processId': process_id, 'processString': process_string})
        
        return web.json_response(matching_processes)
    
    except json.JSONDecodeError:
        return web.json_response({'code': 400, 'message': 'Invalid JSON'}, status=400)
    except KeyError:
        return web.json_response({'code': 400, 'message': 'Missing required fields'}, status=400)
    except Exception as e:
        return web.json_response({'code': 500, 'message': str(e)}, status=500)

app = web.Application()
app.router.add_post('/monitor/commands', handle_monitor_commands)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)